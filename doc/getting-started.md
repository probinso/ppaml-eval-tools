% Getting started with the PPAML client tools
% Benjamin Barenblat
% February 2014

<!-- getting-started.md – basic documentation for ppaml_client
Copyright (C)  2014  Galois, Inc.

This document is written in Pandoc-flavored Markdown.  Have a look at
<http://johnmacfarlane.net/pandoc/>. -->

Copyright ©  2014  Galois, Inc.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

  1. Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.
  2. Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.
  3. Neither Galois’s name nor the names of other contributors may be used to
     endorse or promote products derived from this documentation without
     specific prior written permission.

**This documentation is provided by Galois and other contributors “as is” and
any express or implied warranties, including, but not limited to, the implied
warranties of merchantability and fitness for a particular purpose are
disclaimed.  In no event shall Galois or other contributors be liable for any
direct, indirect, incidental, special, exemplary, or consequential damages
(including, but not limited to, procurement of substitute goods or services;
loss of use, data, or profits; or business interruption) however caused and on
any theory of liability, whether in contract, strict liability, or tort
(including negligence or otherwise) arising in any way out of the use of this
documentation, even if advised of the possibility of such damage.**


# Introduction #

The PPAML client tools are a set of libraries and scripts that allow [PPAML][]
TA2–4 teams to evaluate their own probabilistic programming systems in the same
way that we will at Galois.


# Installing the tools #

As with all research software, the most difficult part of the system is simply
installing it.  I’ve tested the installation procedure on both
[Debian GNU/Linux][Debian] v7.4 (“wheezy”) and [OS X][] v10.9 (“Mavericks”),
but it should work on any GNU/Linux system or any recent version of OS X.
Please read this entire section before beginning the installation, as you may
have to make decisions early in the installation process whose effects will
only become apparent later.

Your goal is to set up your system such that

  - Python 2.6 or 2.7; 
  - the [PyPI][]-hosted packages [argparse][], [configobj][], [lockfile][],
    [procfs][], [psutil][], and [validate][]; and
  - the `ppaml` tool

are all installed and accessible.  Many ways of doing so exist – far too many
for me to cover in a simple installation document.  I’ll cover the most common
procedure, but you should feel free to deviate from it.  If you get stuck,
[send me mail](mailto:bbarenblat@galois.com), and I’ll help you free yourself.


## Python ##

