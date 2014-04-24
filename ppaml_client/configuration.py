# configuration.py -- configuration files       -*- coding: us-ascii -*-
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

"""Read PPAML configuration files."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

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
      "[problem]",
      "challenge_problem_id = int",
      "team_id = int",
      "pps_id = int",

      "[artifact]",
      "description = string",
      "version = string",
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

    @property
    def base_dir(self):
        """The directory holding the configuration file (or None)."""
        try:
            return os.path.dirname(
                os.path.abspath(
                    os.path.expanduser(self.path)))
        except AttributeError:
            return None

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
        """Canonicalize, expand, and glob the specified paths.

        Paths are interpreted relative to the directory containing the
        configuration file.  It is a MalformedError for self not to
        correspond to a file on disk, for absolute paths to appear, or
        for paths which reference files above self to appear.
        Accordingly, neither tilde (~) expansion nor environment
        variable expansion will occur.

        Despite the name, this function will not necessarily return a
        list; it is merely guaranteed to return a Sequence.

        """
        #TODO PMR: does it matter that this doesn't check existance of paths
        try:
            result = self[section][field]
        except KeyError:
            raise MissingField(section, field)

        # Absolutize the paths.
        try:
            for i, path in enumerate(result):
                absolute_path = os.path.join(self.base_dir, path)
                if not absolute_path.startswith(self.base_dir):
                    raise MalformedError(textwrap.dedent("""\
                        found an absolute path in the configuration object"""))
                result[i] = absolute_path
        except (AttributeError, TypeError):
            raise MalformedError(textwrap.dedent("""\
                configuration object not backed by a file on disk"""))

        # Expand globs and flatten the list of expansions.
        result = [glob.glob(path) for path in result]
        result = [path for path_list in result for path in path_list]

        # Normalize the paths.
        result = [os.path.normpath(path) for path in result]

        # Perform final sanity checks and return.
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
