% Getting started with the PPAML client tools
% Benjamin Barenblat
% February 2014

<!-- getting-started.md – basic documentation for ppaml_client
Copyright (C)  2014  Galois, Inc.

This document is written in Pandoc-flavored Markdown.  Have a look at
<http://johnmacfarlane.net/pandoc/>. -->

Copyright ©  2014  Galois, Inc.

Permission is granted to copy, distribute and/or modify this document under the
terms of the GNU Free Documentation License, Version 1.3 or any later version
published by the Free Software Foundation; with no Invariant Sections, no
Front-Cover Texts, and no Back-Cover Texts.  A copy of the license is included
in the section entitled
"[GNU Free Documentation License](#gnu-free-documentation-license)".


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


# GNU Free Documentation License #

Version 1.3, 3 November 2008

Copyright © 2000, 2001, 2002, 2007, 2008 Free Software Foundation,
Inc. <<http://fsf.org/>>

Everyone is permitted to copy and distribute verbatim copies of this license
document, but changing it is not allowed.


## 0. Preamble ##

The purpose of this License is to make a manual, textbook, or other functional
and useful document “free” in the sense of freedom: to assure everyone the
effective freedom to copy and redistribute it, with or without modifying it,
either commercially or noncommercially.  Secondarily, this License preserves
for the author and publisher a way to get credit for their work, while not
being considered responsible for modifications made by others.

This License is a kind of “copyleft”, which means that derivative works of the
document must themselves be free in the same sense.  It complements the GNU
General Public License, which is a copyleft license designed for free software.

We have designed this License in order to use it for manuals for free software,
because free software needs free documentation: a free program should come with
manuals providing the same freedoms that the software does.  But this License
is not limited to software manuals; it can be used for any textual work,
regardless of subject matter or whether it is published as a printed book.  We
recommend this License principally for works whose purpose is instruction or
reference.


## 1. Applicability and definitions ##

This License applies to any manual or other work, in any medium, that contains
a notice placed by the copyright holder saying it can be distributed under the
terms of this License.  Such a notice grants a world-wide, royalty-free
license, unlimited in duration, to use that work under the conditions stated
herein.  The “Document”, below, refers to any such manual or work.  Any member
of the public is a licensee, and is addressed as “you”.  You accept the license
if you copy, modify or distribute the work in a way requiring permission under
copyright law.

A “Modified Version” of the Document means any work containing the Document or
a portion of it, either copied verbatim, or with modifications and/or
translated into another language.

A “Secondary Section” is a named appendix or a front-matter section of the
Document that deals exclusively with the relationship of the publishers or
authors of the Document to the Document’s overall subject (or to related
matters) and contains nothing that could fall directly within that overall
subject.  (Thus, if the Document is in part a textbook of mathematics, a
Secondary Section may not explain any mathematics.)  The relationship could be
a matter of historical connection with the subject or with related matters, or
of legal, commercial, philosophical, ethical or political position regarding
them.

The “Invariant Sections” are certain Secondary Sections whose titles are
designated, as being those of Invariant Sections, in the notice that says that
the Document is released under this License.  If a section does not fit the
above definition of Secondary then it is not allowed to be designated as
Invariant.  The Document may contain zero Invariant Sections.  If the Document
does not identify any Invariant Sections then there are none.

The “Cover Texts” are certain short passages of text that are listed, as
Front-Cover Texts or Back-Cover Texts, in the notice that says that the
Document is released under this License.  A Front-Cover Text may be at most 5
words, and a Back-Cover Text may be at most 25 words.

A “Transparent” copy of the Document means a machine-readable copy, represented
in a format whose specification is available to the general public, that is
suitable for revising the document straightforwardly with generic text editors
or (for images composed of pixels) generic paint programs or (for drawings)
some widely available drawing editor, and that is suitable for input to text
formatters or for automatic translation to a variety of formats suitable for
input to text formatters.  A copy made in an otherwise Transparent file format
whose markup, or absence of markup, has been arranged to thwart or discourage
subsequent modification by readers is not Transparent.  An image format is not
Transparent if used for any substantial amount of text.  A copy that is not
“Transparent” is called “Opaque”.

Examples of suitable formats for Transparent copies include plain ASCII without
markup, Texinfo input format,
L<span class="A">a</span>T<span class="E">e</span>X input format, SGML or XML
using a publicly available DTD, and standard-conforming simple HTML, PostScript
or PDF designed for human modification.  Examples of transparent image formats
include PNG, XCF and JPG.  Opaque formats include proprietary formats that can
be read and edited only by proprietary word processors, SGML or XML for which
the DTD and/or processing tools are not generally available, and the
machine-generated HTML, PostScript or PDF produced by some word processors for
output purposes only.

