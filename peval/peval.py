#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
# peval.py -- create a dummy configuration file  -*- coding: us-ascii -*-
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

from __future__ import absolute_import

# EXTERNAL PACKAGES
import argcomplete, argparse 
import sys

# INTERNAL PACKAGES
from . import evaluate
from . import register
from . import run
from . import unpackage
from . import utility


def register_parser(subparsers):
    parser = subparsers.add_parser('register')
    register.generate_parser(parser)
    return parser


def run_parser(subparsers):
    parser = subparsers.add_parser('run')
    run.generate_parser(parser)
    return parser


def evaluate_parser(subparsers):
    parser = subparsers.add_parser('evaluate')
    evaluate.generate_parser(parser)
    return parser


def unpackage_parser(subparsers):
    parser = subparsers.add_parser('unpackage')
    unpackage.generate_parser(parser)
    return parser


def generate_parser(parser):
    subparsers = parser.add_subparsers(help="subcommand")

    register_parser(subparsers)
    run_parser(subparsers)
    evaluate_parser(subparsers)
    return parser


def main():
    parser = argparse.ArgumentParser()
    generate_parser(parser)
    argcomplete.autocomplete(parser)
    arguments = parser.parse_args()
    try:
        sys.exit(arguments.func(arguments))
    except utility.FormatedError as e:
        utility.write(e)


if __name__ == "__main__":
    main()
