# run.py -- artifact run                        -*- coding: us-ascii -*-
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

"""Run an artifact."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import array
import errno
import hashlib
import math
import os
import subprocess
import sys
import time
import textwrap

import lockfile
import psutil

from . import configuration
from . import Fingerprint
from . import package
from . import utility



#################################### Main #####################################


def main(arguments):
    """Run an artifact."""
    try:
        # Read and validate configuration.
        conf = configuration.read_from_file(
            arguments.run_config,
            required_fields=(('artifact', 'paths'),
                             ('artifact', 'input'),
                             ('package', 'base')),
            )

        # Run the artifact.
        run_procedure = RunProcedure(conf)
        with utility.TemporaryDirectory(prefix='ppaml.') as sandbox:
            run_data = _run_artifact(run_procedure, sandbox)

            # Create a space to save the data.
            package_dir = _make_next_available_directory(
                conf['package']['base'],
                )

            # Save it.
            _package_run(run_data, package_dir)

            # Tell the user.
            print("{0}".format(package_dir))

    except utility.FatalError as fatal_error:
        print(textwrap.fill(str(fatal_error), width=80), file=sys.stderr)
        sys.exit(fatal_error.exit_status)


def _run_artifact(run_procedure, sandbox):
    """Run the artifact."""
    try:
        return run_procedure.go(sandbox)

    except (configuration.MissingField,
            configuration.EmptyField) as missing_field:
        raise utility.FatalError("Configuration error: {0}".format(
                missing_field,
                ),
                                 10)

    except IndexError:
        raise utility.FatalError(
            textwrap.dedent("""\
                Configuration error: field "paths" (in section "artifact")
                does not refer to a file."""),
            10,
            )

    except OSError as os_error:
        error_message = "Error executing artifact: {0}".format(os_error)
        if os_error.errno == errno.EACCES:
            # No execute bit on the binary.
            error_message += ".  Is the artifact executable?"
        elif os_error.errno == errno.ENOEXEC:
            # Not a binary.
            error_message += textwrap.dedent(""".  \
                Are you sure you're specifying the artifact as the first file
                in the "paths" field of the configuration file?""")
        raise utility.FatalError(error_message, 10)


def _package_run(run_data, package_dir):
    """Package a run."""
    run_data = run_data.as_mapping()
    try:
        with package.JSONPackage(package_dir) as result:
            for key in run_data:
                if key in ('artifact_config', 'output', 'log', 'trace'):
                    result.record_file(key, run_data[key])
                else:
                    result.record_data(key, run_data[key])

    except (IOError, package.InvalidPackageError,
            lockfile.AlreadyLocked) as error:
        raise utility.FatalError(error)


def add_subparser(subparsers):
    """Register the 'run' subcommand."""
    parser = subparsers.add_parser('run', help="run artifact")
    parser.add_argument('run_config', default='run.conf',
                        help="run configuration file")
    parser.set_defaults(func=main)



#################################### Runs #####################################


class RunProcedure(object):
    """A template describing how to run an artifact."""

    def __init__(self, run_config):
        self._config = run_config

    def go(self, sandbox):
        """Run an artifact, collecting and returning the results."""
        artifact_paths = self._config.expand_path_list('artifact', 'paths')
        artifact_path = artifact_paths[0]

        result = Run(sandbox)
        result.machine = Fingerprint.current()
        try:
            config_file_path = self._config['artifact']['config']
            result.config_file_path = config_file_path
        except KeyError:
            config_file_path = '/dev/null'
            result.config_file_path = None
        result.identify_artifact(artifact_paths)

        # Stick the tracer path into the environment.
        proc_env = os.environ.copy()
        proc_env['PPAMLTRACER_TRACE_BASE'] = os.path.join(result.trace_dir,
                                                          'trace')

        # Start the artifact running.
        result.start_time = time.time()
        proc = subprocess.Popen(
            [   artifact_path,
                config_file_path,
                self._config['artifact']['input'],
                result.output_path,
                result.log_path,
                ],
            env=proc_env,
            )

        # Poll for CPU and RAM usage.
        # Load samples will always be relatively small floating-point
        # values, so store them in an array.array of doubles.
        result.load_samples = array.array('d')
        # RAM samples are a bit of a different story--they're in kiB,
        # which means the maximum storable in an array.array of unsigned
        # long is 2^32 == 4294967296, or exactly 4 TiB.  Given that even
        # small labs can now purchase machines with 1 TiB, assuming that
        # no machine will ever host >4 TiB is dangerous.  Use a list
        # instead--it will transparently support longs when they become
        # necessary.
        result.ram_samples = []
        # Precache the handle to the process's /proc entry.  This should
        # help disturb the environment as little as possible during the
        # sampling.
        proc_entry = psutil.Process(proc.pid)
        while True:
            try:
                load_sample = _sample_load(proc_entry)
                ram_sample = _sample_ram(proc_entry)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                # Polling failed.  This probably means that we've
                # exited, but it could also mean that one of the
                # artifact's children is a zombie.
                if proc.poll() is None:
                    # We have not exited yet.  Discard the samples.
                    continue
                else:
                    # We've actually exited.
                    break
            result.load_samples.append(load_sample)
            result.ram_samples.append(ram_sample)
            try:
                proc_entry.wait(timeout=0.1) # seconds
            except psutil.TimeoutExpired:
                # Our timeout expired, but the process still exists.
                # Keep going.
                pass
            else:
                # The timeout didn't expire--the process exited while we
                # waited.  We're done.
                break
        result.stop_time = time.time()

        return result


def _sample_load(proc):
    """Return CPU used by the process and its descendants."""
    return 0.01 * _for_process_and_descendants(
                      psutil.Process.get_cpu_percent,
                      proc,
                      )


def _sample_ram(proc):
    """Bytes of virt used by the process and its descendants."""
    def get_ram(process):
        return process.get_memory_info().vms
    return _for_process_and_descendants(get_ram, proc) >> 10 # bytes -> KiB


def _for_process_and_descendants(function, proc):
    """Sums a function over an entire process tree."""
    return (function(proc) +
            sum(function(child)
                for child in proc.get_children(recursive=True)))


class Run(object):
    """A single execution of an artifact."""

    def __init__(self, sandbox):
        self._sandbox = sandbox
        os.mkdir(self.trace_dir)

        self._artifact_id = None
        self.machine = None
        self.config_file_path = None
        self.start_time = None
        self.stop_time = None
        self.load_samples = []
        self.ram_samples = []

    @property
    def artifact_id(self):
        """A unique identifier (a Sequence) for this artifact."""
        return self._artifact_id

    def identify_artifact(self, paths):
        """Compute and set the unique identifier for this artifact."""
        # Currently, the identifier is the MD5 sum of all the paths
        # concatenated together.  These are just bytes, so use an array
        # to hold them.
        data = array.array('c')
        for file_path in paths:
            with open(file_path, 'rb') as file_:
                data.extend(file_.read())
        self._artifact_id = hashlib.md5(data).hexdigest()

    @property
    def start_time_human(self):
        """The time the run started, in human-readable format."""
        # Passing None to time.localtime returns the current time, not a
        # TypeError, so we need to use LBYL here.
        if self.start_time:
            return time.strftime('%a %b %d %H:%M:%S %Z %Y',
                                 time.localtime(self.start_time))
        else:
            return None

    @property
    def output_path(self):
        """The path to the artifact's output data."""
        return os.path.join(self._sandbox, 'output')

    @property
    def log_path(self):
        """The path to the artifact's log."""
        return os.path.join(self._sandbox, 'log')

    @property
    def trace_dir(self):
        """The path to the artifact's OTF trace, if it exists."""
        return os.path.join(self._sandbox, 'trace')

    @property
    def runtime(self):
        """The total runtime in seconds."""
        return self.stop_time - self.start_time

    @property
    def load_average(self):
        """The artifact load average during the run.

        Artifact load is not the same as system load--it is the load
        from the artifact and all its descendants.

        """
        return _favg(self.load_samples)

    @property
    def load_max(self):
        """The artifact load maximum during the run.

        Artifact load is not the same as system load--it is the load
        from the artifact and all its descendants.

        """
        return max(self.load_samples)

    @property
    def ram_average(self):
        """The average artifact RAM usage during the run, in kiB.

        This property reflects the RAM usage of the artifact and all its
        descendants.

        """
        return _favg(self.ram_samples)

    @property
    def ram_max(self):
        """The maximum artifact RAM usage during the run, in kiB.

        This property reflects the RAM usage of the artifact and all its
        descendants.

        """
        return max(self.ram_samples)

    def as_mapping(self):
        """Convert self to a Mapping."""
        result =  {'artifact_id': self.artifact_id,
                   'artifact_config': self.config_file_path,
                   'start_time': self.start_time,
                   'start_time_human': self.start_time_human,
                   'runtime': self.runtime,
                   'load_average': self.load_average,
                   'load_max': self.load_max,
                   'ram_kib_average': self.ram_average,
                   'ram_kib_max': self.ram_max,
                   'machine': self.machine,
                   }

        # Before adding the output, log, and trace paths to the mapping,
        # ensure that there's something actually there.
        if os.path.exists(self.output_path):
            result['output'] = self.output_path
        if os.path.exists(self.log_path):
            result['log'] = self.log_path
        if os.listdir(self.trace_dir):
            result['trace'] = self.trace_dir

        return result



