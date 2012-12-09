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
import os
import subprocess
import shlex
import sys
try: # Python 3.x
    from configparser import SafeConfigParser
except: # Python 2.x
    from ConfigParser import SafeConfigParser

from Shade import Config

class Display():
    def __init__(self):
        conf_path = os.path.join(Config.conf_dir, 'display.conf')

        self.conf = SafeConfigParser()
        # Make options case sensitive.
        self.conf.optionxform = str
        self.conf.read(conf_path)

        # Find all mentioned displays and configured display modes.
        self.displays = set()
        self.modes = set()
        for section in self.conf.sections():
            if not section.islower():
                continue
            self.modes.add(section)
            self.displays.update(self.conf.options(section))
        # Which displays have additional properties configured?
        try:
            self.properties = set(self.conf.options('Properties'))
        except:
            # No `Properties` section.
            self.properties = set()

    def switch(self, mode):
        if mode not in self.modes:
            print(
                'Requested display mode is not defined.',
                file = sys.stderr
            )
            return

        d = self.displays.copy()
        cmds = []
        on = ['xrandr']
        off = ['xrandr']
        for display in self.conf.options(mode):
            d.remove(display)
            pos = self.conf.get(mode, display)
            on.append('--output')
            on.append(display)
            on.append('--auto')
            on.append('--dpi')
            on.append('96')
            if pos == 'main':
                on.append('--primary')
            else:
                on.append('--' + pos)
            if display in self.properties:
                prop = self.conf.get('Properties', display)
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

        for cmd in cmds:
            print('## ', cmd)
            subprocess.call(shlex.split(cmd))

        self.on_switch()

    def on_switch(self):
        try:
            cmd = self.conf.get('OnSwitch', 'command')
        except:
            # No `OnSwitch` section.
            cmd = None
        if cmd is not None:
            print('## ', cmd)
            subprocess.call(cmd, shell = True)
