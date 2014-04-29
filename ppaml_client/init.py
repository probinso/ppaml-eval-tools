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
import textwrap
import sys

from . import db

from . import configuration
from . import utility
from . import __version__

def print_init_info(team_id, challenge_problem_id):
    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)

    else:
        with index.session() as session:
            # Ensure UNIQUE constraint is satisfied; if the user tries
            # to add a duplicate tag, update the one already in the
            # database.
            team = session.query(index.Team).filter_by(
              team_id=team_id,
              ).scalar()

            if not team:
                raise utility.FatalError(
                  "team_id {0} is invalid".format(team_id)
                )

            cp = session.query(index.ChallengeProblem).filter_by(
              challenge_problem_id=challenge_problem_id,
              ).scalar()

            if not cp:
                raise utility.FatalError("""\
                  challenge_problem_id {0}\
                  is invalid""".format(challenge_problem_id)
                )

            print("  Team              :: {0}".format(team.institution))
            print("  Challenge Problem :: {0}".format(cp.description))
            print("")

#################################### Main #####################################


def main(arguments):
    """Create a configuration file."""
    def _format(text):
        # Format all comment text at 78 characters so that when the
        # configurator prepends '# ', we'll get a nice block of text
        # wrapped at 80 characters.
        return textwrap.fill(textwrap.dedent(text), width=78).split('\n')

    conf = configuration.RunConfiguration()

    conf.initial_comment = [
        "Configuration file for PPAML run",
        "Created by ppaml init v{0}".format(__version__),
        "All paths are relative to the directory this file is stored in.",
        ]


    # [problem]
    conf['problem'] = {}
    conf.comments['problem'] = [
        '', '',
        "The problem the artifact is going to solve",
        ]
    # challenge_problem_id
    conf['problem']['challenge_problem_id'] = arguments.challenge_problem_id
    conf['problem'].comments['challenge_problem_id'] = [
        '',
        "What challenge problem the artifact is associated with",
        ]
    # team_id
    conf['problem']['team_id'] = arguments.team_id
    conf['problem'].comments['team_id'] = [
        '',
        "What team produced the artifact",
        ]
    # pps_id
    pps_id = arguments.pps if arguments.pps else arguments.team_id
    conf['problem']['pps_id'] = pps_id
    conf['problem'].comments['pps_id'] = [
        '',
        "What PPS the artifact runs under",
        ]


    # [artifact]
    conf['artifact'] = {}
    conf.comments['artifact'] = [
        '', '',
        "Fundamental properties of the artifact",
        ]
    # description
    conf['artifact']['description'] = "My cool probabilistic program"
    conf['artifact'].comments['description'] = [
        '',
        "A brief description of the artifact (optional)",
        ]
    # version
    conf['artifact']['version'] = arguments.version
    conf['artifact'].comments['version'] = [
        '',
        "The artifact version as a free-form string (optional)",
        ]
    # paths
    conf['artifact']['paths'] = ['artifact_exe', 'support_files', '*.blah']
    conf['artifact'].comments['paths'] = [
        '',
        "All the paths which contribute to this artifact",
        '#'
        ] + _format("""\
            This field gets used for two purposes.  It's used to determine
            which executable to run (the first file listed is assumed to be
            the executable), but it's also used to generate a unique
            identifier for the artifact.  You should thus list the primary
            executable first, followed by all of its source files.""")
    conf['artifact']['base'] = os.getcwd()

    # config
    conf['artifact']['config'] = arguments.configure
    conf['artifact'].comments['config'] = [
        '',
        "Path to the artifact configuration file",
        '#',
        ] + _format("""\
            This path will get passed to the artifact.  It's optional; if
            you don't specify it, the artifact will receive
            '/dev/null'.""")
    # input
    conf['artifact']['input'] = 'path/to/my_dataset'
    conf['artifact'].comments['input'] = [
        '',
        "Path to the artifact input",
        ]


    # [evaluation]
    conf['evaluation'] = {}
    conf.comments['evaluation'] = [
        '', '',
        "Evaluating runs",
        ]
    # evaluator
    conf['evaluation']['evaluator'] = ['evaluator.py', '*.h']
    conf['evaluation'].comments['evaluator'] = [
        '',
        "All the paths which contribute to the evaluator",
        '#',
        ] + _format("""\
            This field is interpreted in the same way as the "paths" field
            in the "artifact" section.""")
    # ground_truth
    conf['evaluation']['ground_truth'] = 'path/to/ground'
    conf['evaluation'].comments['ground_truth'] = [
        '',
        "Path to ground truth data",
        ]

    print_init_info(arguments.team_id, arguments.challenge_problem_id)

    if arguments.output == '-':
        conf.write(sys.stdout)
    else:
        if os.path.exists(arguments.output) and not arguments.force:
            raise utility.FatalError(
                'refusing to overwrite configuration file "{0}"'.format(
                    arguments.output,
                    ),
                )
        conf.filename = arguments.output
        try:
            conf.write()
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

    parser.add_argument('-o', '--output', default='run.conf', type=str,
      help="where to place the configuration file")

    parser.add_argument('-f', '--force', default=False, action="store_true",
      help="Force override of run.conf")

    parser.add_argument('--version', default="", type=str,
      help="your pps version")

    parser.set_defaults(func=main)
