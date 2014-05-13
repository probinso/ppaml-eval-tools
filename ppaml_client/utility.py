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

import inspect


def write(message=""):
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

def simple_list(li):
    """
      takes in a list li
      returns a sorted list without doubles
    """
    return sorted(set(li))


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
      Untars a tar.bz2 file to a directory then returns the appropriate dest
    """
    with tarfile.open(src) as tar:
        li = map(lambda x: x.path, tar.getmembers())
        tar.extractall(dest)
        dirnames = lambda x: os.path.dirname(x)
        return os.path.join(dest, os.path.commonprefix(map(dirnames,li)))


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


def tarball_abslists(contents, destpath, RESULT):
    """
      does what it says on the tin
    """
    from os.path import commonprefix, isabs
    assert(not filter(lambda x: not isabs(x), contents))
    return tarball_list(contents, destpath, RESULT, commonprefix(contents))


"""
  FILE OPERATIONS HAPPEN HERE
"""

def path_walk(srcpath, suffix='*'):
    """
      Takes in dirpath and returns list of non-hidden files and subdirectories
    """

    # glob ignores hidden filesx.
    paths = glob.glob(os.path.join(srcpath, suffix))

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
def digest(path):
    #takes path to tar.bz2 and returns digest.tar.bz2 to insure unique naming
    with open(path, 'rb') as fd:
        return hashlib.md5(fd.read()).hexdigest() + '.tar.bz2'

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


def testpath(path):
    if not os.path.exists(path):
        raise FormatedError("""\
          Configuration error: artifact configuration file
          "{}" is invalid""", path)
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
        if persist:
            print("data persists : " + tree)
        else:
            shutil.rmtree(tree)

