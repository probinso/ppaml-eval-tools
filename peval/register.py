#!/usr/bin/python
# register.py -- handles registration to peval tool  -*- coding: us-ascii -*-
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
from . import model as mod
import os.path as osp
from . import utility


def register_stub(*arguments):
    print "STUB FOUND :: ", arguments

#####################################
##         LOCAL HELPERS
#####################################


def solve_cp_id(cp_id):
    ret = map(int, utility.safesplit(cp_id, '-')) + [ 0, 0, 0 ]
    return ret[:3]

"""
  I think that i need to modify the inputs to the below functions, but i am
  unsure to the most appropriate way.
"""

#####################################
##         ENGINES
#####################################
def register_engine_cli(arguments):
    eng_team_id = arguments.eng_team_id
    full_path = utility.resolve_path(arguments.eng_path)

    return register_engine(eng_team_id, full_path)


def register_engine(eng_team_id, full_path):
    with utility.TemporaryDirectory() as tmpdir:
        engine_hash, hash_path = utility.prepare_resource(full_path, tmpdir)
        if mod.DBE:
            register_engine_db(eng_team_id, engine_hash, full_path)

        utility.commit_resource(hash_path)

    return engine_hash

@mod.pny.db_session
def register_engine_db(eng_team_id, engine_hash, full_path):
    t = mod.Team.get(id=eng_team_id)
    # add safety check eng_team_id \in valid

    """
      engine_id collisions -> pony.orm.core.CommitException.IntegrityError
        UNIQUE constraint failed

      team_id wrong        -> pony.orm.core.CommitException.IntegrityError
        FOREIGN KEY constraint failed
    """
    e = mod.Engine(
      id=engine_hash,
      full_path=full_path,
      team=t
    )


def engine_subparser(subparsers):
    parser = subparsers.add_parser('engine')

    parser.add_argument('eng_team_id', type=int,
      help="your engine-team number")

    parser.add_argument('eng_path', type=str,
      help="path to engine")

    parser.set_defaults(func=register_engine_cli)


#####################################
##         DATASETS
#####################################
def register_dataset_cli(arguments):

    [major, minor, revision] = solve_cp_id(arguments.cp_id)
    rel_in   = utility.resolve_path(arguments.in_path)
    rel_eval = utility.resolve_path(arguments.eval_path)

    return register_dataset(major, minor, revision, rel_in, rel_eval)

def register_dataset(major, minor, revision, rel_in, rel_eval):
    with utility.TemporaryDirectory() as tmpdir:
        in_hash, in_hash_path = utility.prepare_resource(rel_in, tmpdir)
        # XXX PMR we will need to store these differently
        eval_hash, eval_hash_path = utility.prepare_resource(rel_eval, tmpdir)

        if mod.DBE:
            register_dataset_db(
                major, minor, revision,
                in_hash, eval_hash, rel_in, rel_eval
            )

        utility.commit_resource(in_hash_path)
        utility.commit_resource(eval_hash_path)

    return in_hash


@mod.pny.db_session
def register_dataset_db(
      major, minor, revision, in_digest, eval_digest,
      rel_in, rel_eval
    ):
    cp = mod.ChallengeProblem.get(
      id=major,
      revision_major=minor,
      revision_minor=revision)
    # how does this react if there is no match?
    if cp is None:
        raise utility.FormattedError("Challenge problem {}-{}-{} not found"
                                    , major, minor, revision)

    # we cast them to abspath at an earlier point
    full_path = osp.commonprefix([rel_in, rel_eval])

    d = mod.Dataset.get(in_digest=in_digest)
    if not d:
        d = mod.Dataset(
          in_digest=in_digest,
          eval_digest=eval_digest,
          rel_inpath=rel_in,
          rel_evalpath=rel_eval,
        )

    cp.datasets.add(d)


def dataset_subparser(subparsers):
    parser = subparsers.add_parser('dataset')

    parser.add_argument('cp_id', type=str,
      help="challenge problem id Major-Minor-Version ex: 01-00-02")

    parser.add_argument('in_path', type=str,
      help="path to input artifact")

    parser.add_argument('eval_path', type=str,
      help="path to evaluation artifact")

    parser.set_defaults(func=register_dataset_cli)


#####################################
##         SOLUTIONS
#####################################

def register_solution_cli(arguments):
    engine_hash = arguments.engine_hash
    assert(osp.exists(utility.get_resource(fname=engine_hash)))

    [major, minor, revision] = solve_cp_id(arguments.cp_id)
    full_path = utility.resolve_path(arguments.solution_path)

    def validate_config(c):
        if not osp.isfile(c):
            raise utility.FormattedError(
                "File error: '{}' is not a regular file (is it a directory perhaps?)",
                c)
        return osp.abspath(c)
    configs = [validate_config(c) for c in arguments.configs]

    return register_solution(engine_hash, full_path, major,
      minor, revision, configs)


