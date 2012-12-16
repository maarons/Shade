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

import getpass
import os.path
import fcntl

class UsesLock():
    def __init__(self, name):
        lock_path = os.path.join('/tmp', '{0}.{1}.lock'.format(
          getpass.getuser(),
          name
        ))
        # Create lock file if it doesn't exist.
        open(lock_path, 'a').close()
        self.__locked = False
        self.__lock_file = open(lock_path)
        # Not usable once lock file is closed.
        self.__usable = True

    def __require_usable(self):
        if not self.__usable:
            raise Exception('Lock is not usable')

    def get_lock(self):
        self.__require_usable()
        if not self.__locked:
            fcntl.flock(self.__lock_file, fcntl.LOCK_EX)
            self.__locked = True

    def release_lock(self):
        self.__require_usable()
        if self.__locked:
            fcntl.flock(self.__lock_file, fcntl.LOCK_UN)
            self.__locked = False

    def close_lock(self):
        self.__require_usable()
        self.__lock_file.close()
