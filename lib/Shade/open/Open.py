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

import subprocess
import shlex
import os

from Shade import Config

# Returns `None` if no handler was found.
def find_handler(mime):
    c = Config.open()
    eof = False
    while not eof:
        l = c.readline()
        if not l.endswith('\n'):
            eof = True
        else:
            [m, _, h] = l.partition(' ')
            if m == mime:
                c.close()
                # Remove trailing '\n'.
                return h[:-1]
    c.close()

# If `handler` is `None`, it will be removed from configuration.
def save_handler(mime, handler = None):
    c = Config.open()
    t = Config.open_temp()

    eof = False
    while not eof:
        l = c.readline()
        if not l.endswith('\n'):
            eof = True
        else:
            [m, _, h] = l.partition(' ')
            if m != mime:
                t.write(l)
    if handler is not None:
        t.write('{0} {1}\n'.format(mime, handler))
    c.close()
    Config.replace_with_temp(t)

def list_handlers():
    c = Config.open()
    handlers = []
    eof = False
    while not eof:
        l = c.readline()
        if not l.endswith('\n'):
            eof = True
        else:
            [m, _, h] = l.partition(' ')
            # Remove the trailing '\n'.
            handlers.append((m, h[:-1], ))
    c.close()
    return handlers

def get_mime(path):
    cmd = shlex.split("file -b --mime-type '{0}'".format(path))
    mime = subprocess.check_output(cmd).strip()
    return mime
