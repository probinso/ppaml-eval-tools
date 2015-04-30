#!/usr/bin/python
# driver.py -- query toy, not clean             -*- coding: us-ascii -*-
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

import datetime
import pony.orm as pny
import utility
import collections
from model import db, ChallengeProblem, Team, Dataset, Solution, Engine, ConfiguredSolution, Run, Evaluator


@pny.db_session
def print_run(pps, cps, config, ds, comment=None):
    if comment:
        print '# ', comment
    print "peval run", pps.id, cps.id, config.id, ds.in_digest, '# ', pps.team.description, " ", cps.challenge_problem.id, cps.challenge_problem.revision_major, config.filename

@pny.db_session
def thething():

    pny.select((t.id, t.description) for t in Team).show()

    divider = " :: "
    print "\n\nI AM CHECKING DATASETS \n----------------------"
    for x in pny.select(e for e in Dataset):
        for y in x.challenge_problems:
            print y, divider, x.in_digest, divider, x.eval_digest, divider, x.rel_inpath


    print 
    print
    pny.select((cp, pny.count(cp.datasets)) for cp in ChallengeProblem).show()
    print
    print
    pny.select((
        s.engine.team.description,
        s.challenge_problem.id,
        s.id
    ) for s in Solution).show()

    runs = pny.select(
      (r.id, r.configured_solution.solution, r.configured_solution, r.dataset)
      for r in Run
    )

    combos = pny.select(
        (c.solution.engine, c.solution, c, d)
        for c in ConfiguredSolution for d in Dataset
        if c.solution.challenge_problem in d.challenge_problems
    )


    [ran, unran] = utility.split_filter(
      combos,
      lambda (pps, cps, con, ds): (cps, con, ds) not in [(r[1], r[2], r[3]) for r in runs]
      )

    print
    print
    for pps, cps, con, ds in unran:
        print_run(pps, cps, con, ds)

    for pps, cps, con, ds in ran:
        print_run(
          pps, cps, con, ds,
          pps.team.description + \
          " " + \
          str(
            [(s[1], s[2], s[3]) for s in runs].count((cps, con, ds))
          )
        )

    print
    print "\n\nI AM CHECKING ENGINES \n----------------------"
    for x in pny.select(e for e in Engine):
        print x.team.description, "\t::\t", x.id
    """
    print "\n\nI AM CHECKING SOLUTIONS \n----------------------"
    for x in pny.select(s for s in Solution):
        print x.id, x.engine

    """

    print "\n\nI AM CHECKING evaluators \n----------------------"
    for x in pny.select(e for e in Evaluator):
        print x


    print "\n\nI AM RUNS configs \n----------------------"
    for x in pny.select((
            r.engine.team.description,
            r.configured_solution.solution.challenge_problem.id,
            r.duration,
            r.dataset.in_digest,
            r.output,
            r.log) for r in Run):
        print divider.join(map(str,list(x)))

if __name__ == "__main__":
    thething()
