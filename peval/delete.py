#!/usr/bin/python
# delete.py -- deletes database objects for peval  -*- coding: us-ascii -*-
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

# Parameterized deletion function to reduce duplication
@mod.pny.db_session
def delete_db_parameterized(identifier,obj_getter,name,deps_finder):
    target = obj_getter(identifier)
    if not(target):
        print ("Couldn't find {} with hash \"{}\"".format(name,identifier))
        return 1

    print ("Found {}".format(target))

    deps_target = deps_finder(identifier)
    if deps_target:
      print "Deleting this will cascadingly delete the following:"
      for x in deps_target:
        print " -", x
    if utility.prompt("Would you like to delete?"):
      target.delete()
      print "Deleted!"
      return 0
    else:
      print "Aborted delete."
      return 1


#####################################
##         ENGINES
#####################################
def delete_engine_cli(arguments):
    identifier = arguments.eng_hash
    obj_getter = lambda identifier: mod.Engine.get(id=identifier)
    name = "engine"
    deps_finder = find_engine_deps
    return delete_db_parameterized(identifier,obj_getter,name,deps_finder)

def engine_subparser(subparsers):
    parser = subparsers.add_parser('engine')

    parser.add_argument('eng_hash', type=str,
      help="an engine's unique identifier")

    parser.set_defaults(func=delete_engine_cli)


#####################################
##         DATASETS
#####################################
def delete_dataset_cli(arguments):
    identifier = arguments.in_digest
    obj_getter = lambda identifier: mod.Dataset.get(in_digest=identifier)
    name = "dataset"
    deps_finder = find_dataset_deps
    return delete_db_parameterized(identifier,obj_getter,name,deps_finder)


def dataset_subparser(subparsers):
    parser = subparsers.add_parser('dataset')

    parser.add_argument('in_digest', type=str,
      help="a dataset's unique identifier")

    parser.set_defaults(func=delete_dataset_cli)


#####################################
##         SOLUTIONS
#####################################

def delete_solution_cli(arguments):
    identifier = arguments.solution_hash
    obj_getter = lambda identifier: mod.Solution.get(id=identifier)
    name = "solution"
    deps_finder = find_solution_deps
    return delete_db_parameterized(identifier,obj_getter,name,deps_finder)


def solution_subparser(subparsers):
    parser = subparsers.add_parser('solution')

    parser.add_argument('solution_hash', type=str,
      help="a solution's unique identifier")

    parser.set_defaults(func=delete_solution_cli)


#####################################
##         CONFIGURATIONS
#####################################

# XXX MAH Is it unclear to say both "configuration" & "configured_solution"?
def delete_configuration_cli(arguments):
    identifier = arguments.configuration_hash
    obj_getter = lambda identifier: mod.ConfiguredSolution.get(id=identifier)
    name = "configuration"
    deps_finder = find_configured_solution_deps
    return delete_db_parameterized(identifier,obj_getter,name,deps_finder)


def configuration_subparser(subparsers):
    parser = subparsers.add_parser('configuration')

    parser.add_argument('configuration_hash', type=str,
      help="a configuration's unique identifier")

    parser.set_defaults(func=delete_configuration_cli)


#####################################
##         EVALUATORS
#####################################

def delete_evaluator_cli(arguments):
    identifier = arguments.evaluator_hash
    obj_getter = lambda identifier: mod.Evaluator.get(id=identifier)
    name = "evaluator"
    deps_finder = find_evaluator_deps
    return delete_db_parameterized(identifier,obj_getter,name,deps_finder)

def evaluator_subparser(subparsers):
    parser = subparsers.add_parser('evaluator')

    parser.add_argument('evaluator_hash', type=str,
      help="an evaluator's unique identifier")

    parser.set_defaults(func=delete_evaluator_cli)


#####################################
##         RUNS
#####################################

def delete_run_cli(arguments):
    identifier = arguments.run_id
    obj_getter = lambda identifier: mod.Run.get(id=identifier)
    name = "run"
    deps_finder = find_run_deps
    return delete_db_parameterized(identifier,obj_getter,name,deps_finder)

def run_subparser(subparsers):
    parser = subparsers.add_parser('run')

    parser.add_argument('run_id', type=str,
      help="a run's integer identifier")

    parser.set_defaults(func=delete_run_cli)


#####################################
##      EVALUATIONS
#####################################

def delete_evaluation_cli(arguments):
    identifier = arguments.evaluation_hash
    obj_getter = lambda identifier: mod.Evaluation.get(id=identifier)
    name = "evaluation"
    # const function since nothing depends on evaluations
    deps_finder = lambda x: set()
    return delete_db_parameterized(identifier,obj_getter,name,deps_finder)

def evaluation_subparser(subparsers):
    parser = subparsers.add_parser('evaluation')

    parser.add_argument('evaluation_hash', type=str,
      help="an evaluation's unique identifier")

    parser.set_defaults(func=delete_evaluation_cli)


#####################################
##       PARSER GENERATION
#####################################

def generate_parser(parser):
    subparsers = parser.add_subparsers(help="subcommand")

    # initialize subparsers
    engine_subparser(subparsers)
    solution_subparser(subparsers)
    configuration_subparser(subparsers)
    dataset_subparser(subparsers)
    evaluator_subparser(subparsers)
    run_subparser(subparsers)
    evaluation_subparser(subparsers)

    return parser


#####################################
##   CASCADING REFERENCE FINDING
#####################################
# These functions search for all database objects which depend on
# a given object. The returned objects will be cascadingly deleted
# if the input object were deleted.
@mod.pny.db_session
def find_engine_deps(eng_hash):
    # Here we go through all of the solutions which have this engine id hash
    solution_deps = mod.Solution.select(lambda x: x.engine.id == eng_hash)
    total_deps = set(solution_deps)
    for x in solution_deps:
      total_deps |= find_solution_deps(x.id)
    return total_deps

def find_solution_deps(sol_id):
    cs_deps = mod.ConfiguredSolution.select(lambda x: x.solution.id == sol_id)
    total_deps = set(cs_deps)
    for x in cs_deps:
      total_deps |= find_configured_solution_deps(x.id)
    return total_deps

def find_configured_solution_deps(cs_id):
    run_deps = mod.Run.select(lambda x: x.configured_solution.id == cs_id)
    total_deps = set(run_deps)
    for x in run_deps:
      total_deps |= find_run_deps(x.id)
    return total_deps

def find_run_deps(run_id):
    evaluation_deps = mod.Evaluation.select(lambda x: x.run.id == run_id)
    return set(evaluation_deps)

def find_evaluator_deps(evaluator_id):
    evaluation_deps = mod.Evaluation.select(lambda x: x.evaluator.id == evaluator_id)
    return set(evaluation_deps)

def find_dataset_deps(dataset_id):
    run_deps = mod.Run.select(lambda x: x.dataset.in_digest == dataset_id)
    total_deps = set(run_deps)
    for x in run_deps:
      total_deps |= find_run_deps(x.id)
    return total_deps

