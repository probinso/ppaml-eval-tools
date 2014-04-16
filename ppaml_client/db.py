# db.py -- database operations                  -*- coding: us-ascii -*-
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

"""Database operations.

The PPAML client tools store all data in a SQLite 3 database that lives in the
user's home directory.  This module provides an object-relational map (using
SQLAlchemy) to manipulate the database, as well as some convenience functions
to ensure that only one database exists.

"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

from abc import ABCMeta, abstractproperty
import contextlib
import errno
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


class _Database:
    """A connection to a database."""
    __metaclass__ = ABCMeta

    @abstractproperty
    def _Table(self):
        raise NotImplementedError()

    @abstractproperty
    def _schema_path(self):
        raise NotImplementedError()

    def _create(self, path):
        """Creates a table according to the table schema."""
        # Normally with SQLAlchemy, you'd define your objects and issue
        # a call to create_all.  However, we'd like to use SQLAlchemy's
        # reflection support to generate those objects automatically, so
        # we need to execute some raw SQL.  SQLAlchemy won't let us do
        # that--it requires a valid database before executing SQL--so we
        # get to use the more primitive sqlite3 module.
        with sqlite3.connect(path) as new_db:
            new_db.executescript(self._schema_path)


@sqlalchemy.event.listens_for(sqlalchemy.engine.Engine, 'connect')
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class SchemaMismatch(Exception):
    """Indicates discovery of a database with the wrong schema."""

    def __init__(self, path):
        super(SchemaMismatch, self).__init__(textwrap.fill(
            textwrap.dedent("""\
                Database {} exists, but it does not match the
                expected schema.""".format(path)),
            width=80,
            ))


class NotReentrant(Exception):
    """Indicates an attempt to do an unsupported reentrant operation."""

    def __init__(self):
        super(NotReentrant, self).__init__("SQL sessions are not reentrant")


class ForeignKeyViolation(Exception):
    """Indicates a FOREIGN KEY constraint has failed."""

    def __init__(self, class_, id_number):
        try:
            class_name = class_.human_name.capitalize()
        except AttributeError:
            class_name = class_.__name__
        super(ForeignKeyViolation, self).__init__(textwrap.fill(
            textwrap.dedent("""\
                {} {} does not exist""".format(class_name, id_number)),
            width=80,
            ))

class NoActiveSession(Exception):
    """Method requires active session"""

    def __init__(self):
        super(NoActiveSession, self).__init__("no presently active session")


############################### Index database ################################


class Index(_Database):
    """A database which records artifacts and runs of those artifacts.

    """

    ##### Initialization #####

    def __init__(self, path, create=True):
        self.__Session = sqlalchemy.orm.sessionmaker()

        self.__Table = None
        self.ChallengeProblem = None
        self.Team = None
        self.PPS = None
        self.Artifact = None
        self.Run = None
        self.Tag = None
        self.Environment = None
        self.Hardware = None
        self.Software = None

        self.engine = None
        self._active_session = None

        self._initialize_table_classes()
        self._connect(path, create)

    @classmethod
    def open_user_index(class_):
        """Opens the current user's default index.db."""
        for directory in xdg.BaseDirectory.load_data_paths('ppaml'):
            db_path = os.path.join(directory, 'index.db')
            try:
                return class_(db_path, create=False)

            except IOError as io_error:
                if (io_error.errno == errno.ENOENT and
                    io_error.filename == db_path):
                    # We couldn't connect to the database, which
                    # probably means it doesn't exist.  Try the next
                    # possible location.
                    continue
                else:
                    raise

            except sqlalchemy.exc.NoSuchTableError:
                # We found a database, but it doesn't satisfy our
                # schema.
                raise SchemaMismatch(db_path)

        else:
            # We tried all the possible locations for the database as
            # specified by XDG, and the database isn't there.  Create a
            # new one.
            db_path = os.path.join(
                xdg.BaseDirectory.save_data_path('ppaml'),
                'index.db',
                )
            return class_(db_path, create=True)

    @property
    def _Table(self):
        return self.__Table

    @property
    def _schema_path(self):
        return pkgutil.get_data('ppaml_client', 'db_init.sql')

    def _initialize_table_classes(self):
        # Create the table superclass.
        # SQLAlchemy's ORM will map exactly one class to exactly one
        # database table.  All the mapped classes inherit from a single
        # /declarative base class/, which keeps track of the mappings.
        self.__Table = sqlalchemy_declarative.declarative_base(
            # Use DeferredReflection so that we can populate the classes
            # later by reflection from the database; see
            # <http://docs.sqlalchemy.org/en/rel_0_9/orm/extensions/declarative.html#using-reflection-with-declarative>.
            # This lets us avoid duplicating fields and semantics
            # between the SQL schema and the mapped classes.
            cls=sqlalchemy_declarative.DeferredReflection,
            )

        # Create classes for the database tables.

        class ChallengeProblem(self._Table):
            """A PPAML challenge problem."""
            __tablename__ = 'challenge_problem'
            human_name = "challenge problem"
        self.ChallengeProblem = ChallengeProblem

        class Team(self._Table):
            """A performer team."""
            __tablename__ = 'team'
            human_name = "team"
        self.Team = Team

        class PPS(self._Table):
            """A probabilistic programming system."""
            __tablename__ = 'pps'
            human_name = "PPS"
        self.PPS = PPS

        class Artifact(self._Table):
            """A program submitted to PPAML for evaluation."""
            __tablename__ = 'artifact'
            human_name = "artifact"
        self.Artifact = Artifact

        class Run(self._Table):
            """A single execution of an Artifact."""
            __tablename__ = 'run'
            human_name = "run"
        self.Run = Run

        class Tag(self._Table):
            """Lookup for Tagged Runs."""
            __tablename__ = 'tag'
            human_name = "tag"
        self.Tag = Tag

        class Environment(self._Table):
            """A machine fingerprint.

            This data do not uniquely identify the machine, but they
            give enough information that its overall specifications may
            be easily inferred.

            """
            __tablename__ = 'environment'
            human_name = "environment record"
        self.Environment = Environment

        class Hardware(self._Table):
            """The hardware component of an Environment."""
            __tablename__ = 'hardware'
            human_name = "hardware record"
        self.Hardware = Hardware

        class Software(self._Table):
            """The software component of an Environment."""
            __tablename__ = 'software'
            human_name = "software record"
        self.Software = Software

    def _connect(self, path, create):
        # Create the engine.
        self.engine = sqlalchemy.create_engine(
            'sqlite:///'+path,
            echo=(os.environ.get('PPAML_SQL_DEBUG') is not None),
            )

        # Try to populate the mapped tables by reflection.
        sqlalchemy.MetaData().reflect(bind=self.engine)

        if os.path.getsize(path):
            self.__Table.prepare(self.engine)
            self.__Session.configure(bind=self.engine)
        else:
            # The database is empty, which means we created it by trying
            # to reflect out of it.
            if create:
                # Create it and try again.
                self._create(path)
                self._connect(path, False)
            else:
                raise IOError(
                    errno.ENOENT,
                    "{}: '{}'".format(os.strerror(errno.ENOENT),
                                      path),
                    )

    ##### Querying #####

    @contextlib.contextmanager
    def session(self, *args, **kwargs):
        """Begins a database transaction, yielding a sqlalchemy.Session.

        Common exceptions:
          - NotReentrant: You tried to start a session inside a session.
          - sqlalchemy.exc.InterfaceError: Your SQL was ill-typed--e.g.,
            you attempted to insert an integer into a VARCHAR.
          - sqlalchemy.exc.IntegrityError: You violated a SQL
            constraint.

        """
        if self._active_session:
            raise NotReentrant()
        else:
            self._active_session = self.__Session(*args, **kwargs)
            try:
                yield self._active_session
                self._active_session.commit()
            except:
                self._active_session.rollback()
                raise
            finally:
                self._active_session.close()
                self._active_session = None

    @contextlib.contextmanager
    def __create_or_use_session(self):
        """An UNSAFE version of session which reuses an active session.

        This function is unsafe--changes you make to the database
        through sessions it returns will not necessarily be committed.
        It is thus extremely unwise to rely on this function for any
        non-query database operations.

        """
        try:
            with self.session() as sess:
                yield sess
        except NotReentrant:
            yield self._active_session

    def contains(self, orm_class, **filters):
        """Performs an EXISTS query.

        The provided class is the ORM class to query over.  All filters are
        passed directly to SQLAlchemy's filter_by function.

        Example:
            my_index.contains(my_index.PPS, team_id=arguments.team_id)

        """
        with self.__create_or_use_session() as sess:
            exists_query = sess.query(orm_class).filter_by(**filters).exists()
            return sess.query(exists_query).scalar()

    def require_foreign_key(self, orm_class, **id_constraint):
        """Checks a foreign key constraint.

        This function sits at a level of abstraction which is difficult
        to express in Python, so its interface is a bit weird.  It's
        best to think of it as taking three arguments:

            require_foreign_key(OtherTable, other_table_id=expected_id)

        will return expected_id if and only if OtherTable contains a row
        with the other_table_id column equal to expected_id.  This
        provides an elegant idiom for setting columns in a new
        row--e.g.,

            def add_student(n):
                new_student = my_index.Student()
                new_student.homeroom_id = my_index.require_foreign_key(
                    my_index.Homeroom,
                    id=n,
                    )

        If the foreign key constraint is not satisfied, this function
        throws a ForeignKeyViolation.

        """
        assert len(id_constraint) == 1
        id_number = id_constraint.values()[0]
        if self.contains(orm_class, **id_constraint):
            return id_number
        else:
            raise ForeignKeyViolation(orm_class, id_number)


    def _require_active_session(self):
        if not self._active_session: raise NoActiveSession()

    def run_specified_by(self, specifier):
        """
          takes in possible run tag or id and returns corresponding run.
          returns None if label does not exist.
          
          This requires an active session
        """
        self._require_active_session()

        session = self._active_session
        if specifier.isdigit():
            run_id = int(specifier)
        else:
            tag = session.query(self.Tag).filter_by(
              label = specifier).scalar()
            run_id = tag.run_id if tag else None

        run = None if run_id == None else session.query(self.Run).filter_by(
          run_id = run_id).scalar()

        return run

    ##### Saving files #####

    @staticmethod
    def migrate_file(path):
        """Migrate a single file into the database directory.

        Return a blob id.

        """
        return Index.migrate((path,), os.path.dirname(path))

    @staticmethod
    def migrate(paths, strip_prefix):
        """Migrate files into the database directory.

        Return a blob ID.

        """
        # TODO: Handle single paths as well as lists of paths.
        with utility.TemporaryDirectory(prefix='ppaml.db.') as sandbox:
            tarball_path = os.path.join(sandbox, 'data.tar.bz2')
            with tarfile.open(tarball_path, 'w:bz2') as tar:
                for source_path in sorted(paths):
                    assert source_path.startswith(strip_prefix), \
                        '"{}" does not start with "{}"'.format(
                            source_path,
                            strip_prefix,
                            )
                    short_path = source_path[len(strip_prefix):]
                    tar.add(source_path, short_path)

            with open(tarball_path, 'rb') as tarball:
                blob_id = hashlib.md5(tarball.read()).hexdigest()

            # TODO: Throw an exception if the file is already there?
            shutil.copyfile(
                tarball_path,
                os.path.join(
                    xdg.BaseDirectory.save_data_path('ppaml'),
                    blob_id,
                    ),
                )

        return blob_id

    @staticmethod
    def extract_blob(blob_id, dest_dir):
        """Extracts the contents of a blob into a directory."""
        with tarfile.open(os.path.join(
                xdg.BaseDirectory.save_data_path('ppaml'),
                blob_id,
                )) as tar:
            tar.extractall(dest_dir)


    @staticmethod
    def remove_blob(blob_id):
        """Remove a blob by ID from the database directory."""
        os.remove(
            os.path.join(xdg.BaseDirectory.save_data_path('ppaml'), blob_id),
            )

