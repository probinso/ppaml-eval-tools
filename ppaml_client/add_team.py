# add_team.py -- add a team to the database     -*- coding: us-ascii -*-
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

"""Add a performer team to the database."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

from . import db
from . import utility



#################################### Main #####################################


def main(arguments):
    """Insert the specified team into the database."""
    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)

    else:
        with index.session() as session:
            # Ensure UNIQUE constraint is satisfied; if the user tries
            # to add a duplicate team, just use the one already in the
            # database.
            team = session.query(index.Team).filter_by(
                institution=arguments.institution,
                contact_name=arguments.contact_name,
                contact_email=arguments.contact_email,
                ).scalar()

            if not team:
                team = index.Team()
                team.institution = arguments.institution
                team.contact_name = arguments.contact_name
                team.contact_email = arguments.contact_email
                session.add(team)

                session.commit()

            print("{0}".format(team.team_id))


def add_subparser(subparsers):
    """Register the 'add-team' subcommand."""
    parser = subparsers.add_parser('add-team', help="add team to the database")

    parser.add_argument('institution', type=str, help="the team's institution")
    parser.add_argument('contact_name', type=str,
                        help="the team's primary point-of-contact")
    parser.add_argument('contact_email', type=str,
                        help="the point-of-contact's e-mail adddress")

    parser.set_defaults(func=main)
