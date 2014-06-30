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
-- THIS SOFTWARE IS PROVIDED BY GALOIS AND OTHER CONTRIBUTORS "AS IS" AND ANY
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
PRAGMA user_version = 7;

-- [sqlite] SQLAlchemy's SQLite backend does not natively handle floating-point
-- values, so all instances of TIMESTAMP WITH TIME ZONE have been replaced with
-- BIGINT.

CREATE TABLE challenge_problem (
	challenge_problem_id INTEGER PRIMARY KEY
		AUTOINCREMENT,	-- [sqlite]

	description VARCHAR(255) NOT NULL,
	revision SMALLINT NOT NULL CHECK (revision > 0),
	url VARCHAR(255) NOT NULL, -- challenge problem's wiki page

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP

	CHECK (meta_created <= meta_updated),
	UNIQUE (description, revision));

CREATE TRIGGER challenge_problem_updated AFTER UPDATE ON challenge_problem
	FOR EACH ROW
	BEGIN
		UPDATE challenge_problem
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE challenge_problem_id = NEW.challenge_problem_id;
	END;

CREATE TABLE team (
	team_id INTEGER PRIMARY KEY
		AUTOINCREMENT,	-- [sqlite]

	institution VARCHAR(255) NOT NULL,
	contact_name VARCHAR(255) NOT NULL,
	contact_email VARCHAR(255) NOT NULL,

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (meta_created <= meta_updated),
	UNIQUE (institution, contact_name, contact_email));

CREATE TRIGGER team_updated AFTER UPDATE ON team
	FOR EACH ROW
	BEGIN
		UPDATE team
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE team_id = NEW.team_id;
	END;

CREATE TABLE challenge_problem_and_pps (
	challenge_problem_id INTEGER NOT NULL
		REFERENCES challenge_problem ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	pps_id INTEGER NOT NULL
		REFERENCES pps ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE pps (
	pps_id INTEGER PRIMARY KEY
		AUTOINCREMENT,	-- [sqlite]

	team_id INTEGER NOT NULL
		REFERENCES team ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	description VARCHAR(255) NOT NULL,
	version VARCHAR(255) NOT NULL,

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (meta_created <= meta_updated),
	UNIQUE (team_id, description, version));

CREATE TRIGGER pps_updated AFTER UPDATE ON pps
	FOR EACH ROW
	BEGIN
		UPDATE pps
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE pps_id = NEW.pps_id;
	END;

CREATE TABLE artifact (
	-- The artifact ID is a 32-character string--a stringified version of
	-- the artifact's 128-bit MD5 hash (as would be output by md5sum(1)).
	artifact_id CHAR(32) PRIMARY KEY,

	challenge_problem_id INTEGER NOT NULL
		REFERENCES challenge_problem ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	team_id INTEGER NOT NULL
		REFERENCES team ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	pps_id INTEGER NOT NULL
		REFERENCES pps ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	description VARCHAR(255),
	version VARCHAR(255),
	submit_timestamp BIGINT DEFAULT CURRENT_TIMESTAMP,

	-- Some artifacts will be interpreted, but some have a separate
	-- compilation step.  These columns are currently placeholders, but
	-- they may be used in the future.
	interpreted SMALLINT
		CHECK (interpreted BETWEEN 0 AND 1),
	-- Artifact binary bundle
	binary CHAR(32),
	build_environment_id INTEGER
		REFERENCES environment(environment_id) ON DELETE RESTRICT
		DEFERRABLE INITIALLY DEFERRED,
	compiler CHAR(32),
	build_flags VARCHAR(255),
	build_configuration CHAR(32),
	build_started BIGINT,
	build_load_average REAL CHECK (build_load_average >= 0),
	build_load_max REAL CHECK (build_load_max >= 0),
	build_ram_average BIGINT CHECK (build_ram_average >= 0),
	build_ram_max BIGINT CHECK (build_ram_max >= 0),

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (build_load_average <= build_load_max),
	CHECK (build_ram_average <= build_ram_max),
	CHECK (meta_created <= meta_updated));

CREATE TRIGGER artifact_updated AFTER UPDATE ON artifact
	FOR EACH ROW
	BEGIN
		UPDATE artifact
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE artifact_id = NEW.artifact_id;
	END;

CREATE TABLE run (
	run_id INTEGER PRIMARY KEY
		AUTOINCREMENT,	-- [sqlite]

	dataset_label VARCHAR(255) NOT NULL,

	artifact_id CHAR(32) NOT NULL
		REFERENCES artifact ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	pps_id INTEGER NOT NULL
		REFERENCES pps ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	environment_id INTEGER NOT NULL
		REFERENCES environment ON DELETE RESTRICT
		DEFERRABLE INITIALLY DEFERRED,
	challenge_problem_id INTEGER NOT NULL
		REFERENCES challenge_problem ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	team_id INTEGER NOT NULL
		REFERENCES team ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	started BIGINT,
	artifact_configuration CHAR(32),
	output CHAR(32),
	log CHAR(32),
	trace CHAR(32),
	duration DOUBLE PRECISION CHECK (duration >= 0),
	quant_score CHAR(32),
	-- Where the qualitative evaluation goes
	qual_score CHAR(32),
	load_average REAL CHECK (load_average >= 0),
	load_max REAL CHECK (load_max >= 0),
	ram_average BIGINT CHECK (ram_average >= 0),
	ram_max BIGINT CHECK (ram_max >= 0),

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (load_average <= load_max),
	CHECK (ram_average <= ram_max),
	CHECK (meta_created <= meta_updated));

CREATE TRIGGER run_updated AFTER UPDATE ON run
	FOR EACH ROW
	BEGIN
		UPDATE run
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE run_id = NEW.run_id;
	END;

CREATE TABLE tag (
	label VARCHAR(255) NOT NULL PRIMARY KEY,
	run_id INTEGER NOT NULL
		REFERENCES run ON DELETE CASCADE,

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (meta_created <= meta_updated),
	UNIQUE (label));

CREATE TRIGGER tag_updated AFTER UPDATE ON tag
	FOR EACH ROW
	BEGIN
		UPDATE tag
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE label = NEW.label;
	END;

CREATE TABLE environment (
	environment_id INTEGER PRIMARY KEY
		AUTOINCREMENT,	-- [sqlite]

	hardware_id INTEGER NOT NULL
		REFERENCES hardware ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	software_id INTEGER NOT NULL
		REFERENCES software ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (meta_created <= meta_updated));

CREATE TRIGGER environment_updated AFTER UPDATE ON environment
	FOR EACH ROW
	BEGIN
		UPDATE environment
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE environment_id = NEW.environment_id;
	END;

CREATE TABLE hardware (
	hardware_id INTEGER PRIMARY KEY
		AUTOINCREMENT,	-- [sqlite]

	description VARCHAR(255),
	cpu_family INTEGER,
	cpu_model INTEGER,
	cpu_model_name VARCHAR(63),
	cpu_stepping INTEGER,
	cpu_microcode INTEGER,
	cpu_n_cores INTEGER CHECK (cpu_n_cores > 0),
	cpu_n_threads INTEGER CHECK (cpu_n_threads > 0),
	cpu_cache BIGINT CHECK (cpu_cache > 0),
	cpu_clock REAL CHECK (cpu_clock > 0),

	ram BIGINT CHECK (ram > 0),

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (meta_created <= meta_updated));

CREATE TRIGGER hardware_updated AFTER UPDATE ON hardware
	FOR EACH ROW
	BEGIN
		UPDATE hardware
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE hardware_id = NEW.hardware_id;
	END;

CREATE TABLE software (
	software_id INTEGER PRIMARY KEY
		AUTOINCREMENT,	-- [sqlite]

	description VARCHAR(255),
	kernel VARCHAR(31) NOT NULL, -- e.g., "Linux"
	kernel_version VARCHAR(63),
	userland VARCHAR(31),	-- e.g., "GNU", "Darwin"
	hostname VARCHAR(255) NOT NULL,

	meta_created BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated BIGINT NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (meta_created <= meta_updated));

CREATE TRIGGER software_updated AFTER UPDATE ON software
	FOR EACH ROW
	BEGIN
		UPDATE software
		SET meta_updated = CURRENT_TIMESTAMP
		WHERE software_id = NEW.software_id;
	END;

/*
INSERT TEAMS
*/

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Galois Inc.','Philip Robinson','probinson@galois.com');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Applied Communications Sciences','Dr. Akshay Vashist','avashist@appcomsci.com');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('BAE Systems Information','Dr. Gregory Sullivan','gregory.sullivan@baesystems.com');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Charles River Analytics','Dr. Avi Pfeffer','apfeffer@cra.com');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Gamelan Labs, Inc.','Dr. Ben Vigoda','ben.vigoda@gamelanlabs.com');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Indiana University','Dr. Chung-Chieh Shan','ccshan@indiana.edu');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Massachusetetts Institute of Technology','Dr. Vikash Mansingka','vkm@mit.edu');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Princeton University','Dr. David Blei','blei@cs.princeton.edu');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('SRI International','Dr. Rodrigo de Salvo Braz','rodrigo.desalvobraz@sri.com');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('Stanford University','Dr. Noah Goodman','ngoodman@stanford.edu');

