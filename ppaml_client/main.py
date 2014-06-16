# main.py -- top-level PPAML tool               -*- coding: us-ascii -*-
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

"""Top-level PPAML tool.

This module should not be imported or run, except by the ppaml script.

"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import os.path
import sys

import argparse

from . import __version__
from . import add_pps
from . import add_team
from . import evaluate
from . import fingerprint
from . import init
from . import run
from . import utility
from . import tag
from . import submit


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
    run.add_subparser(subparsers)
    evaluate.add_subparser(subparsers)
    tag.add_subparser(subparsers)
    submit.add_subparser(subparsers)

    # Internal subcommands
    if False: # change to True if you are a contributer
        add_team.add_subparser(subparsers)
        add_pps.add_subparser(subparsers)
        fingerprint.add_subparser(subparsers)

    # All done.
    return parser


def main(version):
    """Parse command-line arguments and dispatch appropriately."""
    arguments = _generate_parser(version).parse_args()
    try:
        sys.exit(arguments.func(arguments))
    except utility.FatalError as fatal_error:
        print("", file=sys.stderr)
        print("!! ERROR !!    ppaml says - ", file=sys.stderr)
        print(fatal_error, file=sys.stderr)
        print("",file=sys.stderr)
        sys.exit(fatal_error.exit_status)

