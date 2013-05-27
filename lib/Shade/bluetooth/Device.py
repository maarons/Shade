# Copyright (c) 2013 Marek Sapota
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

import subprocess
import io
import traceback

class Device():
    def __init__(self, addr, name = None):
        self.__addr = addr
        self.__name = name

    def get_addr(self):
        return self.__addr

    def get_name(self):
        if self.__name is None:
            return ''
        return self.__name

    def is_connected(self):
        from Shade.bluetooth.DeviceList import DeviceList
        return DeviceList.connected().contains(self)

    def is_trusted(self):
        from Shade.bluetooth.DeviceList import DeviceList
        return DeviceList.trusted().contains(self)

    def is_configured(self):
        from Shade.bluetooth.DeviceList import DeviceList
        return DeviceList.configured().contains(self)

    def connect(self):
        p = subprocess.Popen(
            ['simple-agent', 'hci0', self.__addr],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
        )
        stdout = p.communicate(b'0000')[0]
        ret = p.wait()
        if b'Error' in stdout:
            raise Exception(stdout.decode('utf-8'))
        subprocess.check_call(
            ['bluez-test-device', 'trusted', self.__addr, 'yes']
        )
        subprocess.check_call(
            ['bluez-test-input', 'connect', self.__addr]
        )
        subprocess.check_call(
            ['sudo', 'hcitool', 'enc', self.__addr]
        )

    def disconnect(self):
        ret = subprocess.call(['bluez-test-device', 'remove', self.__addr])
        return ret == 0