The “Title Page” means, for a printed book, the title page itself, plus such
following pages as are needed to hold, legibly, the material this License
requires to appear in the title page.  For works in formats which do not have
any title page as such, “Title Page” means the text near the most prominent
appearance of the work’s title, preceding the beginning of the body of the
text.

The “publisher” means any person or entity that distributes copies of the
Document to the public.

A section “Entitled XYZ” means a named subunit of the Document whose title
either is precisely XYZ or contains XYZ in parentheses following text that
translates XYZ in another language.  (Here XYZ stands for a specific section
name mentioned below, such as “Acknowledgements”, “Dedications”,
“Endorsements”, or “History”.)  To “Preserve the Title” of such a section when
you modify the Document means that it remains a section “Entitled XYZ”
according to this definition.

The Document may include Warranty Disclaimers next to the notice which states
that this License applies to the Document.  These Warranty Disclaimers are
considered to be included by reference in this License, but only as regards
disclaiming warranties: any other implication that these Warranty Disclaimers
may have is void and has no effect on the meaning of this License.


## 2. Verbatim copying ##

You may copy and distribute the Document in any medium, either commercially or
noncommercially, provided that this License, the copyright notices, and the
license notice saying this License applies to the Document are reproduced in
all copies, and that you add no other conditions whatsoever to those of this
License.  You may not use technical measures to obstruct or control the reading
or further copying of the copies you make or distribute.  However, you may
accept compensation in exchange for copies.  If you distribute a large enough
number of copies you must also follow the conditions in section 3.

You may also lend copies, under the same conditions stated above, and you may
publicly display copies.


## 3. Copying in quantity ##

If you publish printed copies (or copies in media that commonly have printed
covers) of the Document, numbering more than 100, and the Document’s license
notice requires Cover Texts, you must enclose the copies in covers that carry,
clearly and legibly, all these Cover Texts: Front-Cover Texts on the front
cover, and Back-Cover Texts on the back cover.  Both covers must also clearly
and legibly identify you as the publisher of these copies.  The front cover must
present the full title with all words of the title equally prominent and
visible.  You may add other material on the covers in addition.  Copying with
changes limited to the covers, as long as they preserve the title of the
Document and satisfy these conditions, can be treated as verbatim copying in
other respects.

If the required texts for either cover are too voluminous to fit legibly, you
should put the first ones listed (as many as fit reasonably) on the actual
cover, and continue the rest onto adjacent pages.

If you publish or distribute Opaque copies of the Document numbering more than
100, you must either include a machine-readable Transparent copy along with
each Opaque copy, or state in or with each Opaque copy a computer-network
location from which the general network-using public has access to download
using public-standard network protocols a complete Transparent copy of the
Document, free of added material.  If you use the latter option, you must take
reasonably prudent steps, when you begin distribution of Opaque copies in
quantity, to ensure that this Transparent copy will remain thus accessible at
the stated location until at least one year after the last time you distribute
an Opaque copy (directly or through your agents or retailers) of that edition
to the public.

It is requested, but not required, that you contact the authors of the Document
well before redistributing any large number of copies, to give them a chance to
provide you with an updated version of the Document.


## 4. Modifications ##

You may copy and distribute a Modified Version of the Document under the
conditions of sections 2 and 3 above, provided that you release the Modified
Version under precisely this License, with the Modified Version filling the
role of the Document, thus licensing distribution and modification of the
Modified Version to whoever possesses a copy of it.  In addition, you must do
these things in the Modified Version:

  - A. Use in the Title Page (and on the covers, if any) a title distinct from
    that of the Document, and from those of previous versions (which should, if
    there were any, be listed in the History section of the Document).  You may
    use the same title as a previous version if the original publisher of that
    version gives permission.

  - B. List on the Title Page, as authors, one or more persons or entities
    responsible for authorship of the modifications in the Modified Version,
    together with at least five of the principal authors of the Document (all
    of its principal authors, if it has fewer than five), unless they release
    you from this requirement.

  - C. State on the Title page the name of the publisher of the Modified
    Version, as the publisher.

  - D. Preserve all the copyright notices of the Document.

  - E. Add an appropriate copyright notice for your modifications adjacent to
    the other copyright notices.

  - F. Include, immediately after the copyright notices, a license notice
    giving the public permission to use the Modified Version under the terms of
    this License, in the form shown in the Addendum below.

  - G. Preserve in that license notice the full lists of Invariant Sections and
    required Cover Texts given in the Document’s license notice.

  - H. Include an unaltered copy of this License.

  - I. Preserve the section Entitled “History”, Preserve its Title, and add to
    it an item stating at least the title, year, new authors, and publisher of
    the Modified Version as given on the Title Page.  If there is no section
    Entitled “History” in the Document, create one stating the title, year,
    authors, and publisher of the Document as given on its Title Page, then add
    an item describing the Modified Version as stated in the previous sentence.

  - J. Preserve the network location, if any, given in the Document for public
    access to a Transparent copy of the Document, and likewise the network
    locations given in the Document for previous versions it was based on.
    These may be placed in the “History” section.  You may omit a network
    location for a work that was published at least four years before the
    Document itself, or if the original publisher of the version it refers to
    gives permission.

  - K. For any section Entitled “Acknowledgements” or “Dedications”, Preserve
    the Title of the section, and preserve in the section all the substance and
    tone of each of the contributor acknowledgements and/or dedications given
    therein.

  - L. Preserve all the Invariant Sections of the Document, unaltered in their
    text and in their titles.  Section numbers or the equivalent are not
    considered part of the section titles.

  - M. Delete any section Entitled “Endorsements”.  Such a section may not be
    included in the Modified Version.

  - N. Do not retitle any existing section to be Entitled “Endorsements” or to
    conflict in title with any Invariant Section.

  - O. Preserve any Warranty Disclaimers.

