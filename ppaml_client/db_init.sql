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
-- This SQL schema is written in standard SQL, modulo pragmas for SQLite 3.

-- Set the application_id field in the SQLite database header to something
-- other than its default, so file(1) knows this isn't just some random SQLite
-- database.
PRAGMA application_id = 3430079183; -- 0xCC72DACF

-- SQLite provides a nice database header to associate human-readable version
-- information with the schema.
PRAGMA user_version = 4;

CREATE TABLE challenge_problem (
	id INTEGER PRIMARY KEY,

	description VARCHAR(255) NOT NULL,
	revision SMALLINT NOT NULL CHECK (revision > 0),
	url VARCHAR(255) NOT NULL,

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP);

-- Ideally, we'd have a trigger to update meta_updated whenever somebody
-- changes a row.  Unfortunately, SQLite and PostgreSQL each implements a
-- different part of the SQL standard regarding trigger syntax, so it's not
-- currently possible to write triggers that work in both.

CREATE TABLE team (
	id INTEGER PRIMARY KEY,

	institution VARCHAR(255) NOT NULL,
	contact_name VARCHAR(255) NOT NULL,
	contact_email VARCHAR(255) NOT NULL,

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE challenge_problem_and_pps(
	challenge_problem_id INTEGER NOT NULL
		REFERENCES challenge_problem ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	pps_id INTEGER NOT NULL
		REFERENCES pps ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE pps (
	id INTEGER PRIMARY KEY,

	team_id INTEGER NOT NULL
		REFERENCES team ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	description VARCHAR(255),
	version VARCHAR(255),

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE artifact (
	id CHAR(32) PRIMARY KEY,

	compiler_environment_id INTEGER NOT NULL
		REFERENCES environment ON DELETE RESTRICT
		DEFERRABLE INITIALLY DEFERRED,
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
	source VARCHAR(255) NOT NULL,
	time TIMESTAMP WITH TIME ZONE,
	compiler VARCHAR(255),
	compiler_flags VARCHAR(255),
	compiler_configuration VARCHAR(255),
	compiler_started TIMESTAMP WITH TIME ZONE,
	compiler_load_average REAL CHECK (compiler_load_average >= 0),
	compiler_load_max REAL CHECK (compiler_load_max >= 0),
	compiler_ram_average BIGINT CHECK (compiler_ram_average >= 0),
	compiler_ram_max BIGINT CHECK (compiler_ram_max >= 0),
	binary VARCHAR(255) NOT NULL,

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (compiler_load_average <= compiler_load_max),
	CHECK (compiler_ram_average <= compiler_ram_max));

CREATE TABLE run (
	id INTEGER PRIMARY KEY,

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

	started TIMESTAMP WITH TIME ZONE,
	artifact_configuration VARCHAR(255),
	output VARCHAR(255),
	log VARCHAR(255),
	trace_base VARCHAR(255),
	duration DOUBLE PRECISION CHECK (duration >= 0),
	score VARCHAR(255),
	load_average REAL CHECK (load_average >= 0),
	load_max REAL CHECK (load_max >= 0),
	ram_average BIGINT CHECK (ram_average >= 0),
	ram_max BIGINT CHECK (ram_max >= 0),

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,

	CHECK (load_average <= load_max),
	CHECK (ram_average <= ram_max));

CREATE TABLE environment (
	id INTEGER PRIMARY KEY,

	hardware_id INTEGER NOT NULL
		REFERENCES hardware ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,
	software_id INTEGER NOT NULL
		REFERENCES software ON DELETE CASCADE
		DEFERRABLE INITIALLY DEFERRED,

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE hardware (
	id INTEGER PRIMARY KEY,

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

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE software (
	id INTEGER PRIMARY KEY,

	kernel VARCHAR(31) NOT NULL,
	kernel_version VARCHAR(63),
	userland VARCHAR(31),
	hostname VARCHAR(255) NOT NULL,

	meta_created TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP,
	meta_updated TIMESTAMP WITH TIME ZONE NOT NULL
		DEFAULT CURRENT_TIMESTAMP);
