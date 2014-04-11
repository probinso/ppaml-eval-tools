# static.py -- info on PPAML as a whole         -*- coding: us-ascii -*-
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

"""Information on PPAML as a whole."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import sqlalchemy

from . import db


def _cp(description, url):
    index = db.Index.open_user_index()
    result = index.ChallengeProblem()
    result.description = description
    result.revision = 1
    result.url = url
    return result

challenge_problems = {
    'cp1': _cp("Quad-Rotor Sensor Fusion",
               'http://ppaml.galois.com/wiki/wiki/CP1QuadRotor'),
    'cp2': _cp("Continent-Scale Bird Migration Modeling",
               'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration'),
    'cp3': _cp("Wide Area Motion Imagery Track Linking",
               'http://ppaml.galois.com/wiki/wiki/CP3WAMITrackLinking'),
    }


def populate_db(session, index, commit=False):
    """Populate the database with the static data."""
    for cp in challenge_problems.itervalues():
        if not index.contains(index.ChallengeProblem,
                              description=cp.description,
                              revision=cp.revision):
            session.add(cp)
            if commit:
                session.commit()
