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
import re

class PulseAudio():
    def __init__(self):
        l = subprocess.check_output(shlex.split('pactl list')).split('\n\n')
        self.sinks = []
        self.volume = 100
        self.muted = True
        for info in l:
            n = re.findall('^Sink #([0-9]+)', info)
            if len(n) > 0:
                sink = { 'id': n[0] }
                vol = re.findall('\tVolume:(.*)\n', info)[0]
                sink['volume'] = min(map(int, re.findall('([0-9]+)%', vol)))
                self.volume = min(self.volume, sink['volume'])
                sink['mute'] = len(re.findall('\tMute: no\n', info)) == 0
                self.muted &= sink['mute']
                sink['max-volume'] = 65536.0
                self.sinks.append(sink)

    def mute(self):
        for s in self.sinks:
            cmd = shlex.split('pactl set-sink-mute {0} 1'.format(s['id']))
            subprocess.call(cmd)
        self.muted = True

    def unmute(self):
        for s in self.sinks:
            cmd = shlex.split('pactl set-sink-mute {0} 0'.format(s['id']))
            subprocess.call(cmd)
        self.muted = False

    def mute_switch(self):
        if self.muted:
            self.unmute()
        else:
            self.mute()

    def __set_sink_volume(self, vol, sink):
        v = int(float(vol) * sink['max-volume'] / 100.0)
        cmd = shlex.split('pactl set-sink-mute {0} 0'.format(sink['id']))
        subprocess.call(cmd)
        cmd = shlex.split('pactl set-sink-volume {0} {1}'.format(sink['id'], v))
        subprocess.call(cmd)

    def volume_up(self):
        self.set_volume(max(0, min(100, 5 + self.volume)))

    def volume_down(self):
        self.set_volume(max(0, min(100, -5 + self.volume)))

    def set_volume(self, vol):
        for s in self.sinks:
            self.__set_sink_volume(vol, s)
        self.muted = False
        self.volume = vol
