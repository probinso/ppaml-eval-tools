# evaluate.py -- check artifact results         -*- coding: us-ascii -*-
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

"""Run an artifact evaluator to determine how well the artifact did."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import os
import subprocess

from . import ps as configuration
from . import db

from . import utility
from contextlib import nested


#################################### Main #####################################


def main(arguments):
    """Run an artifact evaluator."""
    # Read and validate configuration.
    conf = configuration.CPSConfig(infile=arguments.run_config)
    conf.require_fields(('evaluation', 'evaluator'),
                         ('evaluation', 'ground_truth'))

    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)

    with nested(
      utility.TemporaryDirectory(
        prefix='ppaml.',
        persist=arguments.persist
      ),
      index.session()
    ) as (sandbox, session):

        run_db_entry = index.run_specified_by(arguments.run_tid)
        if not run_db_entry:
            raise utility.FormatedError(
              "nonexistent run identifier {}",
              arguments.run_tid
            )

        evaluator = Evaluator(conf, run_db_entry)

        eval_output_paths = evaluator.go(sandbox)

        # Save data.
        if os.path.isdir(eval_output_paths):
            eval_output_paths = utility.path_walk(eval_output_paths)
        elif not os.path.isfile(eval_output_paths):
            raise IOError

        run_db_entry.quant_score = db.Index.migrate(eval_output_paths)


def add_subparser(subparsers):
    """Register the 'evaluate' subcommand."""
    parser = subparsers.add_parser('evaluate', help="evaluate artifact result")
    parser.add_argument('run_config', default='cps.ini',
                        help="run configuration file")
    parser.add_argument('run_tid', default='1', help="tag or run ID")
    parser.add_argument('-p', '--persist', action="store_true", default=False,
      help="to persist data, dont delete sandbox after use")
    parser.set_defaults(func=main)



################################# Evaluators ##################################


class Evaluator(object):
    """A template describing how to run an evaluator."""

    def __init__(self, run_config, run_db_entry):
        self.config = run_config
        self.run_db_entry = run_db_entry

    def go(self, sandbox):

        self.config.require_fields(
          ('evaluation', 'evaluator'),
          ('evaluation', 'ground_truth')
        )
        try:
            """Run an evaluator, collecting and returning the results."""
            evaluator_path = self.config.expand_executable(
              'evaluation',
              'evaluator'
              )

            # Reproduce the output from the run so the evaluator can look at
            # it.
            run_output_path = os.path.join(sandbox, 'run_output')
            run_output_path = db.Index.extract_blob(
              self.run_db_entry.output,
              run_output_path)

            ground_truth_path = self.config['evaluation']['ground_truth']
            eval_output_path = os.path.join(sandbox, 'output')
            # Run the evaluator.

            subprocess.call(
                [   evaluator_path,
                    run_output_path,
                    ground_truth_path,
                    eval_output_path
                    ]
                )

            return eval_output_path

        except IOError as io_error:
            raise utility.FatalError(io_error)

