-- db_init.sql -- set up a PPAML database
-- Copyright © 2014 Galois, Inc.
--
-- Redistribution and use in source and binary forms, with or without
-- modification, are permitted provided that the following conditions are met:
--   1. Redistributions of source code must retain the above copyright notice,
--      this list of conditions and the following disclaimer.
--   2. Redistributions in binary form must reproduce the above copyright
--      notice, this list of conditions and the following disclaimer in the
--      documentation and/or other materials provided with the distribution.
--   3. Neither Galois's name nor the names of other contributors may be used
--      to endorse or promote products derived from this software without
--      specific prior written permission.
--
-- THIS SOFTWARE IS PROVIDED BY GALOIS AND OTHER CONTRIBUTORS AS IS AND ANY
-- EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
-- WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
-- DISCLAIMED.  IN NO EVENT SHALL GALOIS OR OTHER CONTRIBUTORS BE LIABLE FOR
-- ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
-- DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
-- SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
-- CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
-- LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
-- OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
-- DAMAGE.
--
--
-- This SQL schema is written in as close to standard SQL as is possible, but
-- when necessary, I've foregone portability in favor of functionality with
-- SQLite.  Specific fields and pragmas compatible only with SQLite are tagged
-- '[sqlite]'.

-- [sqlite] Set the application_id field in the SQLite database header to
-- something other than its default, so file(1) knows this isn't just some
-- random SQLite database.
PRAGMA application_id = 3430079183; -- 0xCC72DACF

-- [sqlite] SQLite provides a nice database header to associate human-readable
-- version information with the schema.
PRAGMA user_version = 8;

PRAGMA foreign_keys = ON;

CREATE TABLE challenge_problem (
  id INTEGER NOT NULL,
  description TEXT NOT NULL,
  revision_major INTEGER NOT NULL,
  revision_minor INTEGER NOT NULL,
  url TEXT NOT NULL,

  -- current_evaluator TEXT REFERENCES evaluator(evaluator_id) DEFAULT NULL,
  -- could be checked by providing unique id_structure and asking for most
  -- recent from evaluator, but is harder... this acs as a curtousy line.
/*
  add trigger such that when an evaluator that gives a challenge_problem
  identification replaces this entry.

  This is to insure that we can support old evaluators over new
  challenge_problem(s) assuming the only thing that has changed is input
  dataset. (because we are using digest as our identifier, and likey should)
*/

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  evaluator INTEGER REFERENCES evaluator (id) ON DELETE CASCADE DEFAULT NULL,
  PRIMARY KEY (id, revision_major, revision_minor)
);


CREATE TABLE evaluator (
  id TEXT NOT NULL PRIMARY KEY,
  challenge_problem_id INTEGER NOT NULL,
  challenge_problem_revision_major INTEGER NOT NULL,
  challenge_problem_revision_minor INTEGER NOT NULL,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (
    challenge_problem_id,
    challenge_problem_revision_major,
    challenge_problem_revision_minor
  ) REFERENCES challenge_problem (
    id,
    revision_major,
    revision_minor
  ) ON DELETE CASCADE
);

-- STUB
INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(0, 'galois-stub', 0, 0,
    'https://ppaml.galois.com');


--SLAM
INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(1, 'SLAM WITH GPS WITHOUT OBSTICALS', 0, 0,
    'http://ppaml.galois.com/wiki/wiki/CP1QuadRotor');

INSERT INTO
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(1, 'SLAM WITHOUT GPS WITH OBSTICALS', 0, 1,
    'http://ppaml.galois.com/wiki/wiki/CP1QuadRotor');


--BIRDS
INSERT INTO
-- ALL DATASETS, THIS IS RESERVERD FOR SOLUTIONS THAT ARE NOT SEPERABLE
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'ALL BIRDS', 0, 0,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');

INSERT INTO
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'ONE BIRD', 1, 0,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');

INSERT INTO
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'THOUSANDS OF BIRDS', 2, 0,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');

INSERT INTO
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'MILLIONS OF BIRDS', 3, 0,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');


INSERT INTO
-- ALL DATASETS, THIS IS RESERVERD FOR SOLUTIONS THAT ARE NOT SEPERABLE
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'ALL BIRDS', 0, 1,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');

INSERT INTO
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'ONE BIRD', 1, 1,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');

