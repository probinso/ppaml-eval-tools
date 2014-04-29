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

import configobj
import validate


from . import utility

class MalformedError(utility.FatalError):
    """Superclass for all errors related to configuration files."""
    pass


class ParseError(MalformedError):
    """Failure to parse a configuration file."""
    def __init__(self, **kwargs):
        super
    pass


class MissingField(utility.FatalError):
    def __init__(self, section, field):
        super(MissingField, self).__init__(
          'missing required field "{0}" (in section "{1}")',
          field,
          section)

class ExtraField(utility.FatalError):
    def __init__(self, section, field):
        super(MissingField, self).__init__(
          'please remove extra fields "{0}" (in section "{1}")',
          field,
          section)


class RunConfiguration(configobj.ConfigObj):
    """
      configobj.ConfigObj is a class that is used to more easily read
      from configuration files, formated like traditional .ini files
    """

    def __init__(self, **kwargs):

        self._CONFIG_SPEC = (
          "[problem]",
          "challenge_problem_id = int",
          "team_id = int",
          "pps_id = int",

          "[artifact]",
          "description = string",
          "version = string",
          "base = string",
          "paths = force_list",
          "config = string",
          "input = string",

          "[evaluation]",
          "evaluator = force_list",
          "ground_truth = string",
          )

        # Set options.
        kwargs['raise_errors'] = True
        kwargs['create_empty'] = False
        kwargs['file_error'] = True
        kwargs['configspec'] = self._CONFIG_SPEC

        # XXX: old version caught 'ParseErrror', be sure this is nessicary
        super(RunConfiguration, self).__init__(**kwargs)


    @property
    def path(self):
        return self.filename

    @property
    def base_dir(self):
        return os.path.abspath(os.path.expanduser(self['artifact']['base']))

    def require_no_extra_feilds(self):
        self.reload()
        self.validate(validate.Validator())
        extras = configobj.get_extra_values(self)

        if extras:
            section, field = extras[0]
            if not section:
                section = "TOP OF FILE"
            else:
                section = section[0]
            raise ExtraField(section, field)


    def require_fields(self, *fields):
        """
          Checks that the requested fields are present and nonempty.
          Throws MissingField as appropriate.
        """
        try:
            for section, field in fields:
                self[section][field][0]
        except (KeyError, IndexError):
            raise MissingField(section, field)


    def expand_path_list(self, section, field):
        try:
            result = self[section][field]
        except KeyError:
            raise MissingField(section, field)

        for i, path in enumerate(result):
            pass

def read_from_file(infile):
    try:
        conf = RunConfiguration(infile=infile)

    except IOError as io_error:
        raise utility.FormatedError("""\
          {0}  Did you remember to create the configuration file?  Use
          "ppaml init" to create one.""",
          io_error
          )


    return conf
