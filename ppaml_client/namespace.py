# namespace.py -- Namespace object              -*- coding: us-ascii -*-
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

"""Reified namespaces."""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)


class Namespace(dict):
    """Namespace object.

    Similar to a dictionary, a Namespace is a key-value store.  However, in
    addition to supporting all the dictionary methods, a Namespace also
    supports accessing keys that are valid Python identifiers
    directly--e.g.,

        >>> ns = Namespace({'a': 3})
        >>> ns.a
        3

    """

    def __dir__(self):
        return dir(super(Namespace, self)) + self.keys()


    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__,
                                 super(Namespace, self).__repr__())

    def __str__(self):
        pairs = ("{0}: {1!r}".format(key, self[key]) for key in self)
        return "{" + ", ".join(pairs) + "}"

    def __getattr__(self, key):
        if key.startswith('__') and key.endswith('__'):
            raise AttributeError(key)
        try:
            return self[key]
        except KeyError as exn:
            raise AttributeError(exn)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        if key.startswith('__') and key.endswith('__'):
            raise AttributeError(key)
        try:
            del self[key]
        except KeyError:
            raise AttributeError(key)


def test():
    """Run unit tests for this module."""
    import doctest
    doctest.testmod()
