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
from contextlib import nested
import errno
import math
import os
import subprocess
import time

import psutil

from . import ps as configuration
from . import db
from . import fingerprint

from . import utility


#################################### Main #####################################
def testpath(path):
    if not os.path.exists(path):
        raise utility.FormatedError("""\
          Configuration error: artifact configuration file
          "{}" is invalid""", path)
    return path

def main(arguments):
    """Run an artifact."""
    # load configuration file
    conf = configuration.CPSConfig(infile=arguments.run_config)

    # reserve fields required by this method
    conf.require_fields(
        ('identifiers', 'challenge_problem_id'),
        ('identifiers', 'dataset_label'),
        ('identifiers', 'team_id'),
        ('identifiers', 'pps_id'),
        ('identifiers', 'dataset_label'),
        ('files', 'paths'),
        ('files', 'basedir'),
        ('files', 'input')
    )

    db.print_table_info(
      team_id=conf['identifiers']['team_id'],
      pps_id=conf['identifiers']['pps_id'],
      challenge_problem_id=conf['identifiers']['challenge_problem_id']
    )

    try:
        index = db.Index.open_user_index()
    except db.SchemaMismatch as exception:
        raise utility.FatalError(exception)

    else:
        with nested(
          utility.TemporaryDirectory(
            prefix='ppaml.',
            persist=arguments.persist
          ),
          index.session()
        ) as (sandbox, session):



            artifact = index.Artifact()
            # Ensure that all challenge problems, teams, &c. are in the
            # database.

            artifact.challenge_problem_id = index.require_foreign_key(
              index.ChallengeProblem,
              challenge_problem_id=conf['identifiers']['challenge_problem_id'],
            )

            artifact.team_id = index.require_foreign_key(
               index.Team,
               team_id=conf['identifiers']['team_id'],
            )

            artifact.pps_id = index.require_foreign_key(
              index.PPS,
              pps_id=conf['identifiers']['pps_id'],
            )

            try:
                artifact.description = conf['notes']['description']
            except KeyError:
                pass

            try:
                artifact.version = conf['notes']['version']
            except KeyError:
                pass

            # In the future, we may handle compiled artifacts
            # differently than interpreted ones.  In the meantime,
            # consider all artifacts interpreted.
            artifact.interpreted = 1

            # Capture the artifact source code.
            artifact.artifact_id = db.Index.migrate(conf.expanded_files_list)

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
                    raise # this is concerning, and should be better addressed


            """
              We have successfuly recorded the source / execution files by now
            """

            # Run the artifact.
            my_run = RunProcedure(conf)
            run_data = my_run.go(sandbox, artifact.artifact_id)

            run_id = _save_run(index, session, artifact.artifact_id, conf,
                            sandbox, run_data)
            print(utility.FormatMessage("run_id #{0} saved", run_id))
            return run_id


def _save_run(index, session, artifact_id, conf, sandbox, run_result):
    """Convert a _RunResult to a index.Run and save it."""
    run = index.Run()
    run.artifact_id = artifact_id
    run.pps_id = conf['identifiers']['pps_id']
    run.environment_id = run_result.environment_id
    run.challenge_problem_id = conf['identifiers']['challenge_problem_id']
    run.team_id = conf['identifiers']['team_id']
    run.dataset_label = conf['identifiers']['dataset_label']

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
            artifact_config_path
            )
    except AttributeError:
        assert run_result.config_file_path is None

    """
      XXX : we were catching 'NOENT' OS_EXCEPTION
    """

    # output should always have content
    run.output = db.Index.migrate(utility.path_walk(run_result.output_dir))

    # it is not required that logs file/directory is populated
    try:
        run.log = db.Index.migrate(run_result.log_path)
    except db.Empty_Migrate:
        run.log = None

    # it is not required that trace file/directory is populated
    try:
        run.trace = db.Index.migrate(utility.path_walk(run_result.trace_dir))
    except db.Empty_Migrate:
        run.trace = None


    try:
        session.add(run)
        session.commit()
        return run.run_id
    except Exception as e:
        # Clear the saved data.
        for blob_id in (run.artifact_configuration, run.output, run.log,
                        run.trace):
            # We'd like to use EAFP here, but Python 2 doesn't support
            # exception chaining (see PEP 3134), so EAFP would require
            # making this its own function.  LBYL is more elegant,
            # anyway.
            if blob_id:
                db.Index.remove_blob(blob_id)
        raise e


