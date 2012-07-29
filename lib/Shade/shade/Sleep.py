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
import dbus
import subprocess
import shlex
import time
import sys

class Sleep():
    def __init__(self):
        self.bus = dbus.SystemBus()
        self.obj = self.bus.get_object(
            'org.freedesktop.UPower',
            '/org/freedesktop/UPower'
        )
        self.iface = dbus.Interface(self.obj, 'org.freedesktop.UPower')
        self.piface = dbus.Interface(self.obj, dbus.PROPERTIES_IFACE)

    def get_prop(self, name):
        return self.piface.Get('org.freedesktop.UPower', name)

    def can_suspend(self):
        return self.get_prop('CanSuspend') == 1

    def can_hibernate(self):
        return self.get_prop('CanHibernate') == 1

    def lock(self):
        subprocess.call(shlex.split('xscreensaver-command -lock'))
        # Wait for screensaver to appear.
        time.sleep(5)

    def suspend(self):
        if self.can_suspend():
            self.iface.AboutToSleep('')
            self.lock()
            try:
                self.iface.Suspend()
            except: # ignore reply timeout errors and stuff.
                pass
        else:
            print(
                'Suspend is not supported on your hardware.',
                file = sys.stderr
            )

    def hibernate(self):
        if self.can_hibernate():
            self.iface.AboutToSleep('')
            self.lock()
            try:
                self.iface.Hibernate()
            except: # ignore reply timeout errors and stuff.
                pass
        else:
            print(
                'Hibernate is not supported on your hardware.',
                file = sys.stderr
            )
