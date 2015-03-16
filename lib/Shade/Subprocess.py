# Copyright (c) 2012, 2013, 2014 Marek Sapota
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

from subprocess import Popen, PIPE, CalledProcessError
import shlex
from getpass import getuser
import psutil

from Shade.Log import logfile, stderr

def __execute(cmd, shell):
    real_cmd = cmd if shell else shlex.split(cmd)
    p = Popen(real_cmd, shell = shell, stdout = PIPE, stderr = PIPE)
    try:
        (out, err, ) = p.communicate()
        out = out.decode('utf-8')
        err = err.decode('utf-8')
        if p.returncode != 0:
            logfile('Subprocess "{}" exited with code {}', cmd, p.returncode)
            stderr(
                'Subprocess "{}" exited with code {}\nstdout:\n{}\nstderr:\n{}',
                cmd,
                p.returncode,
                out,
                err,
            )
            raise CalledProcessError(p.returncode, cmd)
    except FileNotFoundError as e:
        logfile('Subprocess failed: {}', str(e))
        raise e
    return out

def run(cmd, shell = False):
    __execute(cmd, shell)

def get_output(cmd, shell = False):
    return __execute(cmd, shell)

def get_xuser():
    user = getuser()
    if user == 'root':
        pids = get_output('pgrep -f Xsession').splitlines()
        pids = [int(pid.strip()) for pid in pids]
        for pid in pids:
            try:
                p = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue
            if 'pgrep' not in p.cmdline() and 'grep' not in p.cmdline():
                user = p.username()
    return user
