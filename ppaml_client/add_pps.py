# add_pps.py -- add a PPS to the database       -*- coding: us-ascii -*-
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

"""Add a PPS to the database."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import textwrap

from . import db
from . import static
from . import utility



#################################### Main #####################################


def main(arguments):
    """Insert the specified PPS into the database."""
    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)

    else:
        with index.session() as session:
            # PPSs have a many-to-many relationship with challenge
            # problems, so make sure the challenge problems are all in
            # the database.
            static.populate_db(session, index, commit=True)

            # Add the PPS.
            pps = index.PPS()
            pps.description = arguments.name
            try:
                pps.team_id = index.require_foreign_key(
                    index.Team,
                    team_id=arguments.team_id,
                    )
            except db.ForeignKeyViolation as exception:
                raise utility.FatalError(exception)

            else:
                # Ensure UNIQUE constraint is satisfied.
                if index.contains(index.PPS, team_id=arguments.team_id,
                                  description=arguments.name):
                    raise utility.FatalError(textwrap.fill(textwrap.dedent("""\
                        Duplicate PPS: This PPS is already registered.  Are
                        you sure you've set your description
                        correctly?""")))

                session.add(pps)
                session.commit()

                print("{0}".format(pps.pps_id))


def add_subparser(subparsers):
    """Register the 'add-pps' subcommand."""
    parser = subparsers.add_parser('add-pps', help="add PPS to the database")

    parser.add_argument('team_id', type=str, help="the team's database ID")
    parser.add_argument('name', type=str, help="the PPS's name")


    parser.set_defaults(func=main)
