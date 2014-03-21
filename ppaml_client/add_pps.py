# add_pps.py -- add a PPS to the database       -*- coding: us-ascii -*-
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

"""Add a PPS to the database."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import textwrap

import sqlalchemy

from . import db
from . import static
from . import utility



#################################### Main #####################################


def main(arguments):
    """Insert the specified PPS into the database."""
    # PPSs have a many-to-many relationship with challenge problems, so
    # make sure the challenge problems are all in the database.
    static.populate_db()

    # Add the PPS.
    with db.session() as session:
        pps = db.PPS()
        pps.team_id = arguments.team_id
        pps.description = arguments.name
        pps.version = arguments.version
        session.add(pps)

        try:
            # This must be a commit, not just a flush, since we need
            # foreign key constraints to be checked.
            session.commit()
        except sqlalchemy.exc.IntegrityError as integrity_error:
            session.rollback()
            if 'foreign key' in integrity_error.orig.message.lower():
                raise utility.FatalError("invalid team ID")
            else:
                # The PPS has already been added.  Warn the user.
                existing_id = session.query(db.PPS).filter_by(
                    description=arguments.name,
                    version=arguments.version,
                    )[0].pps_id
                raise utility.FatalError(textwrap.fill(textwrap.dedent("""\
                    Duplicate PPS: This PPS is already registered with PPS ID
                    {0}.  Are you sure you've set your description and version
                    correctly?""".format(existing_id))))

        print("{0}".format(pps.pps_id))


def add_subparser(subparsers):
    """Register the 'add-pps' subcommand."""
    parser = subparsers.add_parser('add-pps', help="add PPS to the database")

    parser.add_argument('team_id', type=str, help="the team's database ID")
    parser.add_argument('name', type=str, help="the PPS's name")
    parser.add_argument('version', type=str, help="the PPS's version string")

    parser.set_defaults(func=main)
