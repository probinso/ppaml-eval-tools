# utility.py -- miscellaneous code              -*- coding: us-ascii -*-
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

"""Miscellaneous utility code that didn't seem to fit anywhere else."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import contextlib
import tempfile
import shutil


class FatalError(Exception):
    """An unrecoverable condition from which the program must exit."""

    def __init__(self, message, exit_status=9):
        super(FatalError, self).__init__(message)
        self.exit_status = exit_status


@contextlib.contextmanager
def TemporaryDirectory(suffix='', prefix='tmp', dir=None):
    """Like tempfile.NamedTemporaryFile, but creates a directory.

    This object appears in Python 3 but is unfortunately absent from
    releases of Python 2.

    """
    tree = tempfile.mkdtemp(suffix, prefix, dir)
    try:
        yield tree
    finally:
        shutil.rmtree(tree)

