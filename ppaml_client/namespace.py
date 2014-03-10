# namespace.py -- Namespace object              -*- coding: us-ascii -*-
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