INSERT INTO
	"team" ('institution', 'contact_name', 'contact_email')
	VALUES('University of California Riverside','Dr. Christian Shelton','cshelton@cs.ucr.edu');

/*
INSERT PPS STUBS
*/
INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(1, 1, 'Galois #1 - WizardMagic', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(2, 2, 'ACS #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(3, 3, 'BSI #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(4, 4, 'CRA #1 - Figaro', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(5, 5, 'GL #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(6, 6, 'IU #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(7, 7, 'MIT #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(8, 8, 'PU #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(9, 9, 'SRII #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(10, 10, 'SU #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(11, 11, 'UCR #1', 1);

INSERT INTO
	"pps" ('pps_id', 'team_id', 'description', 'version')
	VALUES(12, 4, 'CRA #2 - Blog', 1);

INSERT INTO "pps" ('pps_id', 'team_id', 'description', 'version') VALUES(13, 4, 'CRA #1 - Figaro Sanity', 1);


/*
CHALLENGE 1 PROBLEMS
*/

INSERT INTO
	"challenge_problem" ('description', 'url', 'revision')
	VALUES('Quad-Rotor Sensor Fusion', 'http://ppaml.galois.com/wiki/wiki/CP1QuadRotor', 1);

INSERT INTO
	"challenge_problem" ('description', 'url', 'revision')
	VALUES('Continent-Scale Bird Migration Modeling', 'http://ppaml.galois.com/wiki/wiki/CP2BirdMigration', 1);

INSERT INTO
	"challenge_problem" ('description', 'url', 'revision')
	VALUES('Wide Area Motion Imagery Track Linking', 'http://ppaml.galois.com/wiki/wiki/CP3WAMITrackLinking', 1);

