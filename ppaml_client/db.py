# db.py -- database operations                  -*- coding: us-ascii -*-
# Copyright (C) 2014  Galois, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#   1. Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#   2. Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#   3. Neither Galois's name nor the names of other contributors may be used to
#      endorse or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY GALOIS AND OTHER CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED.  IN NO EVENT SHALL GALOIS OR OTHER CONTRIBUTORS BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Database operations.

The PPAML client tools store all data in a SQLite 3 database that lives in the
user's home directory.  This module provides an object-relational map (using
SQLAlchemy) to manipulate the database, as well as some convenience functions
to ensure that only one database exists.

"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import contextlib
import hashlib
import os
import pkgutil
import shutil
import sqlite3
import tarfile
import textwrap
import time

import sqlalchemy
import sqlalchemy.ext.declarative as sqlalchemy_declarative
import xdg.BaseDirectory

from . import utility



############################### Mapped classes ################################


# SQLAlchemy's ORM will map exactly one class to exactly one database
# table.  All the mapped classes inherit from a single /declarative base
# class/, which keeps track of the mappings.

PPAMLDBTable = sqlalchemy_declarative.declarative_base(
    # Use DeferredReflection so that we can populate the classes later
    # by reflection from the database; see
    # <http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#using-reflection-with-declarative>.
    # This lets us avoid duplicating fields and semantics between the
    # SQL schema and the mapped classes.
    cls=sqlalchemy_declarative.DeferredReflection,
    )


class ChallengeProblem(PPAMLDBTable):
    """A PPAML challenge problem."""

    __tablename__ = 'challenge_problem'
    human_name = "challenge problem"


class Team(PPAMLDBTable):
    """A performer team."""

    __tablename__ = 'team'
    human_name = "team"


class PPS(PPAMLDBTable):
    """A probabilistic programming system."""

    __tablename__ = 'pps'
    human_name = "PPS"


class Artifact(PPAMLDBTable):
    """A program submitted to PPAML for evaluation."""

    __tablename__ = 'artifact'
    human_name = "artifact"


class Run(PPAMLDBTable):
    """A single execution of an Artifact."""

    __tablename__ = 'run'
    human_name = "run"


class Environment(PPAMLDBTable):
    """A machine fingerprint.

    This data do not uniquely identify the machine, but they give enough
    information that its overall specifications may be easily inferred.

    """

    __tablename__ = 'environment'
    human_name = "environment record"


class Hardware(PPAMLDBTable):
    """The hardware component of an Environment."""

    __tablename__ = 'hardware'
    human_name = "hardware record"


class Software(PPAMLDBTable):
    """The software component of an Environment."""

    __tablename__ = 'software'
    human_name = "software record"



########################### Talking to the database ###########################