If the Modified Version includes new front-matter sections or appendices that
qualify as Secondary Sections and contain no material copied from the Document,
you may at your option designate some or all of these sections as invariant.
To do this, add their titles to the list of Invariant Sections in the Modified
Version’s license notice.  These titles must be distinct from any other section
titles.

You may add a section Entitled “Endorsements”, provided it contains nothing but
endorsements of your Modified Version by various parties—for example,
statements of peer review or that the text has been approved by an organization
as the authoritative definition of a standard.

You may add a passage of up to five words as a Front-Cover Text, and a passage
of up to 25 words as a Back-Cover Text, to the end of the list of Cover Texts
in the Modified Version.  Only one passage of Front-Cover Text and one of
Back-Cover Text may be added by (or through arrangements made by) any one
entity.  If the Document already includes a cover text for the same cover,
previously added by you or by arrangement made by the same entity you are
acting on behalf of, you may not add another; but you may replace the old one,
on explicit permission from the previous publisher that added the old one.

The author(s) and publisher(s) of the Document do not by this License give
permission to use their names for publicity for or to assert or imply
endorsement of any Modified Version.


## 5.  Combining documents ##

You may combine the Document with other documents released under this License,
under the terms defined in section 4 above for modified versions, provided that
you include in the combination all of the Invariant Sections of all of the
original documents, unmodified, and list them all as Invariant Sections of your
combined work in its license notice, and that you preserve all their Warranty
Disclaimers.

The combined work need only contain one copy of this License, and multiple
identical Invariant Sections may be replaced with a single copy.  If there are
multiple Invariant Sections with the same name but different contents, make the
title of each such section unique by adding at the end of it, in parentheses,
the name of the original author or publisher of that section if known, or else
a unique number.  Make the same adjustment to the section titles in the list of
Invariant Sections in the license notice of the combined work.

In the combination, you must combine any sections Entitled “History” in the
various original documents, forming one section Entitled “History”; likewise
combine any sections Entitled “Acknowledgements”, and any sections Entitled
“Dedications”.  You must delete all sections Entitled “Endorsements”.


## 6. Collections of documents ##

You may make a collection consisting of the Document and other documents
released under this License, and replace the individual copies of this License
in the various documents with a single copy that is included in the collection,
provided that you follow the rules of this License for verbatim copying of each
of the documents in all other respects.

You may extract a single document from such a collection, and distribute it
individually under this License, provided you insert a copy of this License
into the extracted document, and follow this License in all other respects
regarding verbatim copying of that document.


## 7. Aggregation with independent works ##

A compilation of the Document or its derivatives with other separate and
independent documents or works, in or on a volume of a storage or distribution
medium, is called an “aggregate” if the copyright resulting from the
compilation is not used to limit the legal rights of the compilation’s users
beyond what the individual works permit.  When the Document is included in an
aggregate, this License does not apply to the other works in the aggregate
which are not themselves derivative works of the Document.

If the Cover Text requirement of section 3 is applicable to these copies of the
Document, then if the Document is less than one half of the entire aggregate,
the Document’s Cover Texts may be placed on covers that bracket the Document
within the aggregate, or the electronic equivalent of covers if the Document is
in electronic form.  Otherwise they must appear on printed covers that bracket
the whole aggregate.


## 8. Translation ##

