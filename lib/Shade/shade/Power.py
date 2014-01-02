# Copyright (c) 2011, 2012, 2013, 2014 Marek Sapota
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE

import re
import os.path

import Shade.Subprocess as S
from Shade.Log import log

class Power():
    PSTATE_DIR = '/sys/devices/system/cpu/intel_pstate/'
    AC_FILE = '/sys/class/power_supply/AC/online'

    def __init__(self):
        info = S.get_output('cpufreq-info')
        # Get the CPU numbers.
        self.__cpus = re.findall('CPU ([0-9]+):', info)

    def __cpufreq(self, governor):
        for cpu in self.__cpus:
            S.run('sudo cpufreq-set -g {0} -c {1}'.format(governor, cpu))

    def __pstate(self, min_perf, max_perf):
        cmd = 'echo {min} > {dir}min_perf_pct && ' \
              'echo {max} > {dir}max_perf_pct'
        cmd = cmd.format(
            min = min_perf,
            max = max_perf,
            dir = Power.PSTATE_DIR,
        )
        S.run('sudo sh -c "{}"'.format(cmd))

    def __uses_pstate(self):
        return os.path.isfile(Power.PSTATE_DIR + 'min_perf_pct') and \
               os.path.isfile(Power.PSTATE_DIR + 'max_perf_pct')

    def powersave(self):
        log('Setting power state to powersave')
        if self.__uses_pstate():
            self.__cpufreq('performance')
            self.__pstate(0, 0)
        else:
            self.__cpufreq('powersave')
        S.run('sudo pm-powersave true')

    def performance(self):
        log('Setting power state to performance')
        self.__cpufreq('performance')
        if self.__uses_pstate():
            self.__pstate(0, 100)
        S.run('sudo pm-powersave false')

    def is_on_ac(self):
        on_ac = True
        if os.path.isfile(Power.AC_FILE):
            with open(Power.AC_FILE, 'r') as f:
                on_ac = f.read().strip() == '1'
        return on_ac

    def auto(self):
        if self.is_on_ac():
            self.performance()
        else:
            self.powersave()
