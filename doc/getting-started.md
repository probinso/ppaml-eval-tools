% Getting started with the PPAML client tools
% Galois, Inc.
% March 2014

# Introduction #

The PPAML client tools are a set of libraries and scripts that allow [PPAML][]
TA2–4 teams to evaluate their own probabilistic programming systems in the same
way that we will at Galois.


# Installing the tools #

As with all research software, the most difficult part of the system is simply
installing it.  This installation procedure has been tested with:

 - Debain Linux v7.4
 - Fedora Linux v20
 - Apple OS X 10.9

The dependency set of the tools was chosen to reflect those available within
most common Linux distributions released since 2011.  

Please read this entire section before beginning the installation, as you may
have to make decisions early in the installation process whose effects will
only become apparent later.

Your goal is to set up your system such that

  - Python 2.6 or 2.7; 
  - the PyPI-hosted packages argparse, configobj, lockfile,
    procfs, psutil, sqlalchemy, pyxdg, and validate;
  - the `ppaml` tool; and
  - the `ppamltracer` library

are all installed and accessible.  

If you get stuck, send us mail (ppaml-support@community.galois.com),
and we will assist you in identifying the problem and working through
it.

## Download Software ##

Before starting, please make sure you have the following tar archives
downloaded:

  - OTF-1.12.4salmon.tar.gz

    This can be downloaded from the OTF web page at http://bit.ly/PZ32Eg

  - ppamltracer-X.tar.gz 

    This can be downloaded from the PPAML-Tracer web page at http://FILLMEIN/

  - ppamltools-X.tar.gz

    This can be downloaded from the PPAML-Tools web page at http://FILLMEIN/

Where X is the current version of the corresponding tar archive.  We are
assuming that you have downloaded these to the Downloads directory in
your home directory.  If you have placed them elsewhere, make sure to
adjust the commands that refer to the archives later.

You should also download one of the data sets for challenge problem #1
from the PPAML MIDAS site.  We recommend using the simplest data set,
1_straight, as the test case for this tutorial.  This archive is
assumed to also reside in your Downloads directory as:

  - 1_straight.tar.bz2

    This can be downloaded from the PPAML MIDAS page at http://ppaml.kitware.com/midas/item/4388

## System Prerequisites ##

In order to start, you must have a set of prerequisites installed on your
machine that are necessary to build the PPAML tools as well as their
direct dependencies.  If you are installing on a machine that you already
use for active development, it is quite likely that many (or all) of these
dependencies are already installed.

### Debian/Ubuntu Linux ###

If installing on a Debian (or Ubuntu) system, the following packages should
be installed via the distribution package manager apt:

 - autoconf
 - automake
 - libtool
 - autotools-dev
 - pkg-config
 - autoconf-archive
 - build-essential
 - python
 - python-pip
 - python-dev
 - python-scipy

These can be installed via the following command executed as root (or via
sudo from a user account):

    % apt-get install autoconf autotools-dev autoconf-archive automake \
                      libtool pkg-config build-essential \
                      python python-pip python-dev python-scipy

During the installation of these packages, additional dependencies will
automatically be installed by the package manager.

### RedHat/Fedora/Centos Linux ###

A similar process is used on a RedHat (or Fedora and Centos) system.  The set 
of dependencies are:

 - autoconf
 - libtool
 - gcc
 - gcc-c++
 - autoconf-archive
 - python-devel
 - python-pip
 - scipy

These can be installed using the yum package manager via:

    % yum install autoconf libtool gcc gcc-c++ autoconf-archive \
                  python-devel python-pip scipy

### Alternative Python ###

An alternative method for obtaining Python and the necessary dependencies is
to use a pre-built Python distribution intended for use in technical computing.
The Anaconda Python distribution from Continuum IO has been tested with the
PPAML tools and is available for Linux, MacOS X, and Windows.  If you are working
on multiple systems and wish to have a consistent Python environment, the use of
a package such as Anaconda is advantageous since it will provide a consistent set of
packages and versions across all of the platforms you install it on.