Translation is considered a kind of modification, so you may distribute
translations of the Document under the terms of section 4.  Replacing Invariant
Sections with translations requires special permission from their copyright
holders, but you may include translations of some or all Invariant Sections in
addition to the original versions of these Invariant Sections.  You may include
a translation of this License, and all the license notices in the Document, and
any Warranty Disclaimers, provided that you also include the original English
version of this License and the original versions of those notices and
disclaimers.  In case of a disagreement between the translation and the
original version of this License or a notice or disclaimer, the original
version will prevail.

If a section in the Document is Entitled “Acknowledgements”, “Dedications”, or
“History”, the requirement (section 4) to Preserve its Title (section 1) will
typically require changing the actual title.


## 9. Termination ##

You may not copy, modify, sublicense, or distribute the Document except as
expressly provided under this License.  Any attempt otherwise to copy, modify,
sublicense, or distribute it is void, and will automatically terminate your
rights under this License.

However, if you cease all violation of this License, then your license from a
particular copyright holder is reinstated (a) provisionally, unless and until
the copyright holder explicitly and finally terminates your license, and (b)
permanently, if the copyright holder fails to notify you of the violation by
some reasonable means prior to 60 days after the cessation.

Moreover, your license from a particular copyright holder is reinstated
permanently if the copyright holder notifies you of the violation by some
reasonable means, this is the first time you have received notice of violation
of this License (for any work) from that copyright holder, and you cure the
violation prior to 30 days after your receipt of the notice.

Termination of your rights under this section does not terminate the licenses
of parties who have received copies or rights from you under this License.  If
your rights have been terminated and not permanently reinstated, receipt of a
copy of some or all of the same material does not give you any rights to use
it.


## 10. Future revisions of this license ##

The Free Software Foundation may publish new, revised versions of the GNU Free
Documentation License from time to time.  Such new versions will be similar in
spirit to the present version, but may differ in detail to address new problems
or concerns.  See http://www.gnu.org/copyleft/.

Each version of the License is given a distinguishing version number.  If the
Document specifies that a particular numbered version of this License “or any
later version” applies to it, you have the option of following the terms and
conditions either of that specified version or of any later version that has
been published (not as a draft) by the Free Software Foundation.  If the
Document does not specify a version number of this License, you may choose any
version ever published (not as a draft) by the Free Software Foundation.  If
the Document specifies that a proxy can decide which future versions of this
License can be used, that proxy’s public statement of acceptance of a version
permanently authorizes you to choose that version for the Document.


## 11. Relicensing ##

“Massive Multiauthor Collaboration Site” (or “MMC Site”) means any World Wide
Web server that publishes copyrightable works and also provides prominent
facilities for anybody to edit those works.  A public wiki that anybody can
edit is an example of such a server.  A “Massive Multiauthor Collaboration” (or
“MMC”) contained in the site means any set of copyrightable works thus
published on the MMC site.

“CC-BY-SA” means the Creative Commons Attribution-Share Alike 3.0 license
published by Creative Commons Corporation, a not-for-profit corporation with a
principal place of business in San Francisco, California, as well as future
copyleft versions of that license published by that same organization.

“Incorporate” means to publish or republish a Document, in whole or in part, as
part of another Document.

An MMC is “eligible for relicensing” if it is licensed under this License, and
if all works that were first published under this License somewhere other than
this MMC, and subsequently incorporated in whole or in part into the MMC, (1)
had no cover texts or invariant sections, and (2) were thus incorporated prior
to November 1, 2008.

The operator of an MMC Site may republish an MMC contained in the site under
CC-BY-SA on the same site at any time before August 1, 2009, provided the MMC
is eligible for relicensing.  ADDENDUM: How to use this License for your
documents


## Addendum: How to use this license for your documents ##

To use this License in a document you have written, include a copy of the
License in the document and put the following copyright and license notices
just after the title page:

    Copyright (C)  YEAR  YOUR NAME.
    Permission is granted to copy, distribute and/or modify this document
    under the terms of the GNU Free Documentation License, Version 1.3
    or any later version published by the Free Software Foundation;
    with no Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.
    A copy of the license is included in the section entitled "GNU
    Free Documentation License".

If you have Invariant Sections, Front-Cover Texts and Back-Cover Texts, replace
the “with … Texts.” line with this:

    with the Invariant Sections being LIST THEIR TITLES, with the
    Front-Cover Texts being LIST, and with the Back-Cover Texts being LIST.

If you have Invariant Sections without Cover Texts, or some other combination
of the three, merge those two alternatives to suit the situation.

If your document contains nontrivial examples of program code, we recommend
releasing these examples in parallel under your choice of free software
license, such as the GNU General Public License, to permit their use in free
software.