INSERT INTO
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'THOUSANDS OF BIRDS', 2, 1,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');

INSERT INTO
  'challenge_problem' ( 'id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(2, 'MILLIONS OF BIRDS', 3, 1,
    'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration');


-- CP4 Mini Challenge Problems
INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Bayesian Linear Regression', 1, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem1');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Disease Diagnosis', 2, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem2');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Discrete-time Discrete-observate HHM', 3, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem3');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'HDP-LDA Topic Model', 4, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem4');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'PCFG Sentence Completion', 5, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem5');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Network Analysis Expressiveness Challenge', 6, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem6');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Friends and Smokers', 7, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem7');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Seismic 2-D', 8, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem8');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Recursive Reasoning: Scalar Implicature', 9, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem9');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(4, 'Lifted Inference', 10, 0,
    'https://github.com/GaloisInc/ppaml-cp4/tree/master/problems/problem10');


-- PCFG
INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(5, 'Probabilistic Context-Free-Grammar without Latent Annotation', 0, 0,
    'https://github.com/GaloisInc/ppaml-cp5');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(5, 'Probabilistic Context-Free-Grammar with Latent Annotation', 1, 0,
    'https://github.com/GaloisInc/ppaml-cp5');


-- CRF
INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(6, 'Conditional random fields', 0, 0,
    'https://github.com/GaloisInc/ppaml-cp6');

INSERT INTO
  'challenge_problem' ('id', 'description', 'revision_major',
  'revision_minor', 'url')
  VALUES(6, 'Conditional random fields with images tagged "structure"', 1, 0,
    'https://github.com/GaloisInc/ppaml-cp6');


/*
CREATE TABLE environment (
  environment_id INTEGER PRIMARY KEY AUTOINCREMENT,

  hardware_id NOT NULL REFERENCES hardware(hardware_id) ON DELETE CASCADE,
  software_id NOT NULL REFERENCES software(software_id) ON DELETE CASCADE,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
  );


CREATE TABLE hardware (
  hardware_id INTEGER PRIMARY KEY AUTOINCREMENT, -- [sqlite]

  description TEXT,
  cpu_family INTEGER,
  cpu_model INTEGER,
  cpu_model_name TEXT,
  cpu_stepping INTEGER,
  cpu_microcode INTEGER,
  cpu_n_cores INTEGER CHECK (cpu_n_cores > 0),
  cpu_n_threads INTEGER CHECK (cpu_n_threads > 0),
  cpu_cache BIGINT CHECK (cpu_cache > 0),
  cpu_clock REAL CHECK (cpu_clock > 0),

  ram BIGINT CHECK (ram > 0),

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );


CREATE TABLE software (
  software_id INTEGER PRIMARY KEY AUTOINCREMENT, -- [sqlite]

  description TEXT,
  kernel TEXT NOT NULL, -- e.g., "Linux"
  kernel_version TEXT,
  userland TEXT,  -- e.g., "GNU", "Darwin"
  hostname TEXT NOT NULL,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  );
*/


