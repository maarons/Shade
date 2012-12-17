# Copyright (c) 2011, 2012 Marek Sapota
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

from __future__ import print_function
import sys

import Shade.Subprocess as S
from Shade.UsesConfig import UsesConfig

class Display(UsesConfig):
    def __init__(self):
        UsesConfig.__init__(self, 'display.conf')

        self.__conf = self.read_ini_conf()

        # Find all mentioned displays and configured display modes.
        self.__displays = set()
        self.__modes = set()
        for section in self.__conf.sections():
            # Sections with upper case letters are special.
            if not section.islower():
                continue
            self.__modes.add(section)
            self.__displays.update(self.__conf.options(section))
        # Which displays have additional properties configured?
        try:
            self.__properties = set(self.__conf.options('Properties'))
        except:
            # No `Properties` section.
            self.__properties = set()

    def list_modes(self):
        return list(self.__modes)

    def switch(self, mode):
        if mode not in self.__modes:
            print(
                'Requested display mode is not defined.',
                file = sys.stderr
            )
            return

        # Commands that will be run.
        cmds = []
        # Command to turn requested displays on.
        on = ['xrandr']
        # Command to turn all other displays off.
        off = ['xrandr']
        # On and off commands are separate because most laptop video cards are
        # limited to only two displays at a time.  Turning displays off and on
        # with one xrandr command will fail.

        d = self.__displays.copy()
        for display in self.__conf.options(mode):
            d.remove(display)
            pos = self.__conf.get(mode, display)
            on.append('--output')
            on.append(display)
            on.append('--auto')
            if pos == 'main':
                on.append('--primary')
            else:
                on.append('--' + pos)
            if display in self.__properties:
                prop = self.__conf.get('Properties', display)
                cmds.append(' '.join([
                    'xrandr --output',
                    display,
                    '--set',
                    '"' + prop.split(':')[0] + '"',
                    '"' + prop.split(':')[1] + '"'
                ]))
        for display in d:
            off.append('--output')
            off.append(display)
            off.append('--off')

        cmds.append(' '.join(off))
        cmds.append(' '.join(on))
        cmds.append('xrandr --dpi 96')

        for cmd in cmds:
            print('## ', cmd)
            S.run(cmd)

        self.__on_switch()

    def __on_switch(self):
        try:
            cmd = self.__conf.get('OnSwitch', 'command')
        except:
            # No `OnSwitch` section.
            cmd = None
        if cmd is not None:
            print('## ', cmd)
            S.run(cmd, shell = True)
