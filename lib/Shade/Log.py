# Copyright (c) 2014 Marek Sapota
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

import sys
from getpass import getuser
from datetime import datetime

from Shade.UsesLock import UsesLock

class ShadeLog(UsesLock):
    def __init__(self):
        self.__log_file = '/tmp/{}.shade.log'.format(getuser())
        UsesLock.__init__(self, 'shade')

    def log(self, msg, where, *args, **kwargs):
        stamp = datetime.now().strftime('%m/%d/%Y %H:%M:%S> ')
        msg = stamp + msg.format(*args, **kwargs)
        if where in ['both', 'stderr']:
            print(msg, file = sys.stderr)
        if where in ['both', 'file']:
            self.get_lock()
            with open(self.__log_file, 'a') as f:
                print(msg, file = f)
            self.release_lock()

__shade_log = ShadeLog()

def log(msg, *args, **kwargs):
    __shade_log.log(msg, 'both', *args, **kwargs)

def stderr(msg, *args, **kwargs):
    __shade_log.log(msg, 'stderr', *args, **kwargs)

def logfile(msg, *args, **kwargs):
    __shade_log.log(msg, 'file', *args, **kwargs)
