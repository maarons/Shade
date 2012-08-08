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

import readline

# Readline interface is an undocumented mess - if this class does something
# really strange and apparently useless it is actually probably required.  Edit
# with care.
class Completer():
    def __init__(self, storage):
        self.__storage = storage
        self.__possible = []

    def complete(self, text, state):
        # Text passed to this function is useless, it only contains the last
        # word in the line.  For "abc def" it will only contain "def".
        buf = readline.get_line_buffer()
        # Generate the completion list on first request.
        if state == 0:
            self.__regenerate(text, buf)
        if state >= len(self.__possible):
            return None
        return self.__possible[state]

    def __regenerate(self, text, buf):
        def add(cmd):
            possible = map(
                lambda n: '{0} {1}'.format(cmd, n),
                device.names()
            )
            self.__possible.extend(possible)

        self.__possible = ['list', 'update', 'exit']
        for device in self.__storage.devices():
            try:
                if device.is_drive():
                    add('detach')
                if device.is_partition():
                    if device.is_mounted():
                        add('umount')
                        add('unmount')
                    else:
                        add('mount')
                        if device.is_luks():
                            if device.is_open():
                                add('lock')
                            else:
                                add('unlock')
            except:
                # Device disappeared, ignore it.
                pass
        self.__possible = filter(lambda x: x.startswith(buf), self.__possible)
        # Compensate for ignoring the text given to us by readline.
        to_discard = len(buf) - len(text)
        self.__possible = map(lambda x: x[to_discard:].strip(), self.__possible)
