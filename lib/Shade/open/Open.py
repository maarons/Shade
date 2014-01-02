# Copyright (c) 2011, 2012, 2013, 2014 Marek Sapota
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
import os.path

from Shade.UsesConfig import UsesConfig
import Shade.Subprocess as S
from Shade.Log import stderr

class Open(UsesConfig):
    def __init__(self):
        UsesConfig.__init__(self, 'open.conf')
        self.__handlers = self.read_json_conf()

    def __get_mime(self, path):
        # os.path.realpath will resolve symbolic links
        try:
            mime = S.get_output("file -b --mime-type '{0}'".format(
                os.path.realpath(path)
            )).strip()
        except:
            stderr("Couldn't get mime type of '{}'", path)
            return None
        return mime

    def __get_first(self):
        files = S.get_output('ls -1').split('\n')
        if len(files) == 0:
            stderr('No file to open was found')
            return None
        else:
            return files[0]

    def save(self):
        self.save_json_conf(self.__handlers)

    def list(self):
        for mime, app in self.__handlers.items():
            print('{0}: {1}'.format(mime, app))

    def remove_handler(self, mime):
        if mime in self.__handlers:
            del self.__handlers[mime]

    def remove_handler_for_file(self, file):
        mime = self.__get_mime(file)
        if mime is None:
            return
        self.remove_handler(mime)

    def add_handler(self, mime, app):
        self.__handlers[mime] = app

    def open_first(self, background):
        file = self.__get_first()
        if file is not None:
            self.open_file(file, background)

    def add_handler_for_first(self, app):
        file = self.__get_first()
        if file is not None:
            self.add_handler_for_file(file, app)

    def add_handler_for_file(self, file, app):
        mime = self.__get_mime(file)
        if mime is None:
            return
        self.add_handler(mime, app)

    def open_file(self, file, background):
        mime = self.__get_mime(file)
        if mime is None:
            return
        if mime not in self.__handlers:
            stderr("Don't know how to handle '{}' mime type.", mime)
            return
        app = self.__handlers[mime]
        if background:
            S.run(
                "nohup {0} '{1}' &> /dev/null &".format(app, file),
                shell = True
            )
        else:
            S.run(
                "{0} '{1}'".format(app, file),
                shell = True
            )
