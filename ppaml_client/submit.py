# submit.py -- submit info from run to galois     -*- coding: us-ascii -*-
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

"""submit info from run to galois"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

from shutil import copyfile
from shutil import move

import xdg.BaseDirectory
import os.path

import tarfile

from . import db
from . import utility

def run_to_artifact_data(db, session, run):
    """
      takes in run and returns relevent/'detached' artifact data
    """

    assert(run is not None)

    filenames = [run.artifact_id]

    artifact = session.query(db.Artifact).filter_by(
      artifact_id = run.artifact_id).scalar()

    filenames += [
      artifact.binary, artifact.compiler, artifact.build_configuration
      ]
    filenames = filter(lambda x: x is not None, filenames)

    session.expunge(artifact) # detaches artifact from current db session
    return artifact, filenames


def copy_files_to_submit(srcdir, dstdir, filenames):
    for filename in filenames:
        srcpath = os.path.join(srcdir, filename)
        dstpath = os.path.join(dstdir, filename)
        copyfile(srcpath, dstpath)


def create_tables_to_submit(tmpdir, table_entries):
    try:
        index = db.Index(path=os.path.join(tmpdir, "submit.db"))
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)
    else:
        with index.session() as session:
            session.execute("PRAGMA foreign_keys=OFF") # this is special case
            for entry in table_entries:
                entry = session.merge(entry) # attach entry to current session
                session.add(entry)

SUBMIT = "submit.tar.gz"

def package_directory(submitdir):
    contents = os.listdir(submitdir)
    path = os.path.join(submitdir, SUBMIT)
    with tarfile.open(path, "w:gz") as tar:
        for item in contents:
            tar.add(os.path.join(submitdir, item))
    return path

def submit_package(srcdir, dstdir):
    send = os.path.join(dstdir, SUBMIT)
    move(os.path.join(srcdir, SUBMIT), send)
    print("please e-mail \"{0}\" to the contact ".format(SUBMIT),
      "e-mail address for the challenge problem")


#################################### Main #####################################
def main(arguments):
    """given a list of tags and run_ids this procedure packages up cooresponding
       artifact information, then submits it
    """
    if not os.path.isdir(arguments.path):
        print("path does not exist : \"{0}\"".format(arguments.path))
        return # TODO: raise fatal exception instead of return

    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)
    else:
        with index.session() as session:
            runs = [[],[]] # [[failed], [successful]]

            for run_tid in arguments.run_tids:
                run = index.run_specified_by(run_tid)

                # this will store failed run_tids in runs[False] for later use
                runs[bool(run)].append(run if run else run_tid)

            if runs[False]:
                print("nonexistant run_tids {0}".format(runs[False]),
                ": NO ACTION TAKEN")
                return # TODO: raise fatal exception instead of return

            # this will remove doubles of the successfully addressed runs
            runs = set(runs[True])

            # cannot move 'map' out of with statement, dependent on session
            get_artifact = lambda run: run_to_artifact_data(index, session, run)
            artifact_datas = map(get_artifact, runs)

    artifacts, filenames = [], []
    for artifact, artifact_files in artifact_datas:
        artifacts.append(artifact)
        filenames += artifact_files
    artifacts, filenames = set(artifacts), set(filenames)

    srcdir = xdg.BaseDirectory.save_data_path('ppaml')
    with utility.TemporaryDirectory() as dstdir:
        create_tables_to_submit(dstdir, artifacts)
        copy_files_to_submit(srcdir, dstdir, filenames)

        package = package_directory(dstdir)
        submit_package(dstdir, arguments.path)

    print("submit successful!")


def add_subparser(subparsers):
    """Register the 'add-team' subcommand."""
    parser = subparsers.add_parser(
      'submit',
      help="submit artifact data associated with tag or run_id")

    parser.add_argument('path', type=str,
      help="directory to save submit.tar.gz")

    parser.add_argument('run_tids', type=str, nargs='+',
      help='list of tags or run_ids')

    parser.set_defaults(func=main)
