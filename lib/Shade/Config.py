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

import os
import os.path
import shutil
import json
import tempfile

std_open = open

conf_dir = os.path.join(os.environ['HOME'], '.shade')
conf_path = None

# Create conf_dir if it doesn't exist.
try:
    os.mkdir(conf_dir)
except:
    pass

def init(name):
    global conf_path
    conf_path = os.path.join(conf_dir, name)
    # Create conf file if it doesn't exist.
    std_open(conf_path, 'a').close()

def open(mode = 'r'):
    if conf_path is None:
        raise 'You have to use `init` before opening the config file.'
    return std_open(conf_path, mode)

def replace_with_temp(t):
    if conf_path is None:
        raise 'You have to use `init` before saving the config file.'
    t.close()
    shutil.move(t.name, conf_path)

def open_temp():
    (t, tp, ) = tempfile.mkstemp()
    os.close(t)
    return std_open(tp, 'w')

def load_json():
    try:
        f = open()
        config = json.load(f)
        f.close()
    except:
        config = {}
    return config

def save_json(config):
    t = open_temp()
    json.dump(config, t, indent = 2)
    replace_with_temp(t)