## Python packages ##

A number of Python packages now must be installed via pip.  Installing python
packages can be done either system-wide or within a users home directory.
In instances where the user does not have adminstrative priviledges, we 
highly recommend installing locally within the home directory.  The example
commands in this section are written assuming that installation will be
in the home directory.  If you wish to install system-wide, the "--user"
command line option can be omitted in the examples where it appears.

The following python packages are required by the PPAML tools:

 - argparse
 - configobj
 - lockfile
 - procfs
 - psutil
 - sqlalchemy
 - validate
 - pyxdg

These can be installed via pip, such as:

    % pip install --user argparse
    % pip install --user configobj
      [ and so on ... ]

If any of these fail, please check the error message to determine whether or not your
system is missing a dependency outside of python, such as a C or C++ library.
Contact the TA1 PPAML team if you run into problems installing the Python dependencies
and cannot resolve errors on your own.

# Building and installing tools #

## Sandbox creation ##

The best way to work with the PPAML tools is to create a sandbox in
your home directory or other private location where you can unpack
the necessary archives and data files.  In this tutorial, we will
assume that the sandbox is the ``ppaml'' directory in your home
directory.

    % mkdir ~/ppaml
    % mkdir ~/ppaml/installTree

## `ppaml` ##

The first step is to install the PPAML tools.  Start by un-archiving
them in the sandbox directory that you created.  We will need to
access files to run through the example contained in this archive
later, so keep the directory after you do the installation.

    % cd ~/ppaml
    % tar xzvf ~/Downloads/ppamltools-X.tar.gz
    % cd ppamltools-X

The PPAML tools are easy to install in your home directory using pip.

    % pip install --user .

If the directory that pip installs binaries is not in your path, such
as ~/.local/bin, then you must add it now.

    % export PATH=$PATH:~/.local/bin

## ``ppamltracer'' ##

The PPAML evaluation tools provide a tracing library that can be used
by probabilistic programs to measure their performance at a finer
granularity than simply recording the overall wallclock execution
time.  The tracing library is optional for use by TA2-4 teams in their
official evaluation. The example described in this tutorial for the
Challenge Problem 1 solution requires the tracing library to
illustrate how one would apply it to your own probabilistic programs.

Installation of the PPAML tracing library has a single prerequisite:
the Open Trace Format (OTF) library that was downloaded earlier.  This
library must be compiled from sources.

The first step is to build and install libotf.  Un-tar the libotf file
into the sandbox and enter the directory.

    % tar xzvf ~/Downloads/OTF-1.12.4salmon.tar.gz
    % cd OTF-1.12.4salmon

We now configure it and install into the sandbox:

    % ./configure --prefix=$HOME/ppaml/installTree

Build and install it with the following two commands:

    % make
    % make install

Now, we need to set up a couple of environment variables that are used by the PPAML
tools to find the shared library that we just built.  Be sure to set both of
these variables:

    % export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$HOME/ppaml/installTree/lib
    % export LIBRARY_PATH=$LIBRARY_PATH:$HOME/ppaml/installTree/lib

If you are on OSX, you need to set the DYLD_LIBRARY_PATH instead of LD_LIBRARY_PATH.
The value that you assign to the variable is the same as above.

These will need to be set each time you run the PPAML tools, so be sure to add them
to your ~/.bashrc or other script that is used to set up your environment.

Now, unpack and configure the ppamltracer library.  

    % cd ~/ppaml
    % tar xzvf ~/Downloads/ppamltracer-X.tar.gz
    % cd ppamltracer-X

We will install to the same place we installed libotf, and must
indicate where the configure script can find the otfconfig program.

    % OTFCONFIG=$HOME/ppaml/installTree/bin/otfconfig ./configure --prefix=$HOME/ppaml/installTree

