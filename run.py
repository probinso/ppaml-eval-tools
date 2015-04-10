#!/usr/bin/python
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


import argparse
import sys
import model as mod
import os.path as osp
import os, psutil, subprocess
import time
import utility
from datetime import datetime


def valid_params(*args):
    if None in args:
        raise utility.FormatedError("Invalid input parameter",*args)


def run_solution_cli(arguments):
    engine_id, solution_id, dataset_id =\
      arguments.engine, arguments.solution, arguments.dataset
    valid_params(engine_id, solution_id, dataset_id)

    p_flag = arguments.persist

    with utility.TemporaryDirectory(prefix='ppaml.', persist=p_flag) as sandbox:
        engroot, solpath, configpaths, datapath, outpath, logpath =\
          hash_to_paths(
            sandbox, engine_id,
            solution_id, dataset_id
          )

        for config_id in configpaths:
            configpath = config_id if osp.abspath(config_id) else osp.join(solpath, config_id)
            rc, ram, load, time =\
              run_solution(
                engroot, solpath,
                configpath,
                datapath, outpath, logpath)

            if rc != 0:
                utility.failed_run()
                raise utility.FormatedError("solution execuution crashed")

            if osp.exists(logpath):
                log_hash, log_hash_path = utility.prepare_resource(logpath, sandbox)
            else:
                log_hash, log_hash_path = None, None
        
            out_hash, out_hash_path = utility.prepare_resource(outpath, sandbox)
            save_run(
              engine_id, solution_id, config_id, dataset_id,
              out_hash, log_hash, time, load, ram
            )

            if log_hash:
                utility.commit_resource(log_hash_path)

            utility.commit_resource(out_hash_path)


def hash_to_paths(dest, engine_hash, solution_hash, dataset_hash):
    """
    """
    eng_path = utility.unpack_part(engine_hash, dest, "engine")
    sol_path = utility.unpack_part(solution_hash, dest, "solution")
    inp_path = utility.unpack_part(dataset_hash, dest, "input")

    config_labels = retrieve_configurations(solution_hash)
    config_paths = map(lambda x: utility.unpack_part(x, dest), config_labels)
    """
    if not osp.isabs(config_label):
        config_label = osp.join(sol_path, config_label)
    """

    new_path = lambda x: osp.join(osp.realpath(dest), x)
    out_path = new_path("output")
    log_file = new_path("log")

    return eng_path, sol_path, config_labels, inp_path, out_path, log_file


"""
  process helpers, likely to be moved to a different file
"""
def sum_for_process_children(function, proc):
    return function(proc) +\
      sum(function(child) for child in proc.get_children(recursive=True))

def sample_ram(proc):
    def get_ram_usage(process):
        return process.get_memory_info().vms >> 10 # bytes -> KiB
    return sum_for_process_children(get_ram_usage, proc)

def sample_load(proc):
    def get_cpu_usage(process):
        return 0.01 * psutil.Process.get_cpu_percent(process)
    return sum_for_process_children(get_cpu_usage, proc)
"""
  end process helpers
"""


def run_solution(engroot, solpath, configpath, datasetpath, outputdir, logfile):
    """
      all input parameters must be valid paths
    """

    utility.test_path(solpath)
    os.chdir(solpath)

    this_exec = utility.file_from_tree('run.sh', solpath)

    start_t = time.time()

    # setup environment variables
    proc_env = os.environ.copy()
    proc_env['ENGROOT'] = engroot

    # define process
    proc = subprocess.Popen(
      [
        this_exec, configpath,
        datasetpath, outputdir,
        logfile,
      ],
    env=proc_env
    )

    proc_entry = psutil.Process(proc.pid)

    ram_samples = []
    load_samples = []
    rc = None

    while True:
        try:
            curr_load_sample = sample_load(proc_entry)
            curr_ram_sample  = sample_ram(proc_entry)
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

        load_samples.append(curr_load_sample)
        ram_samples.append(curr_ram_sample)

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
    end_t = time.time()

    # insure that the return code of the called process is 0
    # assert(rc == 0)
    maxavg = lambda li: (max(li), sum(li)/len(li))

    return rc,\
      maxavg(ram_samples),\
      maxavg(load_samples),\
      (start_t, end_t)


@mod.pny.db_session
def retrieve_configurations(solution_id):
    s = mod.Solution.get(id=solution_id)
    cs = [c.id.encode('ascii') for c in s.configurations]
    return cs


@mod.pny.db_session
def save_run(
      engine_id, solution_id, config_label, dataset_id,
      output_hash, log_hash, time_info, load_info, ram_info
    ):

    e = mod.Engine.get(id=engine_id)
    s = mod.Solution.get(id=solution_id)

    cs = mod.ConfiguredSolution.get(
      solution = s,
      id = config_label
    )

    d = mod.Dataset.get(in_digest=dataset_id)

    r = mod.Run(
      engine = e, configured_solution = cs, dataset = d,
      output = output_hash,
      started = datetime.fromtimestamp(time_info[0]).strftime(
        '%Y-%m-%d %H:%M:%S'
      ),
      duration = time_info[1] - time_info[0],

      load_average = load_info[0],
      load_max = load_info[1],

      ram_average = ram_info[0],
      ram_max = ram_info[1]
    )

    if log_hash:
        r.log_id = log_hash


def generate_parser(parser):

    parser.add_argument('engine', type=str,
      help="hash engine identifier to be used as engine for solution")

    parser.add_argument('solution', type=str,
      help="hash solution identifier to be used as engine for solution")

    """
    parser.add_argument('config', type=str,
      help="hash configuration identifier to be used for solution")
    """
    parser.add_argument('dataset', type=str,
      help="dataset to run solution over")

    parser.add_argument('--persist', action='store_true', default=False,
      help="make directory persist for debugging purposes")

    parser.set_defaults(func=run_solution_cli)

    return parser


def main():
    if not mod.DBE:
        utility.write("NO DATABASE PRESENT")

    parser = argparse.ArgumentParser()
    arguments = generate_parser(parser).parse_args()
    sys.exit(arguments.func(arguments))


if __name__ == "__main__":
    main()
