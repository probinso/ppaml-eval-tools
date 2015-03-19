#!/usr/bin/bpython -i 
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

#import tempfile
import shutil

import hashlib

import os
import glob
import tarfile
import tempfile
import inspect
import xdg.BaseDirectory


SUCC_RUN = True

def failed_run():
    global SUCC_RUN
    SUCC_RUN = False

def location_resource(
  fname='.',
  location=xdg.BaseDirectory.save_data_path('ppaml')
  ):
    return os.path.join(location, fname)


def get_resource(fname='.'):
    path = location_resource(fname=fname)
    return test_path(path)

def commit_resource(full_path):
    srcdir, fname = os.path.split(test_path(resolve_path(full_path)))
    copy_directory_files(srcdir, location_resource(), [fname])
    return True


def write(message):
    """
      debugging tool prints out message and other helper data
    """
    DEBUG = True
    if DEBUG:
        from sys import __stderr__ as std
        _lineno = inspect.currentframe().f_back.f_lineno
        _name = inspect.currentframe().f_back.f_code.co_filename
        _name = os.path.split(_name)[1]
        std.write('% '+str(_lineno)+'-'+_name+' : '+str(message)+'\n')
    return message

def simple_list(li, cond=cmp):
    """
      takes in a list li
      returns a sorted list without doubles
    """
    try:
        return sorted(set(li), cmp=cond)
    except TypeError:
        # handle edgecase where only one element not in list form is passd in.
        # would like same behaviour even if this function is missused.
        return [li]


def split_filter(li, cond, op=lambda x:x):
    """
      takes in list and conditional
      returns [[False], [True]] split list in O(n) time
    """
    retval = [[],[]]
    for elm in li:
        index = cond(elm)
        retval[index].append(op(elm) if index else elm)
    return retval


def safesplit(s, c):
    # input string and substring c
    # return list of strings, divided on substring c
    return filter(lambda x: x, s.split(c)) if s.count(c) else s


def FormatMessage(message, *args):
    """
      usage :: FormatMessage("{0} {1} {3} {2}", "cat", 2, 3, 4)
    """
    from textwrap import dedent, fill
    message = fill(dedent(message.format(*args)), 78)
    return message


"""
  TAR FILE OPERATIONS HAPPEN HERE
"""

def untar_to_directory(src, dest):
    """
      Untars a tar.bz2 file to a directory then returns the appropriate dest
    """
    with tarfile.open(src) as tar:
        li = map(lambda x: x.path, tar.getmembers())
        tar.extractall(test_path(dest))
        return os.path.join(dest, dircommonprefix(li))


def unpack_parts(dest, *args):
    """
    """
    retval = []
    for (key, value) in args:
        if not value:
            path = os.path.join(os.path.realpath(dest), key)
        else:
            path = unpack_part(value, dest, key)
        retval.append(path)
    return retval


def unpack_part(unique_id, dest, label):
    """
    """
    fname = get_resource(unique_id)
    dstdir = os.path.join(dest, label)
    return untar_to_directory(fname, dstdir)


def resolve_path(path):
    return os.path.realpath(os.path.expanduser(path))


def prepare_resource(inpath, dstdir):
    """
      Take inpath and dstdir then produces inpath.tar.bz2, 
      renames to its digest, moves to dstdir. returns digest.tar.bz2
    """
    inpath, dstdir = resolve_path(inpath), resolve_path(dstdir)
    perf = inpath

    if os.path.isdir(inpath):
        contents = path_walk(inpath)
    else:
        contents = [inpath]
        perf = os.path.dirname(perf)

    contents = map(os.path.abspath, contents)

    unique_name = digest_paths(contents)+".tar.bz2"
    tmpbz = "ppaml-tmp.tar.bz2"
    tmpbz = tarball_list(contents, perf, tmpbz, perf)

    final_path = os.path.join(dstdir, unique_name)
    shutil.move(tmpbz, final_path)

    return unique_name, final_path