Now we can build and install:

    % make
    % make install

At this point, we will need to also install the ppamltracer python bindings.  All language 
bindings are provided in the bindings subdirectory of the ppamltracer archive.  These can
be installed via pip:

    % cd bindings/python
    % pip install --user .

We now have all of the prerequisite software installed for both the PPAML toolchain as well
as the example solution to Challenge Problem 1.

# Basic usage #

Now that you’ve got everything installed, you can actually use the PPAML tools.
To keep the system extensible and to avoid polluting your `PATH`, we’ve bundled
a number of PPAML-related tasks into a single, top-level command.  (This
concept should be quite familiar to users of [Git][] or [Mercurial][].)  To
ensure that everything was installed correctly, try running `ppaml version`,
which prints the version of the `ppaml` executable and library to standard
output, or `ppaml help`, which prints a usage message.

If `ppaml` ever propagates an exception back to the console, then
congratulations!  You’ve found a bug.  Please
[send me](mailto:bbarenblat@galois.com) the invocation of `ppaml` that you
used, along with the exception traceback, and we’ll do everything in our power
to get it fixed in a timely fashion.


# Extended example: Evaluating an artifact #

When we speak of an artifact, we mean both the source code of a
machine-learning solution and the executable that source code describes.  The
`ppaml` tools are all about evaluating artifacts, which proceeds in two steps:

  1. Data collection.  This means running the executable, watching CPU and RAM
     usage, and collecting its output.

  2. Correctness evaluation.  This means running some _evaluator_, which
     compares the output with a reference solution to produce a series of
     numerical scores.

