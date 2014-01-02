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

import Shade.Subprocess as S
import re

class PulseAudio():
    def __init__(self, user = None):
        self.__user = user
        info_list = self.__get_output('pactl list').split('\n\n')
        self.__sinks = []
        self.__in_use = False
        self.__volume = 100
        self.__muted = True
        for info in info_list:
            n = re.findall('^Sink #([0-9]+)', info)
            if len(n) > 0:
                sink = { 'id': n[0] }
                vol = re.findall('\tVolume:(.*)\n', info)[0]
                sink['volume'] = min(map(int, re.findall('([0-9]+)%', vol)))
                self.__volume = min(self.__volume, sink['volume'])
                sink['mute'] = len(re.findall('\tMute: no\n', info)) == 0
                self.__muted &= sink['mute']
                sink['max-volume'] = 65536.0
                self.__sinks.append(sink)
            if re.match('^Sink Input #([0-9]+)', info):
                self.__in_use = True

    def __get_output(self, cmd):
        if self.__user is not None:
            cmd = 'sudo -u {} {}'.format(self.__user, cmd)
        return S.get_output(cmd)

    def __run(self, cmd):
        self.__get_output(cmd)

    def mute(self):
        for sink in self.__sinks:
            self.__run('pactl set-sink-mute {0} 1'.format(sink['id']))
        self.__muted = True

    def unmute(self):
        for sink in self.__sinks:
            self.__run('pactl set-sink-mute {0} 0'.format(sink['id']))
        self.__muted = False

    def mute_switch(self):
        if self.__muted:
            self.unmute()
        else:
            self.mute()

    def is_muted(self):
        return self.__muted

    def __set_sink_volume(self, vol, sink):
        v = int(float(vol) * sink['max-volume'] / 100.0)
        self.__run('pactl set-sink-mute {0} 0'.format(sink['id']))
        self.__run('pactl set-sink-volume {0} {1}'.format(sink['id'], v))

    def set_volume(self, vol):
        for sink in self.__sinks:
            self.__set_sink_volume(vol, sink)
        self.__muted = False
        self.__volume = vol

    def get_volume(self):
        return self.__volume

    # `volume_up` and `volume_down` snaps volume to numbers divisible by 5.
    def volume_up(self):
        self.set_volume(max(0, min(100, 5 + (self.__volume // 5) * 5)))

    def volume_down(self):
        self.set_volume(max(0, min(100, -5 + (self.__volume // 5) * 5)))

    def is_in_use(self):
        return self.__in_use
