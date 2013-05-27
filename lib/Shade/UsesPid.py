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

import getpass
import os
import os.path
import signal

# Should probably be used with a lock.
class UsesPid():
    def __init__(self, name):
        self.__pid_path = os.path.join('/tmp', '{0}.{1}.pid'.format(
          getpass.getuser(),
          name
        ))
        # Create pid file if it doesn't exist.
        open(self.__pid_path, 'a').close()

    def worker_pid(self):
        with open(self.__pid_path) as f:
            # Recover if pid file doesn't contain a pid of another process.
            try:
                pid = int(f.read())
                os.kill(pid, signal.SIGUSR1)
                self.__worker = False
            except:
                self.__worker = True
        if self.__worker:
            with open(self.__pid_path, 'w') as f:
                f.write(str(os.getpid()))

    def is_worker(self):
        return self.__worker

    def worker_done(self):
        if not self.__worker:
            raise Exception('Only workers are allowed to do that.')
        # Clear the pid file.
        open(self.__pid_path, 'w').close()
