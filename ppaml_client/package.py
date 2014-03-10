# package.py -- package a set of data           -*- coding: us-ascii -*-
# Copyright (C) 2014  Galois, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#   3. Neither Galois's name nor the names of other contributors may be used to
#      endorse or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY GALOIS AND OTHER CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL GALOIS OR OTHER CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Package a set of data.

A package is basically a userspace file system--a mechanism for
organizing files dumped into a directory.  It has an extremely simple
interface--one can create packages and record key-value pairs.

This module provides both a package abstract base class and a concrete
implementation using JSON as its key-value store.

"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

from abc import ABCMeta, abstractmethod
import collections
import errno
from types import NoneType
import itertools
import json
import os
import shutil

import lockfile


class Package(collections.MutableMapping):
    """ABC for PPAML packages."""

    @abstractmethod
    def close(self):
        """Close the package, saving it on disk."""
        pass

    @abstractmethod
    def __enter__(self):
        return self

    @abstractmethod
    def __exit__(self, exception_type, exception, traceback):
        self.close()
        return False            # don't suppress exception


class JSONPackage(collections.MutableMapping):
    """A PPAML package indexed with a JSON object.

    This class implements a system somewhat like an object store.  It
    has a flat namespace and supports storing two types of
    string-indexed data: files and everything else.  To insert new
    files, use the record_file function; to insert anything else, use
    the record_data function.

    All instances of this class are mutable mappings, so you can
    generally treat them like dictionaries.  Inserting new data with
    bracket notation inserts data--that is,

        my_package['blah'] = 'blah'

    evaluates to

        my_package.record_data('blah', 'blah')

    """

    # It is entirely conceivable that multiple programs might try to
    # edit the same package at the same time.  One obvious case is that
    # where the package is stored on a network file system, but one can
    # easily imagine a user forgetting that he or she is running a job
    # and starting a new one which tries to write to the same package.
    # However, JSONPackage does /not/ support simultaneous editing--when
    # it is instantiated, the instance loads the package state from disk
    # into memory, and when it is closed, the instance writes the
    # package state back to disk.
    #
    # To protect the validity of the package on disk, JSONPackage
    # employs a coarse-grained locking strategy.  The protocol ensures
    # the following invariants:
    #   - If a package is valid, it will never become invalid.
    #   - If a package is valid, writes to that package will never be
    #     lost.
    # The protocol is implemented as a disk-based lock on the package
    # index file, stored in the instance variable self._lock.

    __CURRENT_FORMAT_VERSION = 3

    def __init__(self, path):
        """Create or open a package located at the given path."""
        self._path = path
        self._lock = lockfile.LockFile(self._index_path)

        # At this point, we know nothing about the state of the package.
        # We don't even know if it exists!  There are a whole bunch of
        # possible states:
        #    path does not exist         -> raise IOError
        #    path exists and is
        #        not a directory         -> raise IOError
        #        an empty directory      -> create and lock package
        #        not a package           -> raise InvalidPackageError
        #        an unlocked package     -> lock package
        #        a locked package        -> raise lockfile.AlreadyLocked
        try:
            self._lock.acquire(timeout=-1)
        except lockfile.LockFailed:
            if os.path.exists(self.path):
                # The path exists, but it's not a directory.
                assert not os.path.isdir(self.path)
                err = IOError(errno.ENOTDIR, os.strerror(errno.ENOTDIR))
            else:
                # The path does not exist.
                err = IOError(errno.ENOENT, os.strerror(errno.ENOENT))
            err.filename = self.path
            raise err
        except lockfile.AlreadyLocked:
            # Who knows if this is a package or not?  It's already
            # locked, so give up.
            raise
        else:
            # We managed to lock the package.
            dir_entries = set(os.listdir(self.path))
            lock_entries = set(os.path.basename(path)
                               for path in (self._lock.lock_file,
                                            self._lock.unique_name))
            if dir_entries == lock_entries:
                # The directory was empty before we locked it.  Create a
                # package.
                open(self._index_path, 'wb').close()
                os.mkdir(self._files_path)
                self._index = {'version': self.__CURRENT_FORMAT_VERSION,
                               'data': {}, 'files': {}}
            else:
                try:
                    self.fsck()
                except InvalidPackageError:
                    # The directory was not a valid package.
                    self._lock.release()
                    raise
                else:
                    # The directory holds a valid package, and we just
                    # locked it.
                    try:
                        with open(self._index_path) as raw_index:
                            self._index = json.load(
                                raw_index,
                                object_hook=_asciify_keys,
                                )
                    except ValueError:
                        # Oops!  Turned out not to be valid at all!
                        # Probably, this means there was some value in
                        # the index that couldn't be asciified.
                        raise InvalidPackageError("could not read index")

    def sync(self):
        """Synchronize the package with its disk representation."""
        with open(self._index_path, 'w') as raw_index:
            json.dump(self._index, raw_index, indent=4)

    def close(self):
        """Close the handle on the package."""
        self.sync()
        self._lock.release()

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback):
        self.close()
        return False            # don't suppress exception

    @property
    def path(self):
        """The path at which the package is located."""
        return self._path

    @property
    def _index_path(self):
        return os.path.join(self.path, "index.json")

    @property
    def _files_path(self):
        return os.path.join(self.path, "files")

    @property
    def version(self):
        return self._index['version']

    def __contains__(self, item):
        return item in self._index['data'] or item in self._index['files']

    def __len__(self):
        return len(self._index['data']) + len(self._index['files'])

    def __iter__(self):
        return itertools.chain(self._index['data'], self._index['files'])

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(key)
        try:
            return self._index['data'][key]
        except KeyError:
            return os.path.join(self._files_path, self._index['files'][key])

    def __setitem__(self, key, value):
        return self.record_data(key, value)

    def record_data(self, key, value, json_encoder=json.JSONEncoder):
        if not isinstance(key, str):
            raise TypeError()

        if key in self:
            del self[key]

        # Convert the value to JSON and back to guarantee it can be
        # serialized to JSON without any special JSONEncoder at sync
        # time.
        json_value = json.loads(json.dumps(value, cls=json_encoder))

        # Record it.
        self._index['data'][key] = json_value

    def record_file(self, key, src_path):
        """Record a file in the package."""
        if not isinstance(key, str):
            raise TypeError()

        if isinstance(src_path, NoneType):
            return self.record_data(key, None)
        if not isinstance(src_path, str):
            raise TypeError()

        if key in self:
            del self[key]

        src_dir, src_name = os.path.split(src_path)
        dst_name = src_name
        # If the file/directory already exists in the destination
        # location, come up with a new unique name for the
        # file/directory.
        if os.path.exists(os.path.join(self._files_path, dst_name)):
            suffix = 0
            while os.path.exists(os.path.join(self._files_path,
                                              dst_name+"."+str(suffix))):
                suffix += 1
            dst_name += "." + str(suffix)
        dst_path = os.path.join(self._files_path, dst_name)

        # Copy the file/directory.
        try:
            shutil.copyfile(src_path, dst_path)
        except IOError as io_error:
            if io_error.errno == errno.EISDIR:
                shutil.copytree(src_path, dst_path)
            else:
                raise

        # Record it.
        self._index['files'][key] = dst_name

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise TypeError()

        try:
            del self._index['data'][key]

        except KeyError:
            to_remove = self[key]

            try:
                os.remove(to_remove)
            except OSError as os_error:
                if os_error.errno == errno.EISDIR:
                    shutil.rmtree(to_remove)
                else:
                    raise

            del self._index['files'][key]

    def fsck(self):
        """Check invariants about this package."""
        def require(cond, message):
            if not cond:
                raise InvalidPackageError(message)

        top_files = os.listdir(self._path)

        # Check for basic structure.
        require("index.json" in top_files, "package has no index")
        require("files" in top_files, "package has no file store")

        # Ensure we're actually tracking the files we think we're
        # tracking.
        try:
            file_index = self._index['files']
        except AttributeError:
            # We don't have an index yet, so forget about it.
            pass
        else:
            tracked_paths = set(file_index.itervalues())
            actual_paths = set(os.path.join(self._files_path, p)
                               for p in os.listdir(self._files_path))

            if tracked_paths == actual_paths:
                # Good deal.
                pass
            elif actual_paths.issubset(tracked_paths):
                raise InvalidPackageError("missing files: {0}".format(
                        ", ".join(tracked_paths - actual_paths),
                        ))
            elif tracked_paths.issubset(actual_paths):
                raise InvalidPackageError("untracked files: {0}".format(
                        ", ".join(actual_paths - tracked_paths),
                        ))


Package.register(JSONPackage)


class InvalidPackageError(Exception):
    """Indicates that the package has violated some invariant."""

    pass


def _asciify_keys(mapping):
    """Converts all the keys in a MutableMapping to ascii."""
    result = {}
    for key in mapping:
        result[str(key)] = mapping[key]
    return result
