# tag.py -- add a tag to the database     -*- coding: us-ascii -*-
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

"""Add a tag to the database."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

from . import db



#################################### Main #####################################


def main(arguments):
    """Insert the specified tag lookup label into db."""

    if arguments.label.isdigit():
        print("\"{0}\" innapropriate tag, must include alphabetical characters",
          arguments.label)
        return

    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)

    else:
        with index.session() as session:
            # Ensure UNIQUE constraint is satisfied; if the user tries
            # to add a duplicate tag, update the one already in the
            # database.
            tag = session.query(index.Tag).filter_by(
                label=arguments.label,
                ).scalar()

            if not tag:
                tag = index.Tag()
                tag.label = arguments.label

            tag.run_id = index.require_foreign_key(
                index.Run,
                run_id=arguments.run_id,
                )
            session.add(tag)

            print("\"{0}\" tags {1}".format(tag.label, tag.run_id))


def add_subparser(subparsers):
    """Register the 'add-team' subcommand."""
    parser = subparsers.add_parser('tag', help="tag a 'run id' with a label")

    parser.add_argument('label', type=str, help="human readable label")
    parser.add_argument('run_id', type=int, help="run_id existing in database")

    parser.set_defaults(func=main)
