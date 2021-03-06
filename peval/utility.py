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

from __future__ import (absolute_import, division, print_function)

import contextlib

import shutil

import hashlib
from itertools import ifilter

import os
import os.path as osp
import glob
import tarfile
import tempfile
import inspect
import xdg.BaseDirectory
import stat

import time
import subprocess
import psutil


"""
  ::SUCC_COMMENT
  This is used below in the contextmanager for directories.
"""
RUN_STATE = ['.SUCCESS', '.FAILED', '.INTERRUPT', '.CRASH', '.UNDECIDED']
"""
SUCCESS   -> Run Successfuly terminates
FAILED    -> Run Unsuccessfuly terminates
INTERRUPT -> Sigint sent to peval
CRASH     -> peval crashed
UNDECIDED -> Presently running, exit status undecided
"""
SUCC_RUN = 0

DEBUG = True

def failed_exec():
    global SUCC_RUN
    SUCC_RUN = 1

def signal_handler(signum, frame):
    global SUCC_RUN
    SUCC_RUN = 2
    raise FormattedError("Signal handler called with signal '{}'", signum)
"""
  ::SUCC_COMMENT
  This ends SUCC_COMMENT related data and modifications
"""

def location_resource(
  fname='.',
  location=xdg.BaseDirectory.save_data_path('peval')
  ):
    return osp.join(location, fname)

def glob_resource(fname):
    path = location_resource(fname=(fname + "*"))
    candidates = glob.glob(path)
    if len(candidates) != 1:
        raise FormattedError("Identifier %s is not unique. Please specify further", path)
    return test_path(candidates[0])

def get_resource(fname='.'):
    path = location_resource(fname=fname)
    return test_path(path)

def commit_resource(full_path):
    srcdir, fname = osp.split(test_path(resolve_path(full_path)))
    copy_directory_files(srcdir, location_resource(), [fname])
    return True

def write(message):
    """
      debugging tool prints out message and other helper data
    """
    global DEBUG
    if DEBUG:
        from sys import __stderr__ as std
        _lineno = inspect.currentframe().f_back.f_lineno
        _name = inspect.currentframe().f_back.f_code.co_filename
        _name = osp.split(_name)[1]
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
        # handle edgecase where only one element not in list form is passd
        # in. would like same behaviour even if this function is missused.
        return [li]


def file_from_tree(tstname, dir_path, check=True):
    """
      given a tstname and a directory path, this function returns the first
      instance of tstname from a directory walk of the path
    """
    if osp.isdir(dir_path):
        this_file = next(ifilter(
            lambda x: osp.basename(x) == osp.basename(tstname),
            path_walk(dir_path)),
            None
        )

    if check and not this_file:
        raise FormattedError(
          "'{}' script does not exist in '{}'",
          tstname, dir_path
        )

    return this_file


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
    """
      input string and substring c
      return list of strings, divided on substring c
    """
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
    if not (osp.exists(dest)):
      os.mkdir(dest)
    with tarfile.open(src) as tar:
        li = map(lambda x: x.path, tar.getmembers())
        tar.extractall(dest)
        return dest


def unpack_parts(dest, *args):
    """
      ???
    """
    # XXX PMR :: I don't know why this exists, but it is used...
    retval = []
    for (key, value) in args:
        if not value:
            path = osp.join(osp.realpath(dest), key)
        else:
            path = unpack_part(value, dest, key)
        retval.append(path)
    return retval


def unpack_part(unique_id, dest, label=''):
    """
      takes in hashed id, destination, and new directory label
      returns root directory of extracted archive

      retrieves resource path for id.tar.bz2
      creates directory dest/label
      untars id.tar.bz2 to dest/label/...
    """
    fname = get_resource(unique_id)
    dstdir = osp.join(dest, label)
    return untar_to_directory(fname, dstdir)


def resolve_path(path, allow_symbol=False):
    """
    """
    path = osp.expanduser(path)
    if not allow_symbol:
        path = osp.realpath(path)
    if osp.exists(path) and osp.isdir(path):
        path = osp.join(path,'')
    return path


