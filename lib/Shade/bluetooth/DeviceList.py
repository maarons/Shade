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

import os.path
import subprocess

from Shade.bluetooth.Device import Device

class DeviceList():
    __connected = None
    __configured = None
    __trusted = None
    __name_to_addr = {}
    __addr_to_name = {}

    def __init__(self, devices):
        self.__devices = devices

    def __iter__(self):
        return iter(self.__devices.values())

    def names(self):
        return list(filter(
            lambda n: len(n) > 0,
            map(Device.get_name, self.__devices.values()),
        ))

    def contains(self, device):
        return device.get_addr() in self.__devices

    def get_by_name(self, name):
        addr = DeviceList.__name_to_addr.get(name)
        return self.__devices.get(addr)

    @staticmethod
    def connected():
        if DeviceList.__connected is None:
            out = subprocess.check_output(['hcitool', 'con']).strip()
            lines = out.split(b'\n')[1:]
            devices = {}
            for line in lines:
                addr = line.split(b' ')[2].decode('utf-8')
                DeviceList.__add_device(devices, addr)
            DeviceList.__connected = DeviceList(devices)
        return DeviceList.__connected

    @staticmethod
    def configured():
        if DeviceList.__configured is None:
            path = os.path.expanduser('~/.bluetooth_devices')
            lines = []
            try:
                with open(path, 'r') as f:
                    lines = f.readlines()
            except:
                # No config file.
                pass
            devices = {}
            for line in lines:
                (addr, name, ) = line.strip().split(' ', 1)
                DeviceList.__name_to_addr[name] = addr
                DeviceList.__addr_to_name[addr] = name
                devices[addr] = Device(addr, name)
            DeviceList.__configured = DeviceList(devices)
        return DeviceList.__configured

    @staticmethod
    def trusted():
        if DeviceList.__trusted is None:
            out = subprocess.check_output(['bluez-test-device', 'list']).strip()
            lines = out.split(b'\n')
            devices = {}
            for line in lines:
                if line:
                    addr = line.split(b' ', 1)[0].decode('utf-8')
                    DeviceList.__add_device(devices, addr)
            DeviceList.__trusted = DeviceList(devices)
        return DeviceList.__trusted

    @staticmethod
    def __add_device(devices, addr):
        devices[addr] = Device(
            addr,
            DeviceList.__addr_to_name.get(addr),
        )

# Initialize configured names fields.
DeviceList.configured()
