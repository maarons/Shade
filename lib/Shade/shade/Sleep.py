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

import dbus
import time
import sys

import Shade.Subprocess as S
from Shade.UsesConfig import UsesConfig

class Sleep(UsesConfig):
    def __init__(self):
        UsesConfig.__init__(self, 'on-resume.sh')
        self.__bus = dbus.SystemBus()
        self.__obj = self.__bus.get_object(
            'org.freedesktop.UPower',
            '/org/freedesktop/UPower'
        )
        self.__iface = dbus.Interface(self.__obj, 'org.freedesktop.UPower')
        self.__piface = dbus.Interface(self.__obj, dbus.PROPERTIES_IFACE)

    def __get_prop(self, name):
        return self.__piface.Get('org.freedesktop.UPower', name)

    def __can_suspend(self):
        return self.__get_prop('CanSuspend') == 1

    def __can_hibernate(self):
        return self.__get_prop('CanHibernate') == 1

    def __on_resume(self):
        self.execute_conf()

    def __sleep(self, can_sleep, go_sleep):
        if can_sleep():
            self.__iface.AboutToSleep('')
            self.lock()
            try:
                go_sleep()
            except: # ignore reply timeout errors and stuff.
                pass
            self.__on_resume()
        else:
            print(
                'Operation is not supported on your hardware.',
                file = sys.stderr
            )

    def lock(self):
        S.run('xscreensaver-command -lock')
        # Wait for screensaver to appear.
        time.sleep(5)

    def suspend(self):
        self.__sleep(self.__can_suspend, self.__iface.Suspend)

    def hibernate(self):
        self.__sleep(self.__can_hibernate, self.__iface.Hibernate)
