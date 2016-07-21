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
import peval.utility as utility
import collections
from peval.model import db, ChallengeProblem, Team, Dataset, Solution, Engine, ConfiguredSolution, Run, Evaluator, Evaluation


@pny.db_session
def print_run(pps, cps, config, ds, comment=None):
    print '# ', pps.team.description, " ", cps.challenge_problem.id, cps.challenge_problem.revision_major, config.filename, cps.meta_updated,
    if comment:
        print '# ', comment
    print ""
    print "peval run", pps.id, cps.id, config.id, ds.in_digest

def print_title(title):
    print
    print title
    print "################################################################"
    print

@pny.db_session
def print_teams():
    print_title("Teams")
    pny.select((t.id, t.description) for t in Team).show()

@pny.db_session
def print_datasets():
    print_title("Datasets")

    print "challenge problem :: input digest :: eval digest :: input relative path"
    print
    divider = " :: "
    for x in pny.select(e for e in Dataset):
        for y in x.challenge_problems:
            print y, divider, x.in_digest, divider, x.eval_digest, divider, x.rel_inpath

@pny.db_session
def print_solutions():
    print_title("Solutions")

    print "team :: challenge problem :: solution digest"
    print
    for tch in pny.select((
        s.engine.team.description,
        s.challenge_problem.id,
        s.id,
    ) for s in Solution):
        print "%s :: %s :: %s" % tch

@pny.db_session
def print_engines():
    print_title("Engines")

    print "team :: engine digest :: full path"
    print
    for x in pny.select(e for e in Engine):
        print "%s :: %s :: %s" % (x.team.description, x.id, x.full_path)

@pny.db_session
def print_completed_run_stats():
    print_title("Completed Run Stats")
    for fields in pny.select((
            r.engine.team.description,
            r.configured_solution.solution.challenge_problem.id,
            r.configured_solution.solution.challenge_problem.revision_major,
            r.id,
            r.configured_solution.solution.id[:8],
            r.dataset.in_digest,
            r.duration,
            r.output[:8]) for r in Run):
        print "%15s - CP%d.%d.0 { run.id: %03d, solution[:8]: %s, dataset: %s, took: %10.4f secs, ouput[:8]: %s }" % fields
        #print divider.join(map(str,list(x)))


@pny.db_session
def print_everything():
    print_teams()
    print_engines()
    print_solutions()
    print_datasets()

    #print 
    #print
    #pny.select((cp, pny.count(cp.datasets)) for cp in ChallengeProblem).show()

    runs = pny.select(
      (r.id, r.configured_solution.solution, r.configured_solution, r.dataset)
      for r in Run
    )

    combos = pny.select(
        (c.solution.engine, c.solution, c, d)
        for c in ConfiguredSolution for d in Dataset
        if c.solution.challenge_problem in d.challenge_problems
      ).order_by(lambda _e, _s, c, _d: c.meta_updated)


    [ran, unran] = utility.split_filter(
      combos,
      lambda (pps, cps, con, ds): (cps, con, ds) not in [(r[1], r[2], r[3]) for r in runs]
      )

    print_title("Run Command Lines")
    for pps, cps, con, ds in unran:
        print_run(pps, cps, con, ds)

    print_title("Completed Runs")
    for pps, cps, con, ds in ran:
        print_run(
          pps, cps, con, ds,
          " This ran " + str(
            [(s[1], s[2], s[3]) for s in runs].count((cps, con, ds))
          ) + " times."
        )

    print_completed_run_stats()

    """
    print "\n\nI AM CHECKING SOLUTIONS \n----------------------"
    for x in pny.select(s for s in Solution):
        print x.id, x.engine

    """
    """
    print "\n\nI AM CHECKING evaluators \n----------------------"
    for x in pny.select(e for e in Evaluator):
        print x


    """

    print "\n", "-"*40, "\n"
    runs = pny.select((r.id) for r in Run)
    if runs:
      print "Max run id:", max(runs)
    else:
      print "No runs yet."

    print_title("Evaluations")
    for fields in pny.select((
            e.id,
            e.run.id,
            e.meta_created) for e in Evaluation).order_by(2):
        print "%s for run %03d at %s" % fields

if __name__ == "__main__":
    print_everything()
