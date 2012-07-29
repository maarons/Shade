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

from UDisks import UDisks

class Storage():
    def __init__(self):
        self.__udisks = UDisks()

    def devices(self):
        return self.__udisks.devices()

    def update(self):
        self.__udisks.update()

    def list(self, tries = 3):
        try:
            for device in self.devices():
                print(device)
        except:
            # One of the device objects is unusable, probaby the corresponding
            # device was unplugged.
            print(
                'There was an error, '
                'updating the device list and trying again.',
                file = sys.stderr
            )
            if tries > 0:
                self.update()
                self.list(tries - 1)
            else:
                print('Too many errors, giving up', file = sys.stderr)

    def __matching_devices(self, name, tries = 3):
        try:
            return filter(lambda device: device.match(name), self.devices())
        except:
            # One of the device objects is unusable, probaby the corresponding
            # device was unplugged.
            if tries > 0:
                self.update()
                return self.__matching_devices(name, tries - 1)
            else:
                # Silently ignore the exceptions.
                return []

    def mount(self, name):
        self.perform_action(name, 'mount')

    def unmount(self, name):
        self.perform_action(name, 'unmount')

    def lock(self, name):
        self.perform_action(name, 'lock')

    def unlock(self, name):
        self.perform_action(name, 'unlock')

    def detach(self, name):
        self.perform_action(name, 'detach')

    def perform_action(self, name, action):
        devices = self.__matching_devices(name)
        for device in devices:
            try:
                # Get the path before so it can't raise errors after mounting.
                path = device.path()
            except:
                # Silently ignore this device.
                continue
            try:
                if action == 'mount':
                    device.mount()
                elif action == 'unmount':
                    device.unmount()
                elif action == 'lock':
                    device.lock()
                elif action == 'unlock':
                    device.unlock()
                elif action == 'detach':
                    device.detach()
                else:
                    # This is weird, this shouldn't have happened, silently
                    # ignore.
                    return
                print('{0}ed: {1}'.format(action.title(), path))
            except Exception as e:
                print(
                    'Could not {0} {1}:\n{2}'.format(
                        action,
                        path,
                        e.message
                    ),
                    file = sys.stderr
                )
        if len(devices) == 0:
            print('Device could not be found')
