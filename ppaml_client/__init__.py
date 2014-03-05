# __init__.py -- package wrapper                -*- coding: us-ascii -*-
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

"""Client library for PPAML.

This library provides common functionality the PPAML client scripts need
to run.

"""


__version__ = "0.1.0"


# Check Python version.
import sys
if not '2.6' <= sys.version < '3':
    raise ImportError("ppaml_client requires Python 2.6 or 2.7")
del sys


__all__ = ['fingerprint', 'namespace']

from fingerprint import Fingerprint, HeterogeneousSystemException
from namespace import Namespace
