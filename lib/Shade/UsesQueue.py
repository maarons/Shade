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
import pickle

# Should probably be used with a lock.
class UsesQueue():
    def __init__(self, name):
        self.__queue_path = os.path.join('/tmp', '{0}.{1}.queue'.format(
          getpass.getuser(),
          name
        ))
        # Create queue file if it doesn't exist.
        if not os.path.exists(self.__queue_path):
            with open(self.__queue_path, 'wb') as q:
                pickle.dump([], q)

    def __load_queue(self):
        with open(self.__queue_path, 'rb') as q:
            try:
                queue = pickle.load(q)
            except:
                queue = []
        return queue

    def push_queue(self, value):
        queue = self.__load_queue()
        queue.append(value)
        with open(self.__queue_path, 'wb') as q:
            pickle.dump(queue, q)

    def pop_queue(self):
        queue = self.__load_queue()
        left = len(queue)
        if left == 0:
            return (None, 0)
        else:
            value = queue.pop(0)
        with open(self.__queue_path, 'wb') as q:
            pickle.dump(queue, q)
        return (value, left - 1)