def tarball_list(contents, destpath, RESULT, prefix=""):
    """
      Takes in list of paths, and tarballs the contents uniquely ordered
      then returns the path to RESULT as a tar.bz2 archive

      if prefix undefined, then defaults to not remove any of the path
      if prefix is set to None then os.path.commonprefix is removed
    """

    contents = simple_list(contents)

    path = os.path.join(destpath, RESULT)
    with tarfile.open(path, "w:bz2") as tar:
        for item in contents:
            if prefix: assert(item.startswith(prefix))
            arcitem = item[len(prefix):]
            tar.add(item, arcitem)

    return path

def dircommonprefix(li):
    from os.path import commonprefix, split
    cp = commonprefix(map(os.path.dirname, li))
    x, y = split(cp)
    if y[:-1] == "dataset": # XXXPMR This is not okay and is hacky
        return x
    else:
        return cp


"""
  FILE OPERATIONS HAPPEN HERE
"""

def path_walk(srcpath, suffix='*'):
    """
      Takes in dirpath and returns list of files and subdirectories (includes hidden)
    """

    # glob ignores hidden filesx.
    paths = glob.glob(os.path.join(srcpath, suffix)) + glob.glob(os.path.join(srcpath, "." + suffix))

    [others, files] = split_filter(paths, os.path.isfile)

    for directory in filter(os.path.isdir, others):
        files += path_walk(directory)

    # XXX: we do not actually want to return srcpath aswell
    return files # + [srcpath] # if directory is empty, must include srcpath


def copy_directory_files(srcdir, dstdir, filenames):
    """
      copies [filenames] from srcdir to dstdir
    """
    for filename in filenames:
        srcpath = os.path.join(srcdir, filename)
        dstpath = os.path.join(dstdir, filename)
        shutil.copyfile(srcpath, dstpath)


def expand_path_list(paths, prefix='.', test=False):
    """
      takes in list of relative path expressions, then expands them to abspaths
      if abspaths are included in 'paths', the prefix is not prepended

      returns list that has no doubles, and is sorted alphabetically

      TODO: incorperate 'existance testing'
    """
    prefix = os.path.expanduser(prefix)

    complete_path = \
    lambda elm: os.path.join(prefix, elm) if not os.path.isabs(elm) else elm

    paths = map(complete_path, paths)
    for i, path in enumerate(paths):
        if path[-1] == '*':
            d, f = os.path.split(path)
            paths[i] = path_walk(d, suffix=f)
        else:
            paths[i] = glob.glob(path)
        paths[i] = map(os.path.abspath, paths[i])

    return simple_list(reduce(lambda a,b: a+b, paths))

""""""
def digest_paths(paths):
    """
      takes in a list of paths that exist and are readable
      returns digest SHA hash to be used as identifier over the whole list
    """
    SHAhash = hashlib.sha1()
    for filename in simple_list(paths):
        f = open(filename, 'rb')
        while True:
            # Read files as little chunks to prevent wierd ram usage
            buf = f.read(4096)
            if not buf : break
            SHAhash.update(hashlib.sha1(buf).hexdigest())
        f.close()
    return SHAhash.hexdigest()

""""""
class FatalError(Exception):
    """An unrecoverable condition from which the program must exit."""
    def __init__(self, message, exit_status=-79):
        super(FatalError, self).__init__(message)
        self.exit_status = exit_status


class FormatedError(FatalError):
    """An unrecoverable condition from which the program must exit."""
    def __init__(self, message, *elms):
       message = FormatMessage(message, *elms)
       FatalError.__init__(self, message, exit_status=-191)


def test_path(path):
    if not (path or os.path.exists(path)):
        raise FormatedError("""\
          File error: artifac file
          "{}" is invalid : Does Not Exist""", path)
    return path


@contextlib.contextmanager
def TemporaryDirectory(suffix='', prefix='tmp', dir=None, persist=False):
    """
      Like tempfile.NamedTemporaryFile, but creates a directory.

      This object appears in Python 3 but is unfortunately absent from
      releases of Python 2.
    """
    tree = tempfile.mkdtemp(suffix, prefix, dir)
    try:
        yield tree
    finally:
        global SUCC_RUN
        if not SUCC_RUN:
            newtree = tree + '.FAILED'
            os.rename(tree, newtree)
            tree = newtree
        if not SUCC_RUN or persist:
            print("Success : " + str(SUCC_RUN))
            print("data persists : " + tree)
        else:
            shutil.rmtree(tree)