@sqlalchemy.event.listens_for(sqlalchemy.engine.Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


_Session = sqlalchemy.orm.sessionmaker()


@contextlib.contextmanager
def session(*args, **kwargs):
    """Begins a database transaction, yielding a sqlalchemy.Session.

    Common exceptions:
      - sqlalchemy.exc.InterfaceError: Your SQL was ill-typed--e.g., you
        attempted to insert an integer into a VARCHAR.
      - sqlalchemy.exc.IntegrityError: You violated a SQL constraint.

    """
    s = _Session(*args, **kwargs)
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()



##### Queries #####


# A useful shortcut for EXISTS queries.
def contains(active_session, class_, **filters):
    """Performs an EXISTS query.

    The provided class is the ORM class to query over.  All filters are
    passed directly to SQLAlchemy's filter_by function.

    Example:
        db.contains(session, PPS, team_id=arguments.team_id)

    """
    exists_query = active_session.query(class_).filter_by(**filters).exists()
    return active_session.query(exists_query).scalar()


# A shortcut for checking FOREIGN KEY constraints.
def require_foreign_key(active_session, class_, **id_constraint):
    """Checks a foreign key constraint.

    This function sits at a level of abstraction which is difficult to
    express in Python, so its interface is a bit weird.  It's best to
    think of it as taking four arguments:

        require_foreign_key(session, OtherTable,
                            other_table_id=expected_id)

    will return expected_id if and only if OtherTable contains a row
    with the other_table_id column equal to expected_id.  This provides
    an elegant idiom for setting columns in a new row--e.g.,

        def add_student(n):
            new_student = Student()
            new_student.homeroom_id = require_foreign_key(
                session,
                Homeroom,
                id=n,
                )

    If the foreign key constraint is not satisfied, this function throws
    a utility.FatalError.

    """
    assert len(id_constraint) == 1
    id_number = id_constraint.values()[0]
    if contains(active_session, class_, **id_constraint):
        return id_number
    else:
        raise utility.FatalError(textwrap.fill(textwrap.dedent("""\
            {0} {1} does not exist.""".format(
                class_.human_name.capitalize(),
                id_number,
                ))))



################################ Saving files #################################


def migrate(paths, strip_prefix):
    """Migrate files into the database directory.

    Return a blob ID.

    """
    # TODO: Handle single paths as well as lists of paths.
    with utility.TemporaryDirectory(prefix='ppaml.db.') as sandbox:
        tarball_path = os.path.join(sandbox, 'data.tar.bz2')
        with tarfile.open(tarball_path, 'w:bz2') as tar:
            for source_path in sorted(paths):
                assert source_path.startswith(strip_prefix)
                short_path = source_path[len(strip_prefix):]
                tar.add(source_path, short_path)

        with open(tarball_path, 'rb') as tarball:
            blob_id = hashlib.md5(tarball.read()).hexdigest()

        # TODO: Throw an exception if the file is already there?
        shutil.copyfile(
            tarball_path,
            os.path.join(xdg.BaseDirectory.save_data_path('ppaml'), blob_id),
            )

    return blob_id


def remove_blob(blob_id):
    """Remove a blob by ID from the database directory."""
    os.remove(os.path.join(xdg.BaseDirectory.save_data_path('ppaml'), blob_id))



############################### Initialization ################################


def _init():
    """Connects to the database and exposes it through this module.

    This function MUST be called immediately after import.

    """
    # Connect to the database.
    for directory in xdg.BaseDirectory.load_data_paths('ppaml'):
        db_path = os.path.join(directory, 'index.db')

        try:
            engine = _create_engine_and_reflect(db_path)
            break

        except sqlalchemy.exc.OperationalError:
            # We couldn't connect to the database, which probably means
            # it doesn't exist.  Try the next possible location.
            continue

        except sqlalchemy.exc.NoSuchTableError:
            # We found a database, but it doesn't satisfy our schema.
            # It might be somebody else's database, which means either
            # it's somebody else's database (bad) or it just got created
            # (also bad--a newly-created database should go in
            # $XDG_DATA_HOME/ppaml).
            if (os.path.getsize(db_path) == 0 and
                time.time() - os.path.getmtime(db_path) < 5):
                # Empty file created less than 5 seconds ago?  We just
                # created it.  Get rid of it.
                os.remove(db_path)
            else:
                # Almost certainly somebody else's database.  This is
                # bad news--somebody's gone and stuck their data in a
                # path we're looking for.  Better just bail out before
                # we accidentally clobber some other app's data.
                raise utility.FatalError(
                    textwrap.dedent("""\
                        Database {0} exists, but it does not match the PPAML
                        schema.  Is it generated by another
                        application?""".format(db_path)))
            continue

    else:
        # We tried all the possible locations for the database as
        # specified by XDG, and the database isn't there.  Create a new
        # one.
        #
        # Normally with SQLAlchemy, you'd define your objects and issue
        # a call to create_all.  However, we'd like to use SQLAlchemy's
        # reflection support to generate those objects automatically, so
        # we need to execute some raw SQL.  SQLAlchemy won't let us do
        # that--it requires a valid database before executing SQL--so we
        # get to use the more primitive sqlite3 module.
        db_path = os.path.join(
            xdg.BaseDirectory.save_data_path('ppaml'),
            'index.db',
            )
        with sqlite3.connect(db_path) as new_db:
            new_db.executescript(
                pkgutil.get_data('ppaml_client', 'db_init.sql'),
                )
        engine = _create_engine_and_reflect(db_path)

    # Bind the _Session class to the engine.
    _Session.configure(bind=engine)


def _create_engine_and_reflect(db_path):
    """Creates a SQLAlchemy engine and reflects its database's contents.

    """
    # Create the engine.
    echo = os.environ.get('PPAML_SQL_DEBUG') is not None
    engine = sqlalchemy.create_engine('sqlite:///'+db_path, echo=echo)
    metadata = sqlalchemy.MetaData()

    # Populate the mapped tables by reflection.
    metadata.reflect(bind=engine)
    PPAMLDBTable.prepare(engine)

    return engine


_init()