################################### Utility ###################################


def _make_next_available_directory(base_path):
    """Creates the next suitable directory in a list.

    Given a directory tree like

        base_path
        |-- 001
        |-- 002
        `-- 003

    this function creates a directory with the next number to use for a
    subdirectory, returning the path to that directory.  In this
    example, it would return 'base_path/004'.  However, this function
    tries very, very hard not to fail or do anything unexpected, even if
    the user has messed quite a bit with the numbers, inserted other
    directories, or otherwise wrecked the nice sequential-directory
    invariant displayed above.

    """
    # Get the directories that already exist.
    try:
        dirs = os.listdir(base_path)
    except OSError as os_error:
        if os_error.errno == errno.ENOENT:
            # The directory doesn't exist yet.
            os.mkdir(base_path)
            dirs = ()
        else:
            raise

    # Find the maximum-numbered one.
    def target_path(n):
        return os.path.join(base_path, '{0:0>3}'.format(n))
    try:
        max_dir = max(int(number) for number in dirs if number.isdigit())
    except ValueError:
        max_dir = 0

    # Increment and create the new directory.
    next_number = max_dir + 1
    while True:
        try:
            os.mkdir(target_path(next_number))
        except OSError as os_error:
            if os_error.errno == errno.EEXIST:
                # Somebody got there before us.
                next_number += 1
                continue
            else:
                raise
        else:
            break
    return target_path(next_number)


def _favg(sequence):
    """Averages a sequence of floats."""
    return math.fsum(sequence) / len(sequence)
