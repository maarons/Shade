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
from threading import Lock

from Shade.storage.Device import Device

class UDisks():
    def __init__(self):
        self.__lock = Lock()
        self.__bus = dbus.SystemBus()
        obj = self.__bus.get_object(
            'org.freedesktop.UDisks',
            '/org/freedesktop/UDisks'
        )
        self.__iface = dbus.Interface(obj, 'org.freedesktop.UDisks')

        self.__devices = []
        # Dynamically add and remove devices.
        self.__iface.connect_to_signal('DeviceAdded', self.__add_device)
        self.__iface.connect_to_signal('DeviceRemoved', self.__remove_device)
        # Init the device list.
        self.__load_devices()

    def devices(self):
        self.__lock.acquire()
        devices = self.__devices
        self.__lock.release()
        return devices

    def update(self):
        self.__load_devices()

    def __sort(self):
        # You should have the lock before calling this method.  This method
        # might throw exceptions if one of the devices disappears.
        self.__devices.sort(key = lambda d: d.path())

    def __add_device(self, path):
        self.__lock.acquire()
        try:
            device = Device(path)
            if device.is_useful():
                self.__devices.append(device)
                self.__sort()
        except:
            # Recover if the device disappeared.
            pass
        self.__lock.release()

    def __remove_device(self, path):
        self.__lock.acquire()
        # Device object corresponding to the removed device will be unusable.
        def working(device):
            try:
                # `uuid` is quite arbitrary, it is only meant to throw an
                # exception if a device is not working.
                device.uuid()
                return True
            except:
                return False
        # No need to sort, only removing entries
        self.__devices = list(filter(working, self.__devices))
        self.__lock.release()

    def __load_devices(self, under_lock = False):
        if not under_lock:
            self.__lock.acquire()
        try:
            devices = map(Device, self.__iface.EnumerateDevices())
            self.__devices = list(filter(lambda d: d.is_useful(), devices))
            self.__sort()
        except:
            # Recover from disappearing devices and try again.
            self.__load_devices(under_lock = True)
        self.__lock.release()
