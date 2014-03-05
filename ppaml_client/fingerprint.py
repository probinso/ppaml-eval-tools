# fingerprint.py -- machine fingerprint         -*- coding: us-ascii -*-
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

"""Get a machine fingerprint.

"Fingerprint" is somewhat of a misnomer, as the data collected by the
code in this module does not uniquely identify a machine.  Instead, the
goal is simply to collect enough data that the machine's capabilities
are obvious.

"""


# __init__.py ensured Python 2.6 or 2.7 is running.

from __future__ import (absolute_import, division, print_function)

import json
import platform
import re
import socket

import procfs

from .namespace import Namespace



##################################### CPU #####################################


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


class CPU(Namespace):
    """A central processing unit.

    Standard fields:
        cache_kb -- L3 cache size in kilobytes
        family, model, stepping -- numeric model identifiers
        microcode -- version of microcode loaded
        model_name -- human-readable model name
        mhz -- maximum clock speed in megahertz
        n_cores -- the number of cores
        n_threads -- the number of threads

    """

    @classmethod
    def current(cls):
        """Create a new CPU with the properties of the current one."""
        result = cls()

        try:
            proc = procfs.Proc()
        except procfs.exceptions.DoesNotExist:
            # We're on a system that doesn't have a procfs, like OS X.
            # TODO: Handle this case.
            pass

        else:
            cpuinfo = proc.cpuinfo
            # This cpuinfo data structure behaves very strangely--it
            # presents an interface similar to a dictionary, but among
            # other weirdness, it does not iterate correctly, and
            # __len__ does not work.  The code in this function thus
            # looks a bit unpythonic, but doing this any other way
            # causes boatloads of unexpected exceptions.

            # n_threads
            result.n_threads = len(dict(cpuinfo))

            # Ensure all the remaining statistics are uniform across the
            # remaining CPUs.
            first_thread = cpuinfo[0]
            for thread in cpuinfo.values():
                for attribute in ['cpu_cores', 'cpu_family', 'model',
                                  'stepping', 'microcode', 'cache_size',
                                  'model_name']:
                    if thread[attribute] != first_thread[attribute]:
                        raise HeterogeneousSystemException
            result.n_cores = first_thread.cpu_cores
            result.family = first_thread.cpu_family
            result.model = first_thread.model
            result.stepping = first_thread.stepping
            result.microcode = int(first_thread.microcode, 0)
            result.cache_kb = int(first_thread.cache_size)
            result.model_name = first_thread.model_name

            # Get the CPU speed.  Don't use the cpu_mhz field from
            # cpuinfo, as this indicates the current CPU speed and will
            # likely be inaccurate if CPU frequency scaling is enabled.
            cpu_speed_spec = first_thread.model_name.split()[-1].lower()
            hz_re = re.compile('^([-+]?[\d.]+) *([kmgt]?)hz$', re.IGNORECASE)
            value_str, unit = hz_re.search(cpu_speed_spec).groups()
            result.mhz = int(float(value_str) * _METRIC_PREFIX[unit] / 1e6)

        return result



##################################### RAM #####################################


class RAM(Namespace):
    """A RAM unit.

    Standard fields:
        total_kib -- total RAM capacity in kilobytes

    """

    @classmethod
    def current(cls):
        """Create a new RAM with the properties of the current one."""
        result = cls()

        try:
            proc = procfs.Proc()
        except procfs.exceptions.DoesNotExist:
            # TODO: Handle this case.
            pass

        else:
            result.total_kib = proc.meminfo.MemTotal

        return result



##################################### OS ######################################


class Platform(Namespace):
    """A software platform (kernel + userland).

    Standard fields:
        kernel -- name of the kernel (e.g., 'Linux')
        kernel_version -- kernel version string
        userland -- name of the userland (e.g., 'GNU')
        userland_version -- userland version string
        hostname -- system host name (including domain if possible)

    """

    @classmethod
    def current(cls):
        """Create a new Platform with the properties of the current one."""
        result = cls()

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



#################################### Main #####################################


class Fingerprint(Namespace):
    """A machine fingerprint.

    This data do not uniquely identify the machine, but they give enough
    information that its overall specifications may be easily inferred.

    """

    @classmethod
    def current(cls):
        """Fingerprint the current machine."""
        result = cls()
        result.cpu = CPU.current()
        result.ram = RAM.current()
        result.os = Platform.current()
        return result


def main(arguments):
    """Print the current machine fingerprint in JSON format."""
    indent_level = arguments.indent if arguments.indent else None
    print(json.dumps(Fingerprint.current(), indent=indent_level))


def add_subparser(subparsers):
    """Register the 'fingerprint' subcommand."""
    parser = subparsers.add_parser('fingerprint',
                                   help="print machine fingerprint")
    parser.add_argument('-i', '--indent', default=4, type=int,
                        help="set output indentation level")
    parser.set_defaults(func=main)
