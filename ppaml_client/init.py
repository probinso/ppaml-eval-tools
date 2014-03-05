# init.py -- create a dummy configuration file  -*- coding: us-ascii -*-
# Copyright (C) 2014  Galois, Inc.
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
#
# To contact Galois, complete the Web form at
# <http://corp.galois.com/contact/> or write to Galois, Inc., 421
# Southwest 6th Avenue, Suite 300, Portland, Oregon, 97204-1622.

"""Create a configuration file."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import os.path
import textwrap
import sys

from . import configuration
from . import utility
from . import __version__



#################################### Main #####################################


def main(arguments):
    """Create a configuration file."""
    try:
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

        # [artifact]
        conf['artifact'] = {}
        conf.comments['artifact'] = [
            '', '',
            "Fundamental properties of the artifact",
            ]
        # paths
        conf['artifact']['paths'] = ['artifact', 'support_files', '*.blah']
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
        # config
        conf['artifact']['config'] = '/dev/null'
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


        # [package]
        conf['package'] = {}
        conf.comments['package'] = [
            '', '',
            "Packaging",
            ]
        # base
        conf['package']['base'] = '/tmp/runs'
        conf['package'].comments['base'] = [
            '',
            "Where to place packaged runs",
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

        if arguments.output == '-':
            conf.write(sys.stdout)
        else:
            if os.path.exists(arguments.output):
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

    except utility.FatalError as fatal_error:
        print(textwrap.fill(str(fatal_error), width=80), file=sys.stderr)
        sys.exit(fatal_error.exit_status)


def add_subparser(subparsers):
    """Register the 'init' subcommand."""
    parser = subparsers.add_parser('init', help="generate configuration file")
    parser.add_argument('-o', '--output', default='run.conf', type=str,
                        help="where to place the configuration file")
    parser.set_defaults(func=main)