def add_subparser(subparsers):
    """Register the 'run' subcommand."""
    parser = subparsers.add_parser('run', help="run artifact")
    parser.add_argument('run_config', default='cps.ini',
      help="run configuration file")
    parser.add_argument('-p', '--persist', action="store_true", default=False,
      help="to persist data, dont delete sandbox after use")

    parser.set_defaults(func=main)


#################################### Runs #####################################


class RunProcedure(object):
    """A template describing how to run an artifact."""

    def __init__(self, run_config):
        self._config = run_config

    def go(self, sandbox, artifact_blob):
        """Run an artifact, collecting and returning the results."""
        try:
            db.Index.extract_blob(artifact_blob,sandbox)
            return self.__go__(sandbox)

        except (configuration.MissingField, configuration.EmptyField)\
          as missing_field:
            raise utility.FormatedError("Configuration error: {0}\n{1}",
                    missing_field, "have you filled out the configuration file?")

        except IndexError:
            raise utility.FormatedError("""\
                    Configuration error: field "paths" (in section "artifact")
                    does not refer to a file.""")

        except OSError as os_error:
            error_message = "Error executing artifact: {0}".format(os_error)
            if os_error.errno == errno.EACCES:
                # No execute bit on the binary.
                error_message += ".  Is the artifact executable?"
            elif os_error.errno == errno.ENOEXEC:
                # Not a binary.
                error_message += """.  \
                    Are you sure you're specifying the artifact as the first file
                    in the "paths" field of the configuration file?"""
            raise utility.FormatedError(error_message)

    def __go__(self, sandbox):
        self._config['files']['input'] = os.path.join(
          self._config['files']['basedir'],
          self._config['files']['input']
          )
        self._config['files']['basedir'] = sandbox
        artifact_path = self._config.executable

        result = _RunResult(sandbox)

        result.environment_id = fingerprint.insert_current()

        try:
            config_file_path = self._config['files']['config']
            result.config_file_path = config_file_path
        except KeyError:
            config_file_path = os.devnull # '/dev/null'
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
                self._config['files']['input'],
                result.output_dir,
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

        rc = None # this variable is used to store process return code
        while True:

            try:
                load_sample = _sample_load(proc_entry)
                ram_sample = _sample_ram(proc_entry)
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                # Polling failed.  This probably means that we've
                # exited, but it could also mean that one of the
                # artifact's children is a zombie.
                rc = proc.poll()
                if rc is None:
                    # We have not exited yet.  Discard the samples.
                    continue
                else:
                    # We've actually exited.
                    break


            result.load_samples.append(load_sample)
            result.ram_samples.append(ram_sample)

            try:
                rc = proc_entry.wait(timeout=0.1) # seconds
            except psutil.TimeoutExpired:
                # Our timeout expired, but the process still exists.
                # Keep going.
                pass
            else:
                # The timeout didn't expire--the process exited while we
                # waited.  We're done.
                break
        result.stop_time = time.time()

        # insure that the return code of the called process is 0
        if rc != 0:
            raise utility.FormatedError(
              "Failed artifact execute: return code {}",rc)

        return result


class _RunResult(object):
    """
      A single execution of an artifact, as it exists on disk.

      Instances of this class get converted to instances of index.Run as
      appropriate.
    """

    def __init__(self, sandbox):
        self._sandbox = sandbox
        os.mkdir(self.trace_dir)

        # this violates problem description contract but happens to satisfy team
        #os.mkdir(self.output_dir)

        self.config_file_path = None
        self.start_time = None
        self.stop_time = None
        self.load_samples = []
        self.ram_samples = []

    @property
    def output_dir(self):
        """The path to the artifact's output data."""
        return os.path.join(self._sandbox, 'output' + os.path.sep)

    @property
    def log_path(self):
        """The path to the artifact's log."""
        return os.path.join(self._sandbox, 'log')

    @property
    def trace_dir(self):
        """The path to the artifact's OTF trace, if it exists."""
        return os.path.join(self._sandbox, 'trace' + os.path.sep)

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
