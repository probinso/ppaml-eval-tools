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

import errno
import os
import subprocess
import textwrap
import sys

from . import configuration
from . import db
from . import utility



#################################### Main #####################################


def main(arguments):
    """Run an artifact evaluator."""
    # Read and validate configuration.
    conf = configuration.read_from_file(
        arguments.run_config,
        required_fields=(('evaluation', 'evaluator'),
                         ('evaluation', 'ground_truth')),
        )

    # What are we evaluating?
    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)
    else:
        with index.session():
            run_to_evaluate = index.run_specified_by(arguments.run_tid)
            if not run_to_evaluate:
                raise utility.FatalError(
                    "nonexistent run identifier {}".format(arguments.run_tid),
                    )

            else:
                evaluator = Evaluator(conf, run_to_evaluate)
                with utility.TemporaryDirectory(prefix='ppaml.') as sandbox:
                    results = _run_evaluator(evaluator, sandbox)

                    # Save data.
                    _record_evaluation(index, results, sandbox)


def _run_evaluator(evaluator, sandbox):
    try:
        return evaluator.go(sandbox)

    except (configuration.MissingField,
            configuration.EmptyField) as missing_field:
        raise utility.FatalError("Configuration error: {0}".format(
                missing_field,
                ),
                                 10)

    except IndexError:
        raise utility.FatalError(
            textwrap.dedent("""\
                Configuration error: field "evaluator" (in section
                "evaluation") does not refer to a file."""),
            10,
            )

    except IOError as io_error:
        raise utility.FatalError(io_error)


def _record_evaluation(index, evaluation, sandbox):
    """Package an evaluation."""
    try:
        output_paths = os.listdir(evaluation.output_path)
    except OSError as os_error:
        if os_error.errno == errno.ENOTDIR:
            # The evaluator created a file, not a directory.
            output_paths = (evaluation.output_path,)
        else:
            raise

    evaluation.run.quant_score = db.Index.migrate(output_paths, sandbox)


def add_subparser(subparsers):
    """Register the 'evaluate' subcommand."""
    parser = subparsers.add_parser('evaluate', help="evaluate artifact result")
    parser.add_argument('run_config', default='run.conf',
                        help="run configuration file")
    parser.add_argument('run_tid', default='1', help="tag or run ID")
    parser.set_defaults(func=main)



################################# Evaluators ##################################


class Evaluator(object):
    """A template describing how to run an evaluator."""

    def __init__(self, run_config, run_to_evaluate):
        self._config = run_config
        self._run = run_to_evaluate

    def go(self, sandbox):
        """Run an evaluator, collecting and returning the results."""
        evaluator_paths = self._config.expand_path_list('evaluation',
                                                        'evaluator')
        evaluator_path = evaluator_paths[0]

        # Reproduce the output from the run so the evaluator can look at
        # it.
        run_output_dir = os.path.join(sandbox, 'run_output')
        db.Index.extract_blob(self._run.output, run_output_dir)

        # Run the evaluator.
        result = Evaluation(self._run, sandbox)
        subprocess.call(
            [   evaluator_path,
                os.path.join(run_output_dir, 'output'),
                self._config['evaluation']['ground_truth'],
                result.output_path,
                ]
            )

        return result


class Evaluation(object):
    """Data produced by an Evaluator."""

    def __init__(self, run, sandbox):
        self._run = run
        self._sandbox = sandbox

    @property
    def run(self):
        """The run this evaluation was performed on."""
        return self._run

    @property
    def output_path(self):
        """The path to the evaluator's output data."""
        return os.path.join(self._sandbox, 'output')

    def as_mapping(self):
        """Convert self to a Mapping."""
        return {'output': self.output_path}