Many systems already have Python 2.6 or 2.7 installed.  On those systems that
do not, you can install it through your system’s package manager or by
[downloading it](http://python.org/download/releases/2.7.6/).  Please make sure
that the version of Python you install matches the word size of your operating
system – 32-bit systems need 32-bit Python, and 64-bit systems need 64-bit
Python.

If you want to run the extended example, you’ll need [SciPy][].  Installing
SciPy on OS X is nontrivial; consider installing [Anaconda][] (a distribution
of Python 2.7 targeted at scientific computing), which has SciPy built in.  If
you install Anaconda, you’ll need to restart your open terminals; the installer
mutates some dotfiles, and you need to pick up those changes.


## PyPI-hosted packages ##


### Installing pip ###

While it’s possible to download and install each of these packages manually,
[pip][] will make your life much easier.  To determine if you have pip, try
running

    % pip --version

in a terminal; if you get something like `pip 1.1 from
/usr/lib/python2.7/dist-packages (python 2.7)`, then you have pip.

If you don’t have pip, you should install it.  If you’re on GNU/Linux, install
the relevant pip package (on Debian, python-pip).  If you’re on OS X and
installed Anaconda, then you should have pip already.  In any case, though, you
can always [download pip](https://pypi.python.org/pypi/pip#downloads) from
PyPI, extract it, and run the Distutils script.

    % cd pip-*
    % python setup.py install --user

Where pip gets installed is OS-dependent:

  - On GNU/Linux, pip’s binaries will be installed in `~/.local/bin`, and pip’s
    libraries will be installed in
      - `~/.local/lib/python2.7/site-packages` (if you’re using Python 2.7) or
      - `~/.local/lib/python2.6/site-packages` (if you’re using Python 2.6).

  - On OS X, pip’s binaries will be installed in
      - `~/Library/Python/2.7/bin` (if you’re using Python 2.7) or
      - `~/Library/Python/2.6/bin` (if you’re using Python 2.6),

    and pip’s libraries will be installed in
      - `~/Library/Python/2.7/lib/python/site-packages` (if you’re using Python
        2.7) or
      - `~/Library/Python/2.6/lib/python/site-packages` (if you’re using Python
        2.6).

You can override these locations by passing the `--prefix` option to `setup.py
install`.  In any case, ensure that the directory containing the binaries is in
your `PATH` and the directory containing the libraries is in your `PYTHONPATH`.


### Installing the packages ###

With pip installed, you can run

    % pip install --user argparse configobj lockfile procfs psutil validate

Again, you can pass `--prefix` to change where the libraries get installed; you
may need to set `PYTHONPATH` as in the previous section.


## `ppaml` ##

`ppaml` is not in PyPI, but you can still install it using pip.

    % pip install --user ppaml-*.tar.bz2

The usual instructions regarding `--prefix`, `PATH`, and `PYTHONPATH` apply.










<!-- [ppamltracer][] has two components: a C library and Python bindings. -->



<!-- [ppamltracer][] isn’t in PyPI, but you can still install it using pip. -->





<!--   - the [ppamltracer][] package and its associated Python bindings; and -->

<!-- If you don’t have it -->
<!-- installed, though, you can install it either through your system’s package manager -->






<!--    1. Would you like to evaluate a program?  If not, then you’re in the wrong -->
<!--       place, and you need to find other software to do what you want. -->
<!--       Otherwise, proceed to step X. -->
<!--    2. Do you have [Python][] 2.6 or 2.7 installed on your system?  If so, skip -->
<!--       to step X; otherwise, proceed to step X. -->
<!--    3. Install Python 2.6 or 2.7 in whatever way you prefer.  Reasonable ways -->
<!--       include `aptitude`, `apt-get`, `yum`, `dpkg`, `rpm`, `port`, `brew`, -->
<!--       `fink`, `emerge`, and `./configure;make install`.  When you are done, -->
<!--       proceed to step X. -->
<!--    4. Would you like to work through an example  -->



<!-- Currently, the tools are compatible with Python 2.6 and 2.7.  You’ll first need -->
<!-- to install dependencies – namely, -->

<!--   - [argparse](https://pypi.python.org/pypi/argparse) (necessary only if you -->
<!--     have Python 2.6) -->
<!--   - [configobj](https://pypi.python.org/pypi/configobj/4.7.2) -->
<!--   - [lockfile](https://pypi.python.org/pypi/lockfile) -->
<!--   - [procfs](https://pypi.python.org/pypi/procfs) -->
<!--   - [psutil](https://pypi.python.org/pypi/psutil) -->
<!--   - [validate](https://pypi.python.org/pypi/validate) -->

<!-- You can install the packages manually, but [pip][] (the Python package manager) -->
<!-- will make your life much happier. -->

<!-- <\!-- TODO: This code overflows its allocated space in the HTML version.  How do -->
<!-- we deal with that? -\-> -->

<!--     % pip install --user argparse configobj lockfile procfs psutil validate -->

<!-- This installs the required packages to `~/.local/lib`.  If you’re root, you can -->
<!-- leave off the `--user` to install them to `/usr/local/lib`.  If you’d rather -->
<!-- install the packages somewhere other than `~/.local/lib`, you can use the -->
<!-- `--target` option to `pip`; you’ll need to set `PYTHONPATH` correctly. -->

<!-- Once the dependencies are in place, you can actually install the package. -->

<!--     # python setup.py install --user -->

<!-- Again, this installs the package to `~/.local/lib` (and the executable to -->
<!-- `~/.local/bin`).  Make sure those locations are in your `PATH`. -->


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


## Installing dependencies ##

Our example requires a couple dependencies beyond what got installed earlier.
Notably, it needs [SciPy][].  If you installed Anaconda earlier, you have
SciPy; otherwise, fire up your operating system package manager and install it,
or download and install it manually.

The example also requires [libotf][] and [ppamltracer][], which you should
install in that order.  If you’re on GNU/Linux, there’s a good chance libotf is
packaged for your system (on Debian, install libopen-trace-format-dev); in any
case, though, both libraries follow the standard `./configure; make; make
install` procedure.  If you choose to install them into a prefix, make sure you
set `PATH`, `LIBRARY_PATH`, `LD_LIBRARY_PATH` (or `DYLD_LIBRARY_PATH`), and
`C_INCLUDE_PATH` to pick up the files installed by the libraries.

Finally, the example requires the Python bindings for ppamltracer, located in
the `bindings/python` subdirectory of the ppamltracer distribution.  You can
install the bindings with pip.

    % cd bindings/python
    % pip install --user .


## Data collection ##

With the dependencies in place, you can proceed to the example.  Like `ppaml`
and the associated library, the example is a Python script compatible with
Python 2.6 or 2.7.  Running it yields a nice usage message.

    % cd wherever_you_unpacked/ppaml-*
    % example="`pwd`"/example
    % mkdir sandbox
    % cd sandbox

    % cp -a "$example"/{csv_helper,slam,slamutil,test-slamutil}.py .
    % python slam.py
    USAGE: slam.py END_TIME INPUT_DATA_DIR OUTPUT_DATA_DIR

Unfortunately, the usage message doesn’t have quite all the documentation we
need, for `slam.py` uses the [ppamltracer][] tracing library, which expects an
environment variable with a trace destination.  Fortunately, that’s easy to
specify, and so we can pretty easily try out `slam.py` on ten seconds of data.
The data, [1_straight.tar.bz2](http://ppaml.kitware.com/midas/item/4388), come
from MIDAS.

    % tar xvf 1_straight.tar.bz2
    1_straight/
    [… other output elided …]
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

Looks good.

Unfortunately, the interface slam.py presents is not the interface that `ppaml`
expects.  When the time comes, `ppaml` will execute the artifact executable as

    /path/to/artifact_executable config_file input_dir output_path log_path

Furthermore, `ppaml` does not create `output_path` and `log_path`; it merely
reserves the names.  The executable itself is responsible for creating either
files or directories at those paths.  However, a bit of shell can easily bridge
the gap between `ppaml` and slam.py.

    % tee <"$example"/run_slam run_slam
    #!/bin/bash -eu
    if (( $# != 4 )); then
        printf "Usage: %s config_file input_dir output_path log_path\n" "$0" >&2
        exit 1
    fi
    mkdir "$3"
    exec python "$(dirname "$0")"/slam.py 10 "$2" "$3"
    % chmod +x run_slam

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
    ├── files
    │   ├── output
    │   │   ├── slam_out_landmarks.csv
    │   │   └── slam_out_path.csv
    │   └── trace
    │       ├── trace.0.def
    │       ├── trace.1.events
    │       └── trace.otf
    └── index.json

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
    ├── files/
    │   ├── file_1.txt
    │   ├── file_2.dat
    │   └── file_3.gif
    └── index.json

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
