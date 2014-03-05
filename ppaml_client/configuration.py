# configuration.py -- configuration files       -*- coding: us-ascii -*-
# Copyright (C) 2014  Galois, Inc.
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
#
# To contact Galois, complete the Web form at
# <http://corp.galois.com/contact/> or write to Galois, Inc., 421
# Southwest 6th Avenue, Suite 300, Portland, Oregon, 97204-1622.

"""Read PPAML configuration files."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import collections
import glob
import os.path
import textwrap

import configobj
import validate

from . import utility


class MalformedError(Exception):
    """Superclass for all errors related to configuration files."""

    pass


class ParseError(MalformedError):
    """Failure to parse a configuration file."""

    pass


class MissingField(MalformedError):
    """A required field was missing."""

    def __init__(self, section, field):
        super(MissingField, self).__init__(
            'missing required field "{0}" (in section "{0}")'.format(
                field,
                section,
                ),
            )


class EmptyField(MalformedError):
    """A required field was empty."""

    def __init__(self, section, field):
        super(EmptyField, self).__init__(
            'required field "{0}" (in section "{0}") was empty'.format(
                field,
                section,
                ),
            )


class RunConfiguration(configobj.ConfigObj):
    """Configuration file for an artifact run."""

    _CONFIG_SPEC = (
        "[package]",
        "base = string",

        "[artifact]",
        "paths = force_list",
        "config = string",
        "input = string",

        "[evaluation]",
        "evaluator = force_list",
        "ground_truth = string",
        )

    def __init__(self, **kwargs):
        """Parse a config file or create a config file object.

        All keyword arguments will be passed directly to ConfigObj, from
        which this class inherits, except
          - raise_errors, which will be set to True,
          - create_empty, which will be set to False,
          - file_error, which will be set to True, and
          - configspec, which will be set appropriately.

        Should a parse error occur, this function will throw a
        ParseError.  This function does not perform any kind of semantic
        validation or checking on inputs.

        """

        # Set options.
        kwargs['raise_errors'] = True
        kwargs['create_empty'] = False
        kwargs['file_error'] = True
        kwargs['configspec'] = self._CONFIG_SPEC

        # Record the path to the configuration file.
        self._path = kwargs.get('infile')

        # Parse the configuration file.
        try:
            super(RunConfiguration, self).__init__(**kwargs)
        except configobj.ConfigObjError as parse_error:
            raise ParseError(parse_error)

    @property
    def path(self):
        """The path to the configuration file (or None)."""
        return self._path

    def require_no_extra_fields(self):
        """Checks that a configuration file lacks extra fields."""
        self.validate(validate.Validator())
        extra_fields = configobj.get_extra_values(self)
        try:
            extra_field = extra_fields[0]
        except IndexError:
            # No extra fields.
            pass
        else:
            try:
                section_message = '''in section "{0}"'''.format(
                    extra_field[0][0],
                    )
            except IndexError:
                # No section specified; this means it's at the top
                # level.
                section_message = "at top level"
            error_message = """extraneous field "{0}" {1}.""".format(
                extra_field[1],
                section_message
                )
            raise MalformedError(error_message)


    def require_fields(self, *fields):
        """Checks that the requested fields are present and nonempty.

        Throws MissingField or EmptyField as appropriate.

        """
        try:
            for section, field in fields:
                _dummy = self[section][field][0]
        except KeyError:
            raise MissingField(section, field)
        except IndexError:
            raise EmptyField(section, field)

    def expand_path_list(self, section, field):
        """Canonicalizes, expands, and globs the specified paths.

        Relative paths are interpreted relative to the directory
        containing the configuration file; if self does not correspond
        to a file on disk, relative paths will trigger a MalformedError.
        The tilde (~) will be expanded to the user's home directory, but
        no environment variable expansion will occur.

        Despite the name, this function will not necessarily return a
        list; it is merely guaranteed to return a Sequence.

        """
        try:
            result = self[section][field]
        except KeyError:
            raise MissingField(section, field)

        # Expand tildes.
        result = [os.path.expanduser(path) for path in result]

        # Absolutize the paths.  This needs to be done after tilde
        # expansion, since os.path.join does not recognize that a
        # literal tilde represents an absolute path.
        try:
            base_dir = os.path.dirname(
                           os.path.abspath(
                               os.path.expanduser(self._path)))
        except AttributeError:
            base_dir = None
        try:
            result = [os.path.join(base_dir, path) for path in result]
        except AttributeError:
            # base_dir is None, and one of the paths was relative.
            raise MalformedError(textwrap.dedent("""\
                found a relative path in a configuration object not backed by a
                file"""))

        # Expand globs and flatten the list of expansions.
        result = [glob.glob(path) for path in result]
        result = [path for path_list in result for path in path_list]

        # Normalize the paths.
        result = [os.path.normpath(path) for path in result]

        # Perform final sanity checks and return.
        assert isinstance(result, collections.Sequence)
        for path in result:
            assert isinstance(path, (str, unicode)), \
                "path {0!r} is not a string".format(path)
            assert os.path.isabs(path), \
                "path {0} is not absolute".format(path)
        return result


def read_from_file(infile, required_fields=()):
    """Read and validate configuration from a configuration file.

    This function is intended to be used in applications; it throws a
    utility.FatalError if the configuration is malformed, rather than
    propagating a MalformedError back to the caller."""
    # Read
    try:
        conf = RunConfiguration(infile=infile)

    except IOError as io_error:
        raise utility.FatalError(textwrap.dedent("""\
            {0}  Did you remember to create the configuration file?  Say
            "ppaml init{1}" to create one.""".format(
                    io_error,
                    '' if infile == 'run.conf' else " -o {0}".format(infile),
                    )))

    except ParseError as parse_error:
        raise utility.FatalError(
            "Error parsing configuration file: {0}".format(parse_error),
            )

    # Validate
    try:
        conf.require_no_extra_fields()
        conf.require_fields(*required_fields)
    except (MalformedError, MissingField, EmptyField) as error:
        raise utility.FatalError("Configuration error: {0}".format(error))

    return conf
