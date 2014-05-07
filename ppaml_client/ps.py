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

import os

import configobj
import validate


from . import utility
from . import __version__

#__version__ = "x.y.z"

class MissingField(utility.FormatedError):
    def __init__(self, section, field):
        super(MissingField, self).__init__(
          'missing required field "{0}" (in section "{1}")',
          field,
          section)


class ExtraField(utility.FormatedError):
    def __init__(self, section, field):

        super(ExtraField, self).__init__(
          'please remove extra fields "{0}" (in section "{1}")',
          field,
          section)


class ProblemSolutionConfig(configobj.ConfigObj):
    def __init__(self, **kwargs):
        assert(type(self) != ProblemSolutionConfig)
        # Set options.
        kwargs['raise_errors'] = True
        kwargs['create_empty'] = False
        kwargs['file_error'] = True

        if kwargs.has_key('configspec'):
            self._CONFIG_SPEC = kwargs['configspec']
        else:
            self._CONFIG_SPEC = ()

        self._CONFIG_SPEC += (
          "paths = force_list",
          "basedir = string",
        )

        kwargs['configspec'] = self._CONFIG_SPEC

        try:
            configobj.ConfigObj.__init__(self, **kwargs)
        except IOError as io_error:
            raise utility.FormatedError("""\
              {0}  Did you remember to create the configuration file?  Use
              "ppaml init" to create one.""",
              io_error
            )

        if 'infile' in kwargs:
            self.require_no_extra_fields()

    @property
    def path(self):
        return self.filename

    @property
    def executable(self):
        self.require_fields(('files', 'paths'),('files', 'basedir'))
        return os.path.abspath(os.path.join(
          self['files']['basedir'], self['files']['paths'][0]))

    def require_fields(self, *fields):
        """
          Checks that the requested fields are present and nonempty.
          Throws MissingField as appropriate.
        """
        try:
            for section, field in fields:
                if not self[section][field]:
                    raise KeyError
        except (KeyError, IndexError):
            raise MissingField(section, field)

    def require_no_extra_fields(self):
        """
          raises ExtraField exception when extra fields exist in config file
        """
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

    @property
    def expanded_files_list(self):
        """
          return list of files referenced by this configuration file
        """
        assert(self.path)

        basedir = self['files']['basedir']
        files = []
        for field in self['files']:
            if field == 'basedir':
                # basedir is special case
                continue
            elif field: # ignore empty fields
                tmp = self['files'][field]
                files += [tmp] if not isinstance(tmp, list) else tmp

        # filter removes system devices like '/dev/null/' and directories
        return filter(os.path.isfile, utility.expand_path_list(files, basedir))


    def populate_defaults(self):
        _format = lambda x: utility.FormatMessage(x).split("\n")

        self.initial_comment = [
          "Configuration file for PPAML ",
          "Created by ppaml init v{0}".format(__version__),
        ]

        # [files]
        self.comments['files'] = [
          '','',
          "This is where all solution files required will be listed"
          ]
       # paths
        self['files']['paths'] = [
          'artifact_exe', 'support_files', '*.blah', 'all/subdirs/*'
          ]
        self['files'].comments['paths'] = [
        '','',
        "All the paths which contribute to this artifact",
        '#'
        ] + _format("""\
            This field gets used for two purposes.  It's used to determine
            which executable to run (the first file listed is assumed to be
            the executable), but it's also used to generate a unique
            identifier for the artifact.  You should thus list the primary
            executable first, followed by all of its source files.""") + ['']
        #basedir
        self['files']['basedir'] = os.getcwd()
        self['files'].comments['basedir'] = ['',
          "all paths are relative to this"]

        self.validate(validate.Validator())


class CPSConfig(ProblemSolutionConfig):
    """
      This is a class used to read and write to Challenge Problem Solutions
      to and from disk.
    """
    def __init__(self, **kwargs):
        self._CONFIG_SPEC = (
          "[identifiers]",
          "challenge_problem_id = integer",
          "challenge_problem_level = integer",
          "pps_id = integer",
          "team_id = integer",

          "[notes]",
          "version = string",
          "description = string",

          "[files]",
          "config = string",
          "input = string"
        )

        kwargs['configspec'] = self._CONFIG_SPEC

        ProblemSolutionConfig.__init__(self, **kwargs)

    def populate_defaults(self, cp_id=int(1), cp_level=int(1), pps_id=int(1),
      team_id=int(1), configpath=os.devnull):

        # [identifiers]
        self['identifiers'] = {}
        self.comments['identifiers'] = ['','',
          "Identifiers are integer values that coorespond to elements already",
          "in the program store"]
        self['identifiers']['challenge_problem_id'] = cp_id
        self['identifiers']['challenge_problem_level'] = cp_level
        self['identifiers']['pps_id'] = pps_id
        self['identifiers']['team_id'] = team_id

        # [notes]
        self['notes'] = {}
        self.comments['notes'] = ['','',
          "This is where you can add human readable descriptors"]
        self['notes']['version'] = ""
        self['notes']['description'] = ""

        # [files]
        self['files'] = {}
        self['files']['config'] = configpath
        self['files']['input'] = "path/to/input/data"
        ProblemSolutionConfig.populate_defaults(self)


class PPSConfig(ProblemSolutionConfig):
    def __init__(self, **kwargs):
        self._CONFIG_SPEC = (
          "[identifiers]",
          "pps_id = integer",
          "team_id = integer",

          "[files]",
          "build = string",
          "build_cps = string",
        )

        kwargs['configspec'] = self._CONFIG_SPEC

        ProblemSolutionConfig.__init__(self, **kwargs)

    def populate_defaults(self, pps_id=int(1), team_id=int(1)):

        # [identifiers]
        self['identifiers'] = {}
        self['identifiers']['pps_id'] = pps_id
        self['identifiers']['team_id'] = team_id

        # [files]
        self['files'] = {}
        self['files']['build'] = os.devnull
        self['files'].comments['build'] = [
          '','',
          "this is the path to the script that builds the pps",
          ]
        self['files']['build_cps'] = 'path/to/run'
        self['files'].comments['build_cps'] = ['','',
          "Given the challenge problem solution executable as input",
          "this path should be able to build the challenge_problem_solution"
          ]
        ProblemSolutionConfig.populate_defaults(self)

