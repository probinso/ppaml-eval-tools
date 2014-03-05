# setup.py -- Distutils install script for PPAML client scripts
# Copyright (C) 2014  Galois, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at
# your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# To contact Galois, complete the Web form at
# <http://corp.galois.com/contact/> or write to Galois, Inc., 421
# Southwest 6th Avenue, Suite 300, Portland, Oregon, 97204-1622.


# Check to ensure this script is running on a version of Python that
# won't cause issues down the line.  This code needs to be compatible
# with both Python 2 and 3.
import sys

if sys.version < '2.6':
    # Use sys.stderr.write instead of print, because print's syntax is
    # incompatible between 2 and 3.
    sys.stderr.write(
        "ppaml_client will not function on Python versions before 2.6.\n")
    sys.exit(1)
elif '3' < sys.version:
    sys.stderr.write("ppaml_client will not function on Python 3.\n")
    sys.exit(1)

# From this point forward, code should be written for Python 2.6.


from distutils.core import setup


# Check for dependencies.
def missing_dependency(description):
    """Report a missing dependency and exits with exit status 2."""
    print >> sys.stderr, "ppaml requires " + description
    sys.exit(2)


def require(module, version=None):
    """Attempts to import a module, exiting if it fails."""
    module_description = (module +
                          ("" if version is None
                              else " >={0}".format(version)))
    try:
        exec 'import ' + module
    except ImportError:
        missing_dependency(module_description)
    else:
        if version is not None and eval(module).__version__ < version:
            missing_dependency(module_description)


require('argparse', '1.1')
require('configobj', '4.7')
require('lockfile')
require('psutil', '0.5')
require('validate', '1.0')


# Run the setup program.
setup(
    name='ppaml_client',
    version='0.1.0',
    description="PPAML client scripts",
    author="Benjamin Barenblat",
    author_email="bbarenblat@galois.com",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        ],
    packages=['ppaml_client'],
    scripts=['scripts/ppaml'],
    data_files=[
        ('doc', ['doc/getting-started.html']),
        ('example', [
                'example/csv_helper.py',
                'example/README',
                'example/run.conf.1',
                'example/run.conf.2',
                'example/run_slam',
                'example/slam_eval',
                'example/slam.py',
                'example/slamutil.py',
                'example/test-slamutil.py',
                ]),
        ],
    )


# Local Variables:
# coding: us-ascii
# End:
