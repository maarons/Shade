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

import os
import os.path
import json
import tempfile
import shutil
from configparser import SafeConfigParser

import Shade.Subprocess as S

class UsesConfig():
    def __init__(self, conf_name):
        conf_dir = os.path.join(os.environ['HOME'], '.shade')
        # Create conf_dir if it doesn't exist.
        try:
            os.mkdir(conf_dir)
        except:
            pass
        self.__conf_path = os.path.join(conf_dir, conf_name)
        # Create conf file if it doesn't exist.
        open(self.__conf_path, 'a').close()

    def read_ini_conf(self):
        conf = SafeConfigParser()
        # Make options case sensitive.
        conf.optionxform = str
        conf.read(self.__conf_path)
        return conf

    def read_json_conf(self):
        with open(self.__conf_path) as f:
            try:
                conf = json.load(f)
            except:
                conf = {}
        return conf

    def save_json_conf(self, conf):
        (handle, path, ) = tempfile.mkstemp()
        os.close(handle)
        with open(path, 'w') as tmp:
            json.dump(conf, tmp, indent = 2)
        shutil.move(path, self.__conf_path)
