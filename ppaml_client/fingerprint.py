# fingerprint.py -- machine fingerprint         -*- coding: us-ascii -*-
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

"""Get a machine fingerprint.

"Fingerprint" is somewhat of a misnomer, as the data collected by the
code in this module does not uniquely identify a machine.  Instead, the
goal is simply to collect enough data that the machine's capabilities
are obvious.

"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import platform
import re
import socket

import procfs

from . import db



################################## Hardware ###################################


_METRIC_PREFIX = {
    'y': 1e24,
    'z': 1e21,
    'e': 1e18,
    'p': 1e15,
    't': 1e12,
    'g': 1e9,
    'm': 1e6,
    'k': 1e3,
    '': 1e0,
    }


class HeterogeneousSystemException(Exception):
    """Tried to fingerprint a heterogeneous SMP system.

    Currently, fingerprinting systems with more than one model of CPU is
    unsupported; this exception indicates that this script ran on such a
    CPU.

    """

    def __init__(self):
        super(HeterogeneousSystemException, self).__init__(
            "heterogeneous SMP systems are unsupported")


def current_hardware():
    """Create a new db.Hardware capturing the current platform."""
    result = db.Hardware()

    # CPU
    try:
        proc = procfs.Proc()
    except procfs.exceptions.DoesNotExist:
        # We're on a system that doesn't have a procfs, like OS X.
        # TODO: Handle this case.
        pass

    else:
        cpuinfo = proc.cpuinfo
        # This cpuinfo data structure behaves very strangely--it
        # presents an interface similar to a dictionary, but among other
        # weirdness, it does not iterate correctly, and __len__ does not
        # work.  The code in this section thus looks a bit unpythonic,
        # but doing this any other way causes boatloads of unexpected
        # exceptions.

        # n_threads
        result.cpu_n_threads = len(dict(cpuinfo))

        # Ensure all the remaining statistics are uniform across the
        # remaining CPUs.
        first_thread = cpuinfo[0]
        for thread in cpuinfo.values():
            for attribute in ['cpu_cores', 'cpu_family', 'model',
                              'stepping', 'microcode', 'cache_size',
                              'model_name']:
                if thread[attribute] != first_thread[attribute]:
                    raise HeterogeneousSystemException
        result.cpu_n_cores = first_thread.cpu_cores
        result.cpu_family = first_thread.cpu_family
        result.cpu_model = first_thread.model
        result.cpu_stepping = first_thread.stepping
        result.cpu_microcode = int(first_thread.microcode, 0)
        result.cpu_cache = int(first_thread.cache_size) * 1024
        result.cpu_model_name = first_thread.model_name

        # Get the CPU speed.  Don't use the cpu_mhz field from
        # cpuinfo, as this indicates the current CPU speed and will
        # likely be inaccurate if CPU frequency scaling is enabled.
        cpu_speed_spec = first_thread.model_name.split()[-1].lower()
        hz_re = re.compile('^([-+]?[\d.]+) *([kmgt]?)hz$', re.IGNORECASE)
        value_str, unit = hz_re.search(cpu_speed_spec).groups()
        result.cpu_clock = int(float(value_str) * _METRIC_PREFIX[unit])

    # RAM
    try:
        proc = procfs.Proc()
    except procfs.exceptions.DoesNotExist:
        # TODO: Handle this case.
        pass

    else:
        result.ram = proc.meminfo.MemTotal * 1024 # kiB -> B

    return result


def current_software():
    """Create a new db.Software capturing the current platform."""
    result = db.Software()

    # Kernel
    result.kernel = platform.system()
    result.kernel_version = platform.release()

    # Userland
    if platform.libc_ver()[0] == 'glibc':
        # We're almost certainly a GNU/Linux system.
        result.userland = 'GNU'

    # Hostname, for good measure
    result.hostname = socket.getfqdn()
    if result.hostname == "localhost":
        result.hostname = socket.gethostname()

    return result


def insert_current():
    """Insert the current machine fingerprint into the database."""
    with db.session() as session:
        # Hardware
        hw = current_hardware()
        session.add(hw)

        # Software
        sw = current_software()
        session.add(sw)

        # Environment
        env = db.Environment()
        session.flush()
        env.hardware_id = hw.hardware_id
        env.software_id = sw.software_id
        session.add(env)

        session.flush()
        return env.environment_id



#################################### Main #####################################


def main(_arguments):
    insert_current()


def add_subparser(subparsers):
    """Register the 'fingerprint' subcommand."""
    parser = subparsers.add_parser('fingerprint',
                                   help="record machine fingerprint")
    parser.set_defaults(func=main)
