# test_package.py -- test ppaml_client.package  -*- coding: us-ascii -*-
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

# This test script is written for Python 2.6 or 2.7.


from __future__ import (absolute_import, division, print_function)

import errno
import multiprocessing
import os.path
import shutil
import tempfile
import traceback
import unittest

import lockfile

from ppaml_client.package import *


class SandboxedTest(unittest.TestCase):

    def setUp(self):
        self.sandbox = tempfile.mkdtemp(prefix='ppaml.test.')

    def tearDown(self):
        shutil.rmtree(self.sandbox)

    def failOnException(self, thunk):
        try:
            thunk()
        except Exception as exception:
            self.fail("unexpected exception: {0!r}\n{1}".format(
                    exception,
                    traceback.format_exc(exception),
                    ))

    def assertFileEqual(self, actual_path, expected_path):
        with open(actual_path) as actual:
            with open(expected_path) as expected:
                self.assertEqual(actual.read(), expected.read())


class JSONPackageTest(SandboxedTest):

    def setUp(self):
        super(JSONPackageTest, self).setUp()
        self.package = JSONPackage(self.sandbox)

    def tearDown(self):
        self.package.close()
        super(JSONPackageTest, self).tearDown()


class TestJSONPackage(SandboxedTest):

    def test_open_nonexistent_dir(self):
        # Expected behavior: raise IOError with errno == ENOENT.
        try:
            JSONPackage(os.path.join(self.sandbox, "nonexistent"))
        except IOError as io_error:
            self.failUnlessEqual(io_error.errno, errno.ENOENT)
        else:
            self.fail("IOError (with errno == ENOENT) not raised")

    def test_open_file(self):
        # Expected behavior: raise IOError with errno == ENOTDIR.
        not_a_dir = os.path.join(self.sandbox, "file")
        open(not_a_dir, 'wb').close()
        try:
            JSONPackage(not_a_dir)
        except IOError as io_error:
            self.failUnlessEqual(io_error.errno, errno.ENOTDIR)
        else:
            self.fail("IOError (with errno == ENOTDIR) not raised")

    def test_open_empty_dir(self):
        # Expected behavior: create the package.
        def test():
            package = JSONPackage(self.sandbox)
            # TODO: More checks!
        self.failOnException(test)

    def test_open_invalid_package(self):
        # Expected behavior: raise InvalidPackageError.
        open(os.path.join(self.sandbox, "bogus"), 'wb').close()
        self.assertRaises(InvalidPackageError, JSONPackage, self.sandbox)

    def test_fsck_index_only(self):
        # Expected behavior: raise InvalidPackageError.
        open(os.path.join(self.sandbox, "index.json"), 'wb').close()
        self.assertRaises(InvalidPackageError, JSONPackage, self.sandbox)

    def test_fsck_files_only(self):
        # Expected behavior: raise InvalidPackageError.
        os.mkdir(os.path.join(self.sandbox, "files"))
        self.assertRaises(InvalidPackageError, JSONPackage, self.sandbox)

    def test_with_statement(self):
        with JSONPackage(self.sandbox) as package:
            package['foo'] = 'bar'
        self.assertEqual(set(os.listdir(self.sandbox)),
                         set(('index.json', 'files')))


