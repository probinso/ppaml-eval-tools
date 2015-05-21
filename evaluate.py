#!/usr/bin/python
# evaluate.py -- create a dummy configuration file  -*- coding: us-ascii -*-
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
import os.path as osp
import utility
import subprocess, os, psutil


def register_stub(arguments):
    print "STUB FOUND :: ", arguments


def evaluate_run_cli(arguments):
    run_id = arguments.run_id
    p_flag = arguments.persist

    with utility.TemporaryDirectory(persist=p_flag) as sandbox:

        result_path, ground_path, eval_path, output_path = \
          hash_to_paths(run_id, sandbox)

        rc, output_path = \
          evaluate_run(result_path, ground_path, eval_path, output_path)

        out_hash, out_hash_path = \
          utility.prepare_resource(output_path, sandbox)

        try:
            save_evaluation(run_id, out_hash)
        except mod.pny.core.ConstraintError as e:
            raise utility.FormatedError("Conflict : {}",  e)
        utility.commit_resource(out_hash_path)


@mod.pny.db_session
def save_evaluation(run_id, out_hash):
    r = mod.Run.get(id=run_id)
    if not r:
        raise utility.FormatedError("run_id {} not valid", run_id)

    ev = r.configured_solution.solution.challenge_problem.evaluator
    if not ev:
        raise utility.FormatedError(
          "No registered evaluator for challenge problem {}",
          cp.cp_ids
        )

    evaluation = mod.Evaluation(
        id = out_hash,
        evaluator = ev,
        run = r
    )


@mod.pny.db_session
def hash_to_paths(run_id, dest):
    r = mod.Run.get(id=run_id)
    if not r:
        raise utility.FormatedError("run_id {} not valid", run_id)

    ev = r.configured_solution.solution.challenge_problem.evaluator
    if not ev:
        raise utility.FormatedError(
          "No registered evaluator for challenge problem {}",
          cp.cp_ids
        )

    output_hash = r.output
    ground_hash = r.dataset.eval_digest
    eval_hash   = ev.id

    return utility.unpack_parts(dest,
      ('result', output_hash),
      ('ground_truth', ground_hash),
      ('evaluator', eval_hash),
      ('output', None)
    )


def evaluate_run(result_path, ground_path, eval_path, output_path):
    utility.test_path(eval_path)

    this_exec = utility.file_from_tree('eval.sh', eval_path)

    proc = subprocess.Popen(
        [
            this_exec,
            result_path,
            ground_path,
            output_path
        ],
        env = os.environ.copy()
    )
    proc_entry = psutil.Process(proc.pid)

    rc = None
    while True:
        rc = proc.poll()
        if rc is not None:
            break

    return rc, output_path


#####################################
##         PARSERS
#####################################

def run_subparser(subparsers):
    parser = subparsers.add_parser('run')
    parser.add_argument('run_id', type=int,
      help="this is the run_id as listed in the database")

    parser.add_argument('--persist', action='store_true', default=False,
      help="make directory persist for debugging purposes")

    parser.set_defaults(func=evaluate_run_cli)


def challenge_problem_subparser(subparsers):
    parser = subparsers.add_parser('challenge_problem')
    parser.add_argument('cp_id', type=str,
      help="challenge problem id Major-Minor-Version ex: 01-00-02")

    parser.set_defaults(func=utility.write)


def dataset_subparser(subparsers):
    parser = subparsers.add_parser('dataset')
    parser.add_argument('in_digest', type=str,
      help="Unique identifier for the input dataset")

    parser.set_defaults(func=utility.write)


def generate_parser(parser):
    subparsers = parser.add_subparsers(help="subcommand")

    # initialize subparsers
    run_subparser(subparsers)
    # challenge_problem_subparser(subparsers)
    # dataset_subparser(subparsers)

    return parser


def main():
    parser = argparse.ArgumentParser()
    arguments = generate_parser(parser).parse_args()
    sys.exit(arguments.func(arguments))


if __name__ == "__main__":
    main()