CREATE TABLE team (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  institution TEXT NOT NULL,
  description TEXT NOT NULL,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


INSERT INTO --this numbering order is preserved from the previous generation
  'team' ('id', 'institution', 'description')
  VALUES(1, 'Galois', 'Integrator');
INSERT INTO
  'team' ('id', 'institution', 'description')
  VALUES(3, 'BAE', 'gamble');
INSERT INTO
  'team' ('id', 'institution', 'description')
  VALUES(4, 'Charles River Analytics', 'BLOG');
INSERT INTO
  'team' ('id', 'institution', 'description')
  VALUES(5, 'Gamelan Labs', '{CH,D}imple');
INSERT INTO
  'team' ('id', 'institution', 'description')
  VALUES(6, 'Indiana University', 'Hakaru');
INSERT INTO
  'team' ('id', 'institution', 'description')
  VALUES(7, 'MIT', 'Venture');
INSERT INTO
  'team' ('id', 'institution', 'description')
  VALUES(12, 'Charles River Analytics', 'Figaro');


CREATE TABLE engine (
  id TEXT NOT NULL PRIMARY KEY,
  full_path TEXT NOT NULL,
  team INTEGER NOT NULL REFERENCES team (id) ON DELETE CASCADE,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE dataset (
  in_digest TEXT NOT NULL PRIMARY KEY,
  eval_digest TEXT NOT NULL,
  label TEXT,
  rel_inpath TEXT NOT NULL,
  rel_evalpath TEXT NOT NULL,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE ChallengeProblem_Dataset (
  challengeproblem_id INTEGER NOT NULL,
  challengeproblem_revision_major INTEGER NOT NULL,
  challengeproblem_revision_minor INTEGER NOT NULL,
  dataset TEXT NOT NULL REFERENCES dataset (in_digest) ON DELETE CASCADE,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (
    challengeproblem_id,
    challengeproblem_revision_major,
    challengeproblem_revision_minor,
    dataset
  ),

  FOREIGN KEY (
    challengeproblem_id,
    challengeproblem_revision_major,
    challengeproblem_revision_minor
  ) REFERENCES challenge_problem (
    id,
    revision_major,
    revision_minor
  ) ON DELETE CASCADE
);


CREATE TABLE solution (
  id TEXT NOT NULL PRIMARY KEY,
  engine TEXT NOT NULL REFERENCES engine (id) ON DELETE CASCADE,

  description TEXT,

  challenge_problem_id INTEGER NOT NULL,
  challenge_problem_revision_major INTEGER NOT NULL,
  challenge_problem_revision_minor INTEGER NOT NULL,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (
    challenge_problem_id,
    challenge_problem_revision_major,
    challenge_problem_revision_minor
  ) REFERENCES challenge_problem (
    id, revision_major, revision_minor
  ) ON DELETE CASCADE
);


CREATE TABLE evaluation (
  id TEXT NOT NULL,
  evaluator INTEGER NOT NULL REFERENCES evaluator (id) ON DELETE CASCADE,
  run INTEGER NOT NULL REFERENCES Run (id) ON DELETE CASCADE,
  did_succeed BOOLEAN NOT NULL DEFAULT FALSE,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id, evaluator, run)
);


CREATE TABLE configured_solution (
  id TEXT NOT NULL,

  filename TEXT NOT NULL,

  solution TEXT NOT NULL REFERENCES solution (id) ON DELETE CASCADE,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  PRIMARY KEY (id, solution)
);


CREATE TABLE Run (
  id INTEGER PRIMARY KEY AUTOINCREMENT,

  engine TEXT NOT NULL REFERENCES engine (id) ON DELETE CASCADE,
  dataset TEXT NOT NULL REFERENCES dataset (in_digest) ON DELETE CASCADE,
  output TEXT NOT NULL,
  log TEXT,
  started DATETIME NOT NULL,
  duration REAL NOT NULL,
  configured_solution_id TEXT NOT NULL,
  configured_solution_solution TEXT NOT NULL,
  load_average REAL NOT NULL,
  load_max REAL NOT NULL,
  ram_average REAL NOT NULL,
  ram_max REAL NOT NULL,

  meta_created DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  meta_updated DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (
    configured_solution_id,
    configured_solution_solution
  ) REFERENCES configured_solution (
    id, solution
  ) ON DELETE CASCADE
);


CREATE INDEX idx_engine__team ON engine (team);
CREATE INDEX idx_solution__challenge_problem_id_challenge_problem_revision_major_challenge_problem_revision_minor ON solution (challenge_problem_id, challenge_problem_revision_major, challenge_problem_revision_minor);
CREATE INDEX idx_solution__engine ON solution (engine);
CREATE INDEX idx_evaluator__challenge_problem_id_challenge_problem_revision_major_challenge_problem_revision_minor ON evaluator (challenge_problem_id, challenge_problem_revision_major, challenge_problem_revision_minor);
CREATE INDEX idx_evaluation__evaluator ON evaluation (evaluator);
CREATE INDEX idx_evaluation__run ON evaluation (run);
CREATE INDEX idx_configured_solution__solution ON configured_solution (solution);
CREATE INDEX idx_challenge_problem__evaluator ON challenge_problem (evaluator);
CREATE INDEX idx_run__configured_solution_id_configured_solution_solution ON Run (configured_solution_id, configured_solution_solution);
CREATE INDEX idx_run__dataset ON Run (dataset);
CREATE INDEX idx_run__engine ON Run (engine);
CREATE INDEX idx_challengeproblem_dataset ON ChallengeProblem_Dataset (dataset);
