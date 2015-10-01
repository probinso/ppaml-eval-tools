#!/usr/bin/python
# model.py -- database operations                  -*- coding: us-ascii -*-
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


from datetime import datetime
import pony.orm as pny
import os.path as osp
from . import utility

import pkgutil

DB_LOC = utility.location_resource(fname='index.db')
DBE = osp.exists(DB_LOC)

def initialize():
    import sqlite3
    connection = sqlite3.connect(DB_LOC)
    cursor = connection.cursor()
    cursor.executescript(pkgutil.get_data('peval', 'db_init.sql'))
    connection.commit()
    connection.close()
    DBE = not DBE
    del sqlite3

if not DBE:
    initialize()

db = pny.Database("sqlite", DB_LOC, create_db=False)
utility.write(DBE)

class Team(db.Entity):
    _table_ = "team"
    id = pny.PrimaryKey(int, auto=True)
    institution = pny.Required(pny.LongStr)
    description = pny.Required(pny.LongStr)
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)
    engines = pny.Set("Engine")

    @property
    def digest(self):
        return self.id


class Engine(db.Entity):
    _table_ = "engine"
    id = pny.PrimaryKey(str)
    full_path = pny.Required(pny.LongStr)
    team = pny.Required(Team)
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)
    solutions = pny.Set("Solution")
    runs = pny.Set("Run")

    @property
    def digest(self):
        return self.id


class Dataset(db.Entity):
    _table_ = "dataset"
    in_digest = pny.PrimaryKey(str)
    eval_digest = pny.Required(str)
    label = pny.Optional(pny.LongStr)
    rel_inpath = pny.Required(pny.LongStr)
    rel_evalpath = pny.Required(pny.LongStr)
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)
    challenge_problems = pny.Set("ChallengeProblem")
    runs = pny.Set("Run")

    @property
    def full_path(self):
        return osp.commonprefix(self.input_path, self.eval_path)

    @property
    def id(self):
        return self.in_digest

    @property
    def digest(self):
        return self.id


class Solution(db.Entity):
    _table_ = "solution"
    id = pny.PrimaryKey(str)
    engine = pny.Required(Engine)
    description = pny.Optional(pny.LongStr)
    challenge_problem = pny.Required("ChallengeProblem")
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)
    configurations = pny.Set("ConfiguredSolution")

    @property
    def digest(self):
        return self.id


class ChallengeProblem(db.Entity):
    _table_ = "challenge_problem"
    id = pny.Required(int)
    revision_major = pny.Required(int)
    revision_minor = pny.Required(int)
    url = pny.Optional(pny.LongStr)
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)
    solutions = pny.Set(Solution)
    datasets = pny.Set(Dataset)
    # only optional because it's not yet supported
    evaluator = pny.Optional("Evaluator")
    pny.PrimaryKey(id, revision_major, revision_minor)

    @property
    def cp_ids(self):
        return (
          self.id,
          self.revision_major,
          self.revision_major
        )


class Evaluator(db.Entity):
    _table_ = "evaluator"
    id = pny.PrimaryKey(str)
    challenge_problem = pny.Required(ChallengeProblem)
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)
    evaluations = pny.Set("Evaluation")

    @property
    def digest(self):
        return self.id


class Run(db.Entity):
    id = pny.PrimaryKey(int, auto=True)
    engine = pny.Required(Engine)
    configured_solution = pny.Required("ConfiguredSolution")
    dataset = pny.Required(Dataset)
    
    output = pny.Required(pny.LongStr)
    log = pny.Optional(pny.LongStr)
    
    started = pny.Required(datetime)
    duration = pny.Required(float)
    
    load_average = pny.Required(float)
    load_max = pny.Required(float)
    
    ram_average = pny.Required(float)
    ram_max = pny.Required(float)

    evaluation = pny.Optional("Evaluation")
    
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)

    @property
    def solution(self):
        return self.configured_solution.solution

    def recover(self, dest):
        engine_hash = self.engine.id
        solution_hash = self.solution.id
        dataset_hash = self.dataset.id
        log_hash = self.log if self.log else None
        output_hash = self.output
        utility.unpack_part(engine_hash, dest, "engine")
        utility.unpack_part(solution_hash, dest, "solution")
        utility.unpack_part(dataset_hash, dest, "input")
        if log_hash:
            utility.unpack_part(log_hash, dest, "log")
        utility.unpack_part(output_hash, dest, "output")
        return dest

    @property
    def cp_ids(self):
        return self.configured_solution.solution.challenge_problem.cp_ids

class Evaluation(db.Entity):
    _table_ = "evaluation"
    id = pny.Required(str)
    evaluator = pny.Required(Evaluator)
    run = pny.Required(Run)
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)

    pny.PrimaryKey(id, evaluator, run)

    @property
    def digest(self):
        return self.id

    @property
    def cp_ids(self):
        return self.evaluator.challenge_problem.cp_ids


class ConfiguredSolution(db.Entity):
    _table_ = "configured_solution"
    id = pny.Required(str)
    filename = pny.Required(str)
    solution = pny.Required(Solution)
    runs = pny.Set(Run)
    pny.PrimaryKey(id, solution)
    meta_created = pny.Required(datetime, default=datetime.utcnow)
    meta_updated = pny.Required(datetime, default=datetime.utcnow)

    @property
    def full_path(self):
        return osp.join(solution.full_path,self.relative_path)

    @property
    def digest(self):
        return self.id


#pny.sql_debug(True)
db.generate_mapping(check_tables=True, create_tables=false)
