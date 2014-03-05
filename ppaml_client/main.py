# main.py -- top-level PPAML tool               -*- coding: us-ascii -*-
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

"""Top-level PPAML tool.

This module should not be imported or run, except by the ppaml script.

"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import os.path
import sys

import argparse

from . import __version__
from . import evaluate
from . import fingerprint
from . import init
from . import run


def _generate_parser(version):
    """Create a parser for command-line arguments and subcommands."""
    # Generate the version string.
    version_string = "{0} {1} (library version {2})".format(
                         os.path.basename(sys.argv[0]),
                         version,
                         __version__,
                         )

    # Create parser and prepare to add subcommands.
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version',
                        version=version_string)
    subparsers = parser.add_subparsers(help="subcommand")

    # Version subcommand
    parser_version = subparsers.add_parser(
        'version',
        help="show program's version number and exit",
        )
    parser_version.set_defaults(func=lambda _args: print(version_string))

    # Help subcommand
    parser_version = subparsers.add_parser(
        'help',
        help="show this help message and exit",
        )
    parser_version.set_defaults(func=lambda _args: parser.print_help())

    # External subcommands
    init.add_subparser(subparsers)
    fingerprint.add_subparser(subparsers)
    run.add_subparser(subparsers)
    evaluate.add_subparser(subparsers)

    # All done.
    return parser


def main(version):
    """Parse command-line arguments and dispatch appropriately."""
    arguments = _generate_parser(version).parse_args()
    arguments.func(arguments)
