# utility.py -- miscellaneous code              -*- coding: us-ascii -*-
# Copyright (C) 2014  Galois, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#   1. Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.
#   3. Neither Galois's name nor the names of other contributors may be
#      used to endorse or promote products derived from this software
#      without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY GALOIS AND OTHER CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL GALOIS OR OTHER
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""
    Miscellaneous utility code that didn't seem to fit anywhere else.
    Prevents modules from making non-formant decisions
    Also can be run interactive mode to clearly test functionality
"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import contextlib
import tempfile
import shutil

import hashlib

import os
import glob
import tarfile


def simple_list(li):
    return sorted(set(li))


def split_filter(li, cond, op=lambda x:x):
    retval = [[],[]]
    for elm in li:
        retval[cond(elm)].append(op(elm))
    return retval


def FormatMessage(message, *args):
    """
      usage :: FormatMessage("{0} {1} {3} {2}", "cat", 2, 3, 4)
    """
    from textwrap import dedent, fill
    message = fill(dedent(message), 78).format(*args)
    return message


"""
  TAR FILE OPERATIONS HAPPEN HERE
"""

def untar_to_directory(src, dest):
    """
      Untars a tar.bz2 file to a directory
    """
    with tarfile.open(src) as tar:
        tar.extractall(dest)


def tarball_directory(dirpath, RESULT = "result.tar.bz2"):
    """
      Takes in a directory path, then produces a tar.bz2 file of it,
      then returns the path to RESULT.tar.bz2
    """
    contents = path_walk(dirpath)
    return tarball_list(contents, dirpath, RESULT, prefix=dirpath)


def tarball_list(contents, destpath, RESULT, prefix=""):
    """
      Takes in list of paths, and tarballs the contents uniquely ordered
      then returns the path to RESULT as a tar.bz2 archive
    """
    contents = simple_list(contents)
    path = os.path.join(destpath, RESULT)
    with tarfile.open(path, "w:bz2") as tar:
        for item in contents:
            if prefix: assert(item.startswith(prefix))
            arcitem = item[len(prefix):]
            tar.add(item, arcitem)
    return path


"""
  FILE OPERATIONS HAPPEN HERE
"""

def path_walk(srcpath, hidden=False):
    """
      Takes in dirpath and returns list of non-hidden files and subdirectories
    """

    # glob ignores hidden files
    paths = glob.glob(os.path.join(srcpath,'*'))

    [others, files] = split_filter(paths, os.path.isfile)

    for directory in filter(os.path.isdir, others):
        files += path_walk(directory)

    return files


def copy_directory_files(srcdir, dstdir, filenames):
    """
      copies [filenames] from srcdir to dstdir
    """
    for filename in filenames:
        srcpath = os.path.join(srcdir, filename)
        dstpath = os.path.join(dstdir, filename)
        shutil.copyfile(srcpath, dstpath)

""""""
def digest(path):
    with open(path, 'rb') as fd:
        return hashlib.md5(fd.read()).hexdigest()

""""""
class FatalError(Exception):
    """An unrecoverable condition from which the program must exit."""
    def __init__(self, message, exit_status=9):
        super(FatalError, self).__init__(message)
        self.exit_status = exit_status


class FormatedError(FatalError):
    """An unrecoverable condition from which the program must exit."""
    def __init__(self, message, *elms):
       message = FormatMessage(message, *elms)
       FatalError.__init__(self, message, exit_status=9)


@contextlib.contextmanager
def TemporaryDirectory(suffix='', prefix='tmp', dir=None):
    """Like tempfile.NamedTemporaryFile, but creates a directory.

    This object appears in Python 3 but is unfortunately absent from
    releases of Python 2.

    """
    tree = tempfile.mkdtemp(suffix, prefix, dir)
    try:
        yield tree
    finally:
        shutil.rmtree(tree)

