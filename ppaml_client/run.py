# run.py -- artifact run                        -*- coding: us-ascii -*-
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

"""Run an artifact."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import array
import contextlib
import errno
import math
import os
import subprocess
import time
import textwrap

import psutil

from . import configuration
from . import db
from . import fingerprint
from . import static
from . import utility



#################################### Main #####################################
def testpath(path):
    if not os.path.exists(path):
        raise utility.FatalError(textwrap.fill(
          textwrap.dedent("""\
          Configuration error: artifact configuration file
          "{}" is invalid""".format(path)), 80))
    return path

def main(arguments):
    """Run an artifact."""
    # Read and validate configuration.
    conf = configuration.read_from_file(
        arguments.run_config,
        required_fields=(('problem', 'challenge_problem_id'),
                         ('problem', 'team_id'),
                         ('problem', 'pps_id'),
                         ('artifact', 'paths'),
                         ('artifact', 'input')),
        )
    try:
        artifact_config_path = conf['artifact']['config']
        artifact_input_path = conf['artifact']['input']
    except KeyError:
        # No configuration file specified, so we'll end up using
        # /dev/null.  No big deal.
        pass
    else:
        testpath(artifact_config_path)
        testpath(artifact_input_path)

    # Register the artifact.
    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)

    else:
        with contextlib.nested(utility.TemporaryDirectory(prefix='ppaml.'),
                               index.session()) as (sandbox, session):
            artifact = index.Artifact()

            # Ensure that all challenge problems, teams, &c. are in the
            # database.
            static.populate_db(session, index, commit=True)

            artifact.challenge_problem_id = index.require_foreign_key(
                index.ChallengeProblem,
                challenge_problem_id=conf['problem']['challenge_problem_id'],
                )

            artifact.team_id = index.require_foreign_key(
                index.Team,
                team_id=conf['problem']['team_id'],
                )

            artifact.pps_id = index.require_foreign_key(
                index.PPS,
                pps_id=conf['problem']['pps_id'],
                )

            try:
                artifact.description = conf['artifact']['description']
            except KeyError:
                pass

            try:
                artifact.version = conf['artifact']['version']
            except KeyError:
                pass

            # In the future, we may handle compiled artifacts
            # differently than interpreted ones.  In the meantime,
            # consider all artifacts interpreted.
            artifact.interpreted = 1

            # Capture the artifact source code.
            # XXX: DOES NOT CHECK PATH EXISTANCE, and sqashes NONEXISTANT PATHS
            artifact.artifact_id = db.Index.migrate(
                conf.expand_path_list('artifact', 'paths'),
                conf.base_dir
                )

            # Insert the artifact into the database.
            if index.contains(
                    index.Artifact,
                    artifact_id=artifact.artifact_id,
                    ):
                # We've already captured this artifact; we don't need to
                # insert a new row into the database.
                pass
            else:
                try:
                    session.add(artifact)
                    session.commit()
                except Exception:
                    db.Index.remove_blob(artifact.artifact_id)
                    raise

            # Run the artifact.
            run_data = _run_artifact(RunProcedure(conf), sandbox)

            # Save the run in the database.
            print(_save_run(index, session, artifact.artifact_id, conf,
                            sandbox, run_data))


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


def _save_run(index, session, artifact_id, conf, sandbox, run_result):
    """Convert a _RunResult to a index.Run and save it."""
    run = index.Run()
    run.artifact_id = artifact_id
    run.pps_id = conf['problem']['pps_id']
    run.environment_id = run_result.environment_id
    run.challenge_problem_id = conf['problem']['challenge_problem_id']
    run.team_id = conf['problem']['team_id']

    run.started = long(run_result.start_time)
    run.duration = run_result.runtime
    run.load_average = run_result.load_average
    run.load_max = run_result.load_max
    run.ram_average = long(run_result.ram_average) * 1024
    run.ram_max = long(run_result.ram_max) * 1024

    # Save the artifact configuration.
    try:
        artifact_config_path = os.path.abspath(run_result.config_file_path)
        run.artifact_configuration = db.Index.migrate(
            (artifact_config_path,),
            _deepest_common_component((artifact_config_path,)),
            )
    except AttributeError:
        assert run_result.config_file_path is None

    # Save the artifact output, log, and trace.
    def save(paths, strip_prefix):
        try:
            return db.Index.migrate(paths, strip_prefix)
        except OSError as os_error:
            if os_error.errno == errno.ENOENT:
                # The artifact didn't produce this datum.
                return None
            else:
                raise
    run.output = save([run_result.output_path], sandbox)
    run.log = save([run_result.log_path], sandbox)
    run.trace = save(
        [os.path.join(run_result.trace_dir, p)
         for p in os.listdir(run_result.trace_dir)],
        run_result.trace_dir,
        )

    try:
        session.add(run)
        session.commit()
        return run.run_id
    except Exception:
        # Clear the saved data.
        for blob_id in (run.artifact_configuration, run.output, run.log,
                        run.trace):
            # We'd like to use EAFP here, but Python 2 doesn't support
            # exception chaining (see PEP 3134), so EAFP would require
            # making this its own function.  LBYL is more elegant,
            # anyway.
            if blob_id:
                db.Index.remove_blob(blob_id)
        raise


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

        result = _RunResult(sandbox)
        result.environment_id = fingerprint.insert_current()
        try:
            config_file_path = self._config['artifact']['config']
            result.config_file_path = config_file_path
        except KeyError:
            config_file_path = '/dev/null' #TODO: LOOK AT THIS
            result.config_file_path = None

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


class _RunResult(object):
    """A single execution of an artifact, as it exists on disk.

    Instances of this class get converted to instances of index.Run as
    appropriate.

    """

    def __init__(self, sandbox):
        self._sandbox = sandbox
        os.mkdir(self.trace_dir)

        self.config_file_path = None
        self.start_time = None
        self.stop_time = None
        self.load_samples = []
        self.ram_samples = []

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



############################### Utility ################################


def _favg(sequence):
    """Averages a sequence of floats."""
    return math.fsum(sequence) / len(sequence)


def _deepest_common_component(paths):
    """Find the deepest parent directory of a sequence of paths.

    This algorithm is entirely syntactic, so it will likely be confused
    by links and other file system features.  It should, however, work
    on non-Unix systems.

    """
    paths = list(paths)

    # Get rid of any files; use only directories.
    for i in xrange(len(paths)):
        paths[i] = os.path.abspath(paths[i])
        if not os.path.isdir(paths[i]):
            paths[i] = os.path.dirname(paths[i])

    result = os.sep.join(
        os.path.commonprefix([path.split(os.sep) for path in paths]),
        )
    return result if result else os.sep
