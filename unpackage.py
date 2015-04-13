"""
#!/usr/bin/python
# inspect.py -- inspect archive managed by database  -*- coding: us-ascii -*-
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

import argparse
import sys
import model as mod
import utility


def register_stub_cli(arguments):
    pass


def engine_subparser(subparsers):
    parser = subparsers.add_parser('engine')
    parser.set_defaults(func=register_stub_cli)


def solution_subparser(subparsers):
    parser = subparsers.add_parser('solution')
    parser.set_defaults(func=register_stub_cli)


def configuration_subparser(subparsers):
    parser = subparsers.add_parser('configuration')
    parser.set_defaults(func=register_stub_cli)


def dataset_subparser(subparsers):
    parser = subparsers.add_parser('dataset')
    parser.set_defaults(func=register_stub_cli)


def evaluator_subparser(subparsers):
    parser = subparsers.add_parser('evaluator')
    parser.set_defaults(func=register_stub_cli)


def generate_parser(parser):
    subparsers = parser.add_subparsers(help="subcommand")

    # initialize subparsers
    engine_subparser(subparsers)
    solution_subparser(subparsers)
    configuration_subparser(subparsers)
    dataset_subparser(subparsers)
    evaluator_subparser(subparsers)

    return parser


def main():
    parser = argparse.ArgumentParser()
    arguments = generate_parser(parser).parse_args()
    sys.exit(arguments.func(arguments))


if __name__ == "__main__":
    main()


"""