class TestJSONPackageWithPackage(JSONPackageTest):

    def test_open_locked_package(self):
        # Expected behavior: raise lockfile.AlreadyLocked.  lockfile,
        # however, ties the lock to the PID, so simply trying to open
        # (i.e., lock) the already-open package won't work correctly.
        # multiprocessing to the rescue!
        def test():
            self.assertRaises(lockfile.AlreadyLocked,
                              JSONPackage, self.sandbox)
        other_proc = multiprocessing.Process(target=test)
        other_proc.start()
        other_proc.join()

    def test_get_property_path(self):
        self.assertEqual(self.package.path, self.sandbox)

    def test_property_path_read_only(self):
        def test(): self.package.path = ""
        self.assertRaises(AttributeError, test)

    def test_get_property_version(self):
        self.failOnException(lambda: self.package.version)

    def test_property_version_read_only(self):
        def test(): self.package.version = -1
        self.assertRaises(AttributeError, test)

    def test_insert_data(self):
        def test(): self.package['foo'] = 'bar'
        self.failOnException(test)

    def test_insert_data_illtyped_key(self):
        def test(): self.package[3] = None
        self.assertRaises(TypeError, test)

    def test_record_data(self):
        def test(): self.package.record_data('foo', 'bar')
        self.failOnException(test)

    def test_record_data_illtyped_key(self):
        def test(): self.package.record_data(3, None)
        self.assertRaises(TypeError, test)

    def test_record_file(self):
        def test(): self.package.record_file('passwd', "/etc/passwd")
        self.failOnException(test)

    def test_record_file_illtyped_key(self):
        def test(): self.package.record_file(3, "/etc/passwd")
        self.assertRaises(TypeError, test)

    def test_record_file_illtyped_value(self):
        def test(): self.package.record_file('passwd', None)
        self.assertRaises(TypeError, test)

    def test_record_same_name_file(self):
        def test():
            self.package.record_file('passwd', "/etc/passwd")
            self.package.record_file('other_passwd', "/etc/passwd")
        self.failOnException(test)

    def test_record_same_name_file_force_suffix(self):
        def test():
            self.package.record_file('passwd', "/etc/passwd")
            self.package.record_file('passwd.0', "/etc/passwd")
            self.package.record_file('passwd.1', "/etc/passwd")
        self.failOnException(test)

    def test_record_directory(self):
        def test(): self.package.record_file('init.d', "/etc/init.d")
        self.failOnException(test)

    def test_record_file_over_data(self):
        def test():
            self.package['foo'] = 'bar'
            self.package.record_file('foo', "/etc/passwd")
        self.failOnException(test)
        self.assertEqual(len(self.package), 1)
        self.assertFileEqual(self.package['foo'], "/etc/passwd")

    def test_record_data_over_file(self):
        def test():
            self.package.record_file('foo', "/etc/passwd")
            self.package['foo'] = 'bar'
        self.failOnException(test)
        self.assertEqual(len(self.package), 1)
        self.assertEqual(self.package['foo'], 'bar')

    def test_get_data(self):
        self.package['foo'] = 'bar'
        self.assertEqual(self.package['foo'], 'bar')

    def test_get_data_illtyped_key(self):
        self.assertRaises(TypeError, lambda: self.package[3])

    def test_get_file(self):
        self.package.record_file('passwd', "/etc/passwd")
        self.assertFileEqual("/etc/passwd", self.package['passwd'])

    def test_overwrite_file(self):
        self.package.record_file('my_file', "/etc/passwd")
        self.package.record_file('my_file', "/etc/fstab")
        self.assertFileEqual(self.package['my_file'], "/etc/fstab")
        self.failOnException(self.package.fsck)

    def test_delete_data(self):
        self.package['random'] = 17
        del self.package['random']
        self.assertEqual(len(self.package), 0)

    def test_delete_file(self):
        self.package.record_file('stuff', "/etc/passwd")
        del self.package['stuff']
        self.assertEqual(len(self.package), 0)

    def test_delete_directory(self):
        self.package.record_file('init.d', "/etc/init.d")
        del self.package['init.d']
        self.assertEqual(len(self.package), 0)

    def test_close_and_reopen(self):
        def test():
            self.package.close()
            self.package = JSONPackage(self.sandbox)
        self.failOnException(test)

    def test_close_releases_lock(self):
        def test():
            self.failOnException(lambda: JSONPackage(self.sandbox).close())
        self.package.close()
        other_proc = multiprocessing.Process(target=test)
        other_proc.start()
        other_proc.join()
        self.package = JSONPackage(self.sandbox)

    def test_close_data_persistence(self):
        self.package['foo'] = 42
        self.package.close()
        self.package = JSONPackage(self.sandbox)
        self.assertEqual(self.package['foo'], 42)

    def test_close_file_persistence(self):
        self.package.record_file('passwd', "/etc/passwd")
        self.package.close()
        self.package = JSONPackage(self.sandbox)
        self.assertFileEqual(self.package['passwd'], "/etc/passwd")

    def test_container_contains(self):
        self.assertFalse('foo' in self.package)
        self.package['foo'] = 42
        self.package.record_file('passwd', "/etc/passwd")
        self.assertTrue('foo' in self.package)
        self.assertTrue('passwd' in self.package)

    def test_iterable_iter(self):
        self.failOnException(lambda: iter(self.package))
        self.assertEqual(len(list(iter(self.package))), 0)

        self.package['foo'] = 17
        self.assertEqual(len(list(iter(self.package))), 1)
        for key in self.package:
            if key != 'foo':
                self.fail('iterator gave key "{0}" (expected "{1}")'.format(
                        key,
                        'foo',
                        ))

        self.package.record_file('passwd', "/etc/passwd")
        self.assertEqual(len(list(iter(self.package))), 2)

    def test_sized_len(self):
        self.assertEqual(len(self.package), 0)
        self.package['foo'] = 42
        try:
            self.package[3] = 42
        except TypeError:
            pass
        self.package.record_file('passwd', "/etc/passwd")
        self.assertEqual(len(self.package), 2)

    def test_fsck_nonexistent_file(self):
        self.package.record_file('passwd', "/etc/passwd")
        os.remove(os.path.join(self.sandbox, "files", "passwd"))
        self.assertRaises(InvalidPackageError, self.package.fsck)

    def test_fsck_extra_file(self):
        open(os.path.join(self.sandbox, "files", "passwd"), 'wb').close()
        self.assertRaises(InvalidPackageError, self.package.fsck)


# test_fsck_*


if __name__ == '__main__':
    unittest.main()