The end result is a [_package_](#package-format), a standardized file system
tree, which can be trivially archived, compressed, and transferred.  To
illustrate artifact evaluation, let’s consider a not-so-hypothetical solution
for challenge problem 1: a Kalman filter.  All the files used in this example
(modulo one data set, which needs to be downloaded from MIDAS) are in the
`example` directory of this distribution.


## Data collection ##

The evaluation process is best performed by creating a working directory where
you place the artifact to evaluate and any related data files.

    % mkdir ~/ppaml-sandbox
    % cd ~/ppaml-sandbox

In this document, we will work through the CP1 solution that is included with the
PPAML tools distribution.  Copy the files from the example/ subdirectory of the
tools distribution to your sandbox:

    % cp -a (location of PPAML tools)/example/{csv_helper,slam,slamutil,test-slamutil}.py .
    % python slam.py
    USAGE: slam.py END_TIME INPUT_DATA_DIR OUTPUT_DATA_DIR

This example is instrumented with the PPAML tracing library, so
invocation requires us to indicate where traces are to be stored when
the code is run.  Before we can try it out, download one of the data
sets that are provided for Challenge Problem 1, such as the basic
straight path set.  The data,
[1_straight.tar.bz2](http://ppaml.kitware.com/midas/item/4388), come
from MIDAS.

    % tar xvf ~/Downloads/1_straight.tar.bz2
    1_straight/
    [... other output elided ...]
    % mkdir /tmp/slam_out
    % PPAMLTRACER_TRACE_BASE=/tmp/slam_out/trace python slam.py 10 1_straight/data/ground /tmp/slam_out
    % ls /tmp/slam_out
    slam_out_landmarks.csv
    slam_out_path.csv
    trace.otf
    trace.0.def
    trace.1.events
    % tail -n 3 /tmp/slam_out/slam_out_path.csv
    9.51017,-5.41752988766,0.672891535838
    9.720175,-5.39463311078,0.684530275571
    9.93518,-5.38026736461,0.666373478798

The interface that slam.py presents is not the interface that `ppaml`
expects.  This is likely to be true with most challenge problem solutions, as
each solution likely adopts its own parameter set and parameter passing
style.  To solve this, each solution must be wrapped with a small layer of
shell or Python code that translates the argument set that the PPAML tools
present to those that are used by the specific probabalistic program.  The
SLAM example used here is a good model for how to approach this problem.

The basic calling pattern that PPAML assumes is:

    /path/to/artifact_executable config_file input_dir output_path log_path

`ppaml` does not create `output_path` and `log_path`; it merely
reserves the names.  The user or executable itself is responsible for creating either
files or directories at those paths.  However, a bit of shell can easily bridge
the gap between `ppaml` and slam.py.  We can create a shell script called "run_slam"
that contains the following:

    #!/bin/bash -eu
    if (( $# != 4 )); then
        printf "Usage: %s config_file input_dir output_path log_path\n" "$0" >&2
        exit 1
    fi
    mkdir "$3"
    exec python "$(dirname "$0")"/slam.py 10 "$2" "$3"

Be sure to make this file executable using chmod.

Now it’s time to write a run configuration file.  This master configuration
file drives all the client tools.  To get a configuration file skeleton, go
ahead and run

    % ppaml init

to generate a skeleton `run.conf`, and have a look.  The fields are fairly
simple:

  - The `artifact` section describes the artifact you’re trying to run.

      - `paths` identifies the files used in the artifact.  The client scripts
        will use these paths to generate a unique identifier for the artifact,
        so it is important that you list all of them!  The scripts assume that
        the first file listed is the artifact executable.

      - `config` specifies the artifact configuration file, if any.  If your
        PPS requires a configuration file, this is the place to put it.  This
        field is optional; if you omit it, `ppaml` will pass `/dev/null` to the
        artifact executable.

      - `input` specifies the input path.

  - The `package` section describes attributes related to packaging run data.
    Currently, it supports only one key – `base` – which sets where the output
    data from the executable will go.

  - The `evaluation` section tells `ppaml` how to evaluate a run.  Don’t worry
    about it just yet – we’ll look at it again in a minute.

All paths are specified relative to the directory containing the configuration
file, and `~` will get expanded to `$HOME`, but no other environment variable
expansion occurs.

For this example, you should set

  - `paths` to `run_slam, *.py`,
  - `config` to `/dev/null` (or just comment it out),
  - `input` to `1_straight/data/ground`, and
  - `base` to `/tmp/my_runs` (or some other directory of your choice).

Comment out the `evaluation` section for now.

We can now actually run the executable.

    % ppaml run run.conf
    /tmp/my_runs/001

The `ppaml run` script runs the artifact executable according to the specified
configuration file, all the while monitoring system load, memory usage, and
other useful metrics for evaluation.  When the executable is finished, `ppaml
run` bundles all the data (including the executable output) into a package,
stores it in a directory under `base`, and prints that directory name to the
console.

    % tree /tmp/my_runs/001
    /tmp/my_runs/001
    +-- files
    |   +-- output
    |   |   +-- slam_out_landmarks.csv
    |   |   `-- slam_out_path.csv
    |   `-- trace
    |       +-- trace.0.def
    |       +-- trace.1.events
    |       `-- trace.otf
    `-- index.json

    2 directories, 4 files


## Correctness evaluation ##

Now that we’ve done a run or three, it’s time to evaluate how well our results
perform.  Our Kalman-filter SLAM implementation comes with an evaluator, which
(not coincidentally) expects exactly the command-line arguments `ppaml
evaluate` will pass it – namely,

  - the output file or directory generated by the run (in our ongoing example,
    `/tmp/my_runs/001/files/output`)

  - whatever ground-truth data path we specify in our configuration file

  - where the evaluator should place its results

Like the runner, the evaluator must create either a file or directory at the
specified output path.

    % cp -a "$example"/slam_eval .

We now need to update our configuration file so it can tell `ppaml` which file
is the evaluator.  Open up `run.conf` again, and check out the `evaluation`
section, which has two directives:

  - `evaluator`, like `paths` in the `artifact` section, is a list of all files
    which are part of the evaluator.

  - `ground_truth` points to a directory containing the ground truth data files
    against which the run results will be compared; the contents of this key
    get passed as the second argument to the evaluator.

For this example, set

  - `evaluator` to `slam_eval` and
  - `ground_truth` to `1_straight`.

Now we can run the evaluator.

    % ppaml evaluate run.conf 1

Note that we must specify an extra argument – `1` – to `ppaml evaluate`; this
identifies the run inside the output directory (`/tmp/my_runs`).  We don’t need
leading zeros, though `ppaml evaluate` won’t complain if we include them.

Once the evaluator finishes, `ppaml evaluate` will mutate the run package to
include the evaluator output.


# Package format #

This section is really an appendix; if all you want to do is evaluate
artifacts, it’s not important that you read it.  If, on the other hand, you
want to see the results of a run, you need to know a bit about how packages are
structured.

A package is effectively a userspace file system.  It consists of an _index_
and any number of _files_, arranged into a directory tree.  For example, a PPS
run might translate to the following package:

    /package/
    +-- files/
    |   +-- file_1.txt
    |   +-- file_2.dat
    |   `-- file_3.gif
    `-- index.json


The index is a single file named `index.ext`, where `ext` is some extension.
The extension determines the format of the file.  Valid extensions are

extension  format
---------  ------
       db  [SQLite][] database
     json  ASCII-JSON

Here, ‘ASCII-JSON’ means a subset of JSON where all keys are ASCII strings.


## ASCII-JSON indices ##

An ASCII-JSON index contains a single JSON object with three keys.

  - The `"version"` key maps to a single integer which indicates the version of
    the standard to which the index adheres.  The current standard is version
    3.
  - The `"data"` key maps to a key-value store.  Values may be any valid JSON
    type.
  - The `"files"` key maps to a dictionary of file names.  Each value is the
    name of a file in the `files` directory.

No key may appear in both the `"data"` and `"files"` sections.


## SQLite indices ##

The schema for SQLite indices remains to be standardized.  Check back later.

## License and Copyright ##

Copyright ©  2014  Galois, Inc.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.
  3. Neither Galois’s name nor the names of other contributors may be used to
     endorse or promote products derived from this documentation without
     specific prior written permission.

**This documentation is provided by Galois and other contributors “as
is” and any express or implied warranties, including, but not limited
to, the implied warranties of merchantability and fitness for a
particular purpose are disclaimed.  In no event shall Galois or other
contributors be liable for any direct, indirect, incidental, special,
exemplary, or consequential damages (including, but not limited to,
procurement of substitute goods or services; loss of use, data, or
profits; or business interruption) however caused and on any theory of
liability, whether in contract, strict liability, or tort (including
negligence or otherwise) arising in any way out of the use of this
documentation, even if advised of the possibility of such damage.**





<!-- References -->

[Anaconda]: https://store.continuum.io/cshop/anaconda/
[argparse]: https://pypi.python.org/pypi/argparse
[configobj]: https://pypi.python.org/pypi/configobj
[Debian]: httphttp://www.debian.org/
[Git]: http://git-scm.com/
[JSON]: http://json.org/
[libotf]: http://tu-dresden.de/die_tu_dresden/zentrale_einrichtungen/zih/forschung/projekte/otf
[lockfile]: https://pypi.python.org/pypi/lockfile
[Mercurial]: http://mercurial.selenic.com/
[OS X]: https://www.apple.com/osx/
[pip]: https://pypi.python.org/pypi/pip
[PPAML]: http://ppaml.galois.com/
[ppamltracer]: https://github.com/galoisinc/ppamltracer
[procfs]: https://pypi.python.org/pypi/procfs
[psutil]: https://pypi.python.org/pypi/psutil
[Python]: http://python.org/
[PyPI]: https://pypi.python.org/
[SciPy]: http://scipy.org/
[SQLite]: https://sqlite.org/
[validate]: https://pypi.python.org/pypi/validate
