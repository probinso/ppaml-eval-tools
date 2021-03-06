#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

setup(
  name         = 'peval',
  version      = '1.0',
  description  = 'Program Evaluator Harness',
  author       = 'Philip Robinson',
  author_email = 'probinson@galois.com',
  license      = 'MIT',

  classifiers  = [
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    ],

  url          = 'https://www.github.com/GaloisInc/ppaml-eval-tools/',
  packages     = ['peval'],
  entry_points = { # enable cmd-line access
    "console_scripts": [
      'peval = peval.peval:main',
    ]
    },
  scripts = ['scripts/driver-peval.py', 'scripts/evil-peval.py'],
  package_data={'peval': ['db_init.sql']},
  data_files=[('share/%s/%s' % ('peval', x[0]), map(lambda y: x[0]+'/'+y, x[2])) for x in os.walk('example/')],
  long_description=read('README.md'),
  install_requires = [
    'argcomplete',
    'argparse',
    'datetime',
    'pony',
    'psutil',
    'pyxdg',
  ]
     )

