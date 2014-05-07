# init.py -- create a dummy configuration file  -*- coding: us-ascii -*-
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

"""Create a configuration file."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import os.path

from . import db

from . import ps as configuration
from . import utility


#################################### Main #####################################


def main(arguments):
    """Create a configuration file."""

    cps_conf = configuration.CPSConfig()
    arguments.team_id

    arguments.challenge_problem_id
    arguments.configure
    cps_conf.populate_defaults(
      cp_id = arguments.challenge_problem_id,
      team_id = arguments.team_id,
      pps_id = arguments.pps if arguments.pps else arguments.team_id,
      configpath = arguments.configure
      )

    db.print_table_info(
      cps_conf['identifiers']['team_id'],
      cps_conf['identifiers']['pps_id'],
      cps_conf['identifiers']['challenge_problem_id']
    )

    if not arguments.output == '-':
        if os.path.exists(arguments.output) and not arguments.force:
            raise utility.FatalError(
                'refusing to overwrite configuration file "{0}"'.format(
                    arguments.output,
                    ),
                )
        cps_conf.filename = arguments.output

    try:
        cps_conf.write()
    except IOError as io_error:
        raise utility.FatalError(io_error)

def add_subparser(subparsers):
    """Register the 'init' subcommand."""
    parser = subparsers.add_parser('init', help="generate configuration file")

    parser.add_argument('team_id', type=int,
      help="your team number")

    parser.add_argument('challenge_problem_id', type=int,
      help="your the 'challenge problem' identifier number")

    parser.add_argument('-c', '--configure', default=os.devnull, type=str,
      help="path to your configuration scripts to be passed to a run.")

    parser.add_argument('--pps', type=int,
      help="your 'pps_id', defaults to your team number")

    parser.add_argument('-o', '--output', default='cps.ini', type=str,
      help="where to place the configuration file")

    parser.add_argument('-f', '--force', default=False, action="store_true",
      help="Force override of run.conf")

    parser.add_argument('--version', default="", type=str,
      help="your pps version")

    parser.set_defaults(func=main)
