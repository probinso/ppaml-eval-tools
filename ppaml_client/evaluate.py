# evaluate.py -- check artifact results         -*- coding: us-ascii -*-
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

"""Run an artifact evaluator to determine how well the artifact did."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import os.path
import subprocess
import textwrap
import sys

import lockfile

from . import configuration
from . import package
from . import utility



#################################### Main #####################################


def main(arguments):
    """Run an artifact evaluator."""
    try:
        # Read and validate configuration.
        conf = configuration.read_from_file(
            arguments.run_config,
            required_fields=(('package', 'base'),
                             ('evaluation', 'evaluator'),
                             ('evaluation', 'ground_truth')),
            )
        run_name = arguments.run_name

        # Run the evaluator.
        evaluator = Evaluator(conf, run_name)
        with utility.TemporaryDirectory(prefix='ppaml.') as sandbox:
            results = _run_evaluator(evaluator, sandbox)

            # Save data.
            _package_evaluation(results, evaluator.package_dir)

    except utility.FatalError as fatal_error:
        print(textwrap.fill(str(fatal_error), width=80), file=sys.stderr)
        sys.exit(fatal_error.exit_status)


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

    except (IOError, package.InvalidPackageError,
            lockfile.AlreadyLocked) as error:
        raise utility.FatalError(error)


def _package_evaluation(evaluation, package_dir):
    """Package an evaluation."""
    evaluation = evaluation.as_mapping()
    try:
        with package.JSONPackage(package_dir) as result:
            result.record_file('evaluation', evaluation['output'])
    except (IOError, package.InvalidPackageError,
            lockfile.AlreadyLocked) as error:
        raise utility.FatalError(error)


def add_subparser(subparsers):
    """Register the 'evaluate' subcommand."""
    parser = subparsers.add_parser('evaluate', help="evaluate artifact result")
    parser.add_argument('run_config', default='run.conf',
                        help="run configuration file")
    parser.add_argument('run_name', default='001',
                        help="subdirectory with run")
    parser.set_defaults(func=main)



################################# Evaluators ##################################


class Evaluator(object):
    """A template describing how to run an evaluator."""

    def __init__(self, run_config, run_name):
        self._config = run_config
        self._run_name = run_name
        self._package_dir = os.path.join(self._config['package']['base'],
                                         _format_run_name(run_name))

    @property
    def package_dir(self):
        return self._package_dir

    def go(self, sandbox):
        """Run an evaluator, collecting and returning the results."""
        evaluator_paths = self._config.expand_path_list('evaluation',
                                                        'evaluator')
        evaluator_path = evaluator_paths[0]

        # Get the package which contains the run we're evaluating.
        with package.JSONPackage(self.package_dir) as run:

            # Run the evaluator.
            result = Evaluation(sandbox)
            subprocess.call(
                [   evaluator_path,
                    run['output'],
                    self._config['evaluation']['ground_truth'],
                    result.output_path,
                    ]
                )

            return result


def _format_run_name(name):
    """Expands a numeric run name to a zero-padded, 3-digit string."""
    try:
        return '{0:0>3}'.format(int(name))
    except ValueError:
        return name


class Evaluation(object):
    """Data produced by an Evaluator."""

    def __init__(self, sandbox):
        self._sandbox = sandbox

    @property
    def output_path(self):
        """The path to the evaluator's output data."""
        return os.path.join(self._sandbox, 'output')

    def as_mapping(self):
        """Convert self to a Mapping."""
        return {'output': self.output_path}
