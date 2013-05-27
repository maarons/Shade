# Copyright (c) 2011, 2012, 2013 Marek Sapota
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

import Shade.Subprocess as S

class Power():
    def __init__(self):
        info = S.get_output('cpufreq-info')
        # Get the CPU numbers.
        self.__cpus = re.findall('CPU ([0-9]+):', info)

    def __cpufreq(self, governor):
        for cpu in self.__cpus:
            S.run('sudo cpufreq-set -g {0} -c {1}'.format(governor, cpu))

    def powersave(self):
        self.__cpufreq('powersave')
        S.run('sudo pm-powersave true')

    def performance(self):
        self.__cpufreq('ondemand')
        S.run('sudo pm-powersave false')
