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

import dbus
from getpass import getpass

from Size import Size
from Shade.storage import Config

# Don't bother with handling DBus errors, things using this module should take
# care of that.

class Device():
    def __init__(self, name):
        self.__bus = dbus.SystemBus()
        obj = self.__bus.get_object('org.freedesktop.UDisks', name)
        self.__iface = dbus.Interface(
            obj,
            'org.freedesktop.UDisks.Device'
        )
        self.__piface = dbus.Interface(obj, dbus.PROPERTIES_IFACE)

        # Connect Luks devices with their children.
        if self.is_open():
            self.child = Device(self.__get_prop('LuksHolder'))
        else:
            self.child = None

        self.load_label()

    def load_label(self):
        config = Config.load_json()
        if self.uuid() in config:
            self.cached_label = config[self.uuid()]
        else:
            self.cached_label = ''

    def save_label(self):
        config = Config.load_json()
        config[self.uuid()] = self.label()
        Config.save_json(config)
        self.load_label()

    def names(self):
        names = [self.label(), self.path()]
        return filter(lambda x: len(x) > 0, names)

    def match(self, name):
        return name in self.names()

    def unlock(self):
        if self.is_partition() and self.is_luks() and not self.is_open():
            password = getpass('password for {0}: '.format(self.path()))
            self.child = Device(self.__iface.LuksUnlock(password, []))
            self.save_label()
        else:
            raise Exception('Not a locked LUKS partition.')

    def lock(self):
        if self.is_partition() and self.is_luks() and self.is_open():
            if self.is_mounted():
                raise Exception('Could not lock a mounted device.')
            self.__iface.LuksLock([])
            self.child = None
        else:
            raise Exception('Not an unlocked LUKS partition.')

    # Set slave to true for cleartext LUKS devices.
    def mount(self, slave = False):
        if (self.is_partition() or slave) and not self.is_mounted():
            if self.is_luks():
                if not self.is_open():
                    self.unlock()
                self.child.mount(slave = True)
            else:
                try:
                    clean = self.__iface.FilesystemCheck([]) == 1
                except Exception as e:
                    raise Exception(
                        'Could not check if file system is clean: '
                        + e.message
                    )
                if not clean:
                    raise Exception('File system is not clean.')
                self.__iface.FilesystemMount('auto', [])
        else:
            raise Exception('Not an unmounted partition.')

    # Set slave to true for cleartext LUKS devices.
    def unmount(self, slave = False):
        if (self.is_partition() or slave) and self.is_mounted():
            if self.is_luks():
                self.child.unmount(True)
                self.lock()
            else:
                self.__iface.FilesystemUnmount([])
        else:
            raise Exception('Not a mounted partition.')

    def detach(self):
        if self.is_drive():
            self.__iface.DriveDetach([])
        else:
            raise Exception('Not a detachable drive.')

    def __get_prop(self, name):
        return self.__piface.Get('org.freedesktop.UDisks.Device', name)

    def __is_usb(self):
        return self.__get_prop('DriveConnectionInterface') == 'usb'

    def __usage(self):
        return str(self.__get_prop('IdUsage'))

    def uuid(self):
        return str(self.__get_prop('IdUuid'))

    def path(self):
        return str(self.__get_prop('DeviceFile'))

    def label(self):
        if self.child:
            return self.child.label()
        else:
            label = str(self.__get_prop('IdLabel'))
            if len(label) == 0:
                label = self.cached_label
            return label

    def __vendor(self):
        return str(self.__get_prop('DriveVendor'))

    def is_luks(self):
        return self.__usage() == 'crypto'

    def is_open(self):
        return self.__get_prop('DeviceIsLuks') == 1

    def is_mounted(self):
        if self.child:
            return self.child.is_mounted()
        else:
            return self.__get_prop('DeviceIsMounted') == 1

    def is_partition(self):
        check = self.__is_usb()
        check &= self.__usage() in ['filesystem', 'crypto']
        return check

    def is_drive(self):
        check = self.__get_prop('DeviceIsDrive')
        check &= self.__get_prop('DriveCanDetach')
        # Drives with no media are not interesting.
        check &= self.__get_prop('DeviceIsMediaAvailable')
        return check

    def is_useful(self):
        return self.is_partition() or self.is_drive()

    def __state(self):
        if self.is_mounted():
            return 'mounted'
        elif self.is_open():
            return 'open LUKS'
        else:
            return 'unmounted'

    def __size(self):
        return str(Size(self.__get_prop('DeviceSize')))

    def __str__(self):
        s = self.path() + ' - '
        if self.is_partition():
            s += '{0} ({1} {2})'.format(
                self.__state(),
                self.__vendor(),
                self.__size()
            )
            if self.label():
                s += ': {0}'.format(self.label())
        else:
            # Not a partition, so it must be a drive.
            s += '{0} {1}'.format(
                self.__vendor(),
                self.__size()
            )
        return s
