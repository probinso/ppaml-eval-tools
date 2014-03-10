# setup.py -- Distutils install script for PPAML client scripts
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
    version='0.1.1',
    description="PPAML client scripts",
    author="Benjamin Barenblat",
    author_email="bbarenblat@galois.com",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
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