def prepare_resource(inpath, dstdir, allow_symbol=False):
    """
      Take inpath and dstdir then produces inpath.tar.bz2, 
      renames to its digest, moves to dstdir. returns digest.tar.bz2

      allow_symbol determines if inpath allows preservation of symlinks
    """
    inpath, dstdir = resolve_path(inpath, allow_symbol), \
                     resolve_path(dstdir)

    perf = inpath

    if osp.isdir(inpath):
        contents = path_walk(inpath)
    else:
        contents = [inpath]
        perf = resolve_path(osp.dirname(perf))

    contents = map(osp.abspath, contents)

    unique_name = digest_paths(contents)+".tar.bz2"
    tmpbz = "ppaml-tmp.tar.bz2"
    tmpbz = tarball_list(contents, perf, tmpbz, perf)

    final_path = osp.join(dstdir, unique_name)
    shutil.move(tmpbz, final_path)

    return unique_name, final_path


def tarball_list(contents, destpath, RESULT, prefix=""):
    """
      Takes in list of paths, and tarballs the contents uniquely ordered
      then returns the path to RESULT as a tar.bz2 archive

      if prefix undefined, then defaults to not remove any of the path
      if prefix is set to None then osp.commonprefix is removed
    """

    contents = simple_list(contents)

    path = osp.join(destpath, RESULT)
    with tarfile.open(path, "w:bz2") as tar:
        for item in contents:
            if prefix: assert(item.startswith(prefix))
            arcitem = item[len(prefix):]
            tar.add(item, arcitem)

    return path


def dircommonprefix(li):
    cp = osp.commonprefix(map(osp.dirname, li))
    x, y = osp.split(cp)
    if y[:-1] == "dataset": # XXX PMR This is not okay and is hacky
        return x
    else:
        return cp


"""
  FILE OPERATIONS HAPPEN HERE
"""

def path_walk(srcpath, suffix='*'):
    """
      Takes in dirpath and returns list of files and subdirectories
      (includes hidden)
    """

    # glob ignores hidden filesx.
    paths = glob.glob(osp.join(srcpath, suffix)) + \
            glob.glob(osp.join(srcpath, "." + suffix))

    [others, files] = split_filter(paths, osp.isfile)

    for directory in filter(osp.isdir, others):
        files += path_walk(directory)

    # XXX: we do not actually want to return srcpath aswell
    return files # + [srcpath] # if directory is empty, must include srcpath


def copy_directory_files(srcdir, dstdir, filenames):
    """
      copies [filenames] from srcdir to dstdir
    """
    for filename in filenames:
        srcpath = osp.join(srcdir, filename)
        dstpath = osp.join(dstdir, filename)
        shutil.copyfile(srcpath, dstpath)


def expand_path_list(paths, prefix='.', test=False):
    """
      takes in list of relative path expressions, then expands them to
      abspaths if abspaths are included in 'paths', the prefix is not
      prepended

      returns list that has no doubles, and is sorted alphabetically

      TODO: incorperate 'existance testing'
    """
    prefix = osp.expanduser(prefix)

    complete_path = \
    lambda elm: osp.join(prefix, elm) if not osp.isabs(elm) else elm

    paths = map(complete_path, paths)
    for i, path in enumerate(paths):
        if path[-1] == '*':
            d, f = osp.split(path)
            paths[i] = path_walk(d, suffix=f)
        else:
            paths[i] = glob.glob(path)
        paths[i] = map(osp.abspath, paths[i])

    return simple_list(reduce(lambda a,b: a+b, paths))


""""""
def digest_paths(paths):
    """
      takes in a list containing paths to files
      returns digest SHA hash to be used as identifier over the whole list

      if the file is empty or is a symbolic link, then the file's name is
      used for the digest rather than it's contents.

      the reason that we don't digest over the contents of
        os.open(f, os.O_NOFOLLOW)
      instead is that multiple symlinks may point to the same file, but not
      have the same name. (this may be a strong assumption, but satisfies
      for now)
    """
    SHAhash = hashlib.sha1()

    filetypes = lambda n: osp.islink(n) or os.lstat(n).st_size == 0
    [real_paths, sym_or_empty] = split_filter(paths, filetypes)

    for filename in simple_list(real_paths):
        buf = filename
        SHAhash.update(hashlib.sha1(buf).hexdigest())

        f = open(filename, 'rb')

        while True:
            # Read files as little chunks to prevent large ram usage
            buf = f.read(4096)
            if not buf : break
            SHAhash.update(hashlib.sha1(buf).hexdigest())
        f.close()

    # handle symlinks and empty files by digesting over filename instead
    for filename in [osp.basename(name) for name in sym_or_empty]:
        buf = filename
        SHAhash.update(hashlib.sha1(buf).hexdigest())

    return SHAhash.hexdigest()


def process_watch( base_dir, command, timeout=3.0, isfile=True,
  **environment_variables
):
    """
      This yields an iterator over
        subprocess.Popen(cmd,env), return code, time_start, time_curr
      so that the user may gain nessicary resources for tracking statisrics
      in a simple loop.

      Takes in a base directory as a new working directory, and a command
      as a list of strings
      Optional :: timeout provides a timestep for gathering use metrics
               :: isfile is used to define whether this command is in the
               local directory tree
    """

    pwd = os.getcwd() # previous working directory
    test_path(base_dir)
    os.chdir(base_dir)

    proc_env = os.environ.copy()
    for index in environment_variables:
        proc_env[index] = environment_variables[index]

    rc = None
    proc_entry = None

    if isfile:
        command[0] = file_from_tree(command[0], base_dir, False)
        if command[0] is not None:
            st = os.stat(command[0])
            os.chmod(command[0], st.st_mode | stat.S_IEXEC)

    write("Command: " + str(command))
    write("ENV: " + str(environment_variables))

    start_t = time.time()

    if command[0] is not None:

        proc = subprocess.Popen(command, env=proc_env)
        proc_entry = psutil.Process(proc.pid)

        while True:
            # this program used to catch the following errors
            # :: psutil.AccessDenied, psutil.NoSuchProcess
            yield proc_entry, rc, start_t, time.time()

            try:
                rc = proc_entry.wait(timeout=timeout) # seconds
                if rc is None:
                    continue
                else:
                    # The timeout didn't expire--the process exited while we
                    # waited.  We're done.
                    break
            except psutil.TimeoutExpired:
                # write("psutil.TimeoutExpired hit")
                # Our timeout expired, but the process still exists.
                # Keep going.
                continue

        os.chdir(pwd)

        yield proc_entry, rc, start_t, time.time()
    else:
        yield None, None, None, None

""""""
class FatalError(Exception):
    """An unrecoverable condition from which the program must exit."""
    def __init__(self, message, exit_status=-79):
        super(FatalError, self).__init__(message)
        self.exit_status = exit_status


class FormattedError(FatalError):
    """An unrecoverable condition from which the program must exit."""
    def __init__(self, message, *elms):
       message = FormatMessage(message, *elms)
       FatalError.__init__(self, message, exit_status=-191)


def test_path(path):
    if not osp.exists(path):
        raise FormattedError("File error: '{}' does not exist", path)
    return path


@contextlib.contextmanager
def TemporaryDirectory(suffix='', prefix='peval.', dir=None, persist=False):
    """
      Like tempfile.NamedTemporaryFile, but creates a directory.

      This object appears in Python 3 but is unfortunately absent from
      releases of Python 2.
    """

    base_tree = tempfile.mkdtemp(suffix, prefix, dir)
    undecided_tree = base_tree + RUN_STATE[-1]
    os.rename(base_tree, undecided_tree)
    global SUCC_RUN
    global RUN_STATE

    try:
        yield undecided_tree

    except Exception as e:
        if SUCC_RUN != 2: # insure not to squash .INTERRUPT
            SUCC_RUN = -2
        raise e

    finally:
        """
          This is probably the most dangerous part of code. SUCC_RUN is a 
            global variable used to track the terminating state of a peval
            run. RUN_STATE is the array of strings denoting the human
            readable name of that state. For more info, look for 
          ::SUCC_COMMENT
        """

        tree = base_tree + RUN_STATE[SUCC_RUN]
        if SUCC_RUN != 0:
            persist = True

        os.rename(undecided_tree, tree)
        print("Success : " + RUN_STATE[SUCC_RUN])

        if persist:
            print("data persists : " + tree)
        else:
            shutil.rmtree(tree)

