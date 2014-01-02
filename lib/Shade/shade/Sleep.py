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

import dbus
import time
import sys
import os
import os.path
import re
import psutil

import Shade.Subprocess as S
from Shade.UsesConfig import UsesConfig
from Shade.Log import log, stderr
from Shade.pa_control.PulseAudio import PulseAudio
from Shade.shade.Power import Power
from Shade.shade.Display import Display

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

    def __sleep(self, sleep_type, can_sleep, go_sleep):
        if can_sleep():
            log('Going to {}', sleep_type)
            self.__iface.AboutToSleep('')
            self.lock()
            try:
                go_sleep()
                pass
            except: # ignore reply timeout errors and stuff.
                pass
            self.__on_resume()
            log('Got out of {}, normal operation resumed', sleep_type)
        else:
            stderr('{} is not supported on your hardware.', sleep_type)

    def lock(self):
        log('Locking screen')
        cmd = 'sudo -u {} xscreensaver-command -lock'
        S.run(cmd.format(S.get_xuser()))
        # Wait for screensaver to appear.
        time.sleep(5)

    def suspend(self):
        self.__sleep('suspend', self.__can_suspend, self.__iface.Suspend)

    def hibernate(self):
        self.__sleep('hibernate', self.__can_hibernate, self.__iface.Hibernate)

    def sleep_on_lid_close(self):
        log('Checking if should go to sleep')
        if not self.__get_prop('LidIsClosed'):
            log('Not going to sleep, lid open')
            return
        p = Power()
        if p.is_on_ac():
            log('Not going to sleep, on AC')
            return
        d = Display()
        if d.is_using_external_display():
            log('Not going to sleep, external monitor on')
            return
        dirs = os.listdir('/tmp')
        for d in dirs:
            if not re.match('^pulse-\w+$', d):
                continue
            pidfile = '/tmp/{}/pid'.format(d)
            if not os.path.isfile(pidfile):
                continue
            with open(pidfile, 'r') as f:
                pid = int(f.read().strip())
                try:
                    p = psutil.Process(pid)
                except psutil.NoSuchProcess:
                    continue
                if p.name == 'pulseaudio':
                    pa = PulseAudio(user = p.username)
                    if pa.is_in_use():
                        log('Not going to sleep, audio playing')
                        return
        self.suspend()
