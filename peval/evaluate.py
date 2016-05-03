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
import pony.orm as pny
from . import model as mod
import os.path as osp
from . import utility
import subprocess, os, psutil


def register_stub(arguments):
    print("STUB FOUND :: ", arguments)


def evaluate_all_cli(arguments):
    unevaluated_run_ids = get_unevaluted_run_ids()
    print("Preparing to evaluate runs {}".format(list(unevaluated_run_ids)))

    exceptions = []
    for i in unevaluated_run_ids:
        print("-"*80)
        print("Evaluating run {}".format(i))
        print("-"*80)
        try:
            evaluate_single_run(i, False)
        except utility.FormattedError as e:
            exceptions.append(e)

    num_exns = len(exceptions)
    num_ran = len(unevaluated_run_ids)
    num_no_exns = num_exns - num_ran
    if num_exns != 0:
        pretty_exceptions = exceptions.join('\n')
        raise utility.FormattedError(pretty_exceptions)

    print("Evaluated {} runs. Succeeded: {}, failed: {}".format(num_ran, num_no_exns, num_exns))


@mod.pny.db_session
def get_unevaluted_run_ids():
    run_ids      = pny.select(r.id for r in mod.Run)
    eval_run_ids = pny.select(e.run.id for e in mod.Evaluation)
    return set(run_ids) - set(eval_run_ids)


def evaluate_run_cli(arguments):
    run_id = arguments.run_id
    p_flag = arguments.persist
    evaluate_single_run(run_id, p_flag)


def evaluate_single_run(run_id, p_flag):
    check_run(run_id)

    with utility.TemporaryDirectory(persist=p_flag) as sandbox:

        result_path, ground_path, input_path, eval_path, output_path = \
          hash_to_paths(run_id, sandbox)

        rc, output_path = \
          evaluate_run(result_path, ground_path, input_path, eval_path, output_path)

        out_hash, out_hash_path = \
          utility.prepare_resource(output_path, sandbox)

        if rc:
            utility.write("Evaluator returned nonzero exit code: " + str(rc))
            did_succeed = False
        else:
            did_succeed = True

        try:
            save_evaluation(run_id, out_hash, did_succeed)
        except mod.pny.core.ConstraintError as e:
            raise utility.FormattedError("Conflict : {}",  e)
        utility.commit_resource(out_hash_path)

        if rc:
            raise utility.FormattedError("Evaluator returned nonzero exit code: " + str(rc))

@mod.pny.db_session
def check_run(run_id):
    if not mod.Run.get(id=run_id):
        raise utility.FormattedError("run_id {} not valid", run_id)

@mod.pny.db_session
def save_evaluation(run_id, out_hash, did_succeed):
    r = mod.Run.get(id=run_id)
    cp = r.configured_solution.solution.challenge_problem
    ev = cp.evaluator
    if not ev:
        raise utility.FormattedError(
          "No registered evaluator for challenge problem {}",
          cp.cp_ids
        )

    evaluation = mod.Evaluation.get(run=r)
    if evaluation:
        utility.write("Old evaluation found, deleting it to save the new one.")
        evaluation.delete()
        pny.flush()
    evaluation = mod.Evaluation(
        id = out_hash,
        evaluator = ev,
        run = r,
        did_succeed = did_succeed
    )


@mod.pny.db_session
def hash_to_paths(run_id, dest):
    r = mod.Run.get(id=run_id)
    if not r:
        raise utility.FormattedError("run_id {} not valid", run_id)

    cp = r.configured_solution.solution.challenge_problem
    ev = cp.evaluator
    if not ev:
        raise utility.FormattedError(
          "No registered evaluator for challenge problem {}",
          cp.cp_ids
        )

    output_hash = r.output
    ground_hash = r.dataset.eval_digest
    input_hash  = r.dataset.in_digest
    eval_hash   = ev.id

    return utility.unpack_parts(dest,
      ('result', output_hash),
      ('ground_truth', ground_hash),
      ('input', input_hash),
      ('evaluator', eval_hash),
      ('output', None)
    )


def evaluate_run(result_path, ground_path, input_path, eval_path, output_path):

    for _, rc, _, _ in utility.process_watch(
      eval_path, ['eval.sh', result_path, ground_path, output_path]
               , INPUT_DIR=input_path
    ):
        pass

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


def all_subparser(subparsers):
    parser = subparsers.add_parser('all')
    parser.set_defaults(func=evaluate_all_cli)


def generate_parser(parser):
    subparsers = parser.add_subparsers(help="subcommand")

    # initialize subparsers
    run_subparser(subparsers)
    all_subparser(subparsers)

    return parser