def register_solution(engine_hash, full_path, major, minor, revision, configs):
    with utility.TemporaryDirectory() as tmpdir:
        solution_hash, solution_hash_path = \
          utility.prepare_resource(full_path, tmpdir)

        if mod.DBE:
            register_solution_db(
                engine_hash, major,
                minor, revision,
                solution_hash, configs
            )

        utility.commit_resource(solution_hash_path)

        for config in configs:
            config = utility.resolve_path(config, True)
            register_configuration(solution_hash, config)

    return solution_hash


@mod.pny.db_session
def register_solution_db(
      engine_id, major, minor,
      revision, solution_hash, configs
    ):
    e = mod.Engine.get(id=engine_id)
    cp = mod.ChallengeProblem.get(
      id=major,
      revision_major=minor,
      revision_minor=revision
    )

    s = mod.Solution(
      id=solution_hash,
      engine=e,
      challenge_problem=cp
    )

    """
    #XXX PMR : cfile located in two places is irresponsable.
    utility.write(configs)
    for cfile in configs:
        mod.ConfiguredSolution(
          id=cfile,
          solution=s
        )
    """


def solution_subparser(subparsers):
    parser = subparsers.add_parser('solution')

    parser.add_argument('engine_hash', type=str,
      help="engine's unique identifier, e.g. '80f5daa5fdda76bb774429a0f07ae1e065af9493.tar.bz2'.")

    parser.add_argument('cp_id', type=str,
      help="challenge problem id Major-Minor-Version, e.g. '01-00-02'. The challenge problem ID must already exist in the database. Edit 'db_init.sql' and update the DB as described in the README to add a new challenge problem ID.")

    parser.add_argument('solution_path', type=str,
      help="full path to solution directory.")

    parser.add_argument('configs', type=str, nargs='+',
      help="list of individual configuration files (not a directory containing configuration files) usable by solution.")

    parser.set_defaults(func=register_solution_cli)


#####################################
##         CONFIGURATIONS
#####################################

def register_configuration_cli(arguments):
    solution_hash = arguments.solution_hash
    assert(osp.exists(utility.get_resource(fname=solution_hash)))

    full_path = utility.resolve_path(arguments.config_path, True)

    return register_configuration(solution_hash, full_path)


def register_configuration(solution_hash, full_path):
    # just in case basename is a symlink, we don't want to confuse the user
    #   by changing the expected name to the realpath's basename
    basename = osp.basename(full_path)

    with utility.TemporaryDirectory() as tmpdir:
        configuration_hash, configuration_hash_path = \
          utility.prepare_resource(full_path, tmpdir, True)

        if mod.DBE:
            register_configuration_db(
                solution_hash,
                configuration_hash,
                basename
            )

        utility.commit_resource(configuration_hash_path)

    return configuration_hash


@mod.pny.db_session
def register_configuration_db(solution_id, configuration_hash, basename):
    s = mod.Solution.get(id=solution_id)

    c = mod.ConfiguredSolution(
      id=configuration_hash,
      filename=basename,
      solution=s
    )


def configuration_subparser(subparsers):
    parser = subparsers.add_parser('configuration')

    parser.add_argument('solution_hash', type=str,
      help="solution's unique identifier")

    parser.add_argument('config_path', type=str,
      help="path to configuration artifact")

    parser.set_defaults(func=register_configuration_cli)


#####################################
##         EVALUATORS
#####################################

def evaluator_subparser(subparsers):
    parser = subparsers.add_parser('evaluator')

    parser.add_argument('cp_id', type=str,
      help="challenge problem id Major-Minor-Version ex: 01-00-02")

    parser.add_argument('evaluator_path', type=str,
      help="full path to evaluator")

    parser.set_defaults(func=register_evaluator_cli)


def register_evaluator_cli(arguments):

    [major, minor, revision] = solve_cp_id(arguments.cp_id)
    full_path = utility.resolve_path(arguments.evaluator_path)

    return register_evaluator(full_path, major, minor, revision)


def register_evaluator(full_path, major, minor, revision):

    with utility.TemporaryDirectory() as tmpdir:
        evaluator_hash, evaluator_hash_path = \
          utility.prepare_resource(full_path,tmpdir)

        if mod.DBE:
            register_evaluator_db(major, minor, revision, evaluator_hash)

        utility.commit_resource(evaluator_hash_path)

    return evaluator_hash


@mod.pny.db_session
def register_evaluator_db(major, minor, revision, evaluator_hash):

    cp = mod.ChallengeProblem.get(
      id=major,
      revision_major=minor,
      revision_minor=revision
    )

    if cp.evaluator:
        utility.write("old evaluator removed!")
        cp.evaluator.delete()
        mod.pny.commit()

    e = mod.Evaluator(
      id=evaluator_hash,
      challenge_problem=cp
    )


#####################################
##         PARSERS
#####################################

def generate_parser(parser):
    subparsers = parser.add_subparsers(help="subcommand")

    # initialize subparsers
    engine_subparser(subparsers)
    solution_subparser(subparsers)
    configuration_subparser(subparsers)
    dataset_subparser(subparsers)
    evaluator_subparser(subparsers)

    return parser


