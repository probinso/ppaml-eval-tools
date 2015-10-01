#!/usr/bin/python
# evil.py -- database operations                  -*- coding: us-ascii -*-
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
#import pony.orm as pny
import utility
import collections
import model as mod

## XXX: 
@mod.pny.db_session
def hash_by_team():
    for t in mod.pny.select(t for t in mod.Team):
        print '#', t, t.description
        print "mkdir -p", t.description
        for r in mod.pny.select(r for r in mod.Run if r.engine.team == t):
            if r.evaluation:
                print "cp ", "~/.local/share/ppaml/"+r.evaluation.id, t.description+'/'
                with open("CP1-2015/" + t.description + "/" + r.evaluation.id.split('.')[0]+".stats", "w+") as f:
                    f.write("duration, load_max, load_average, ram_max, ram_average\n")
                    f.write(str(r.duration)+", "+str(r.load_average)+", "+str(r.load_max)+", "+str(r.ram_average)+", "+str(r.ram_max))


@mod.pny.db_session
def cp2_hashes():
    for t in mod.pny.select(t for t in mod.Team):
        print '#', t, t.description
        for r in mod.pny.select(r for r in mod.Run if r.configured_solution.solution.challenge_problem.id == 2 and r.engine.team == t):
            fname = "workspace/CP"+str(r.configured_solution.solution.challenge_problem.id)+"-2015/"+t.description+"/"
            if r.evaluation:
                print "mkdir -p", fname
                print "cp ", utility.get_resource(r.evaluation.id), fname
                with open(fname + r.evaluation.id.split('.')[0]+".stats", "w+") as f:
                    f.write("duration, load_max, load_average, ram_max, ram_average\n")
                    f.write(str(r.duration)+", "+str(r.load_average)+", "+str(r.load_max)+", "+str(r.ram_average)+", "+str(r.ram_max))


if __name__ == "__main__":
    cp2_hashes()
