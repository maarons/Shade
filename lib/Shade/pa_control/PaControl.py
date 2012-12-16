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

import signal

from Shade.UsesLock import UsesLock
from Shade.UsesQueue import UsesQueue
from Shade.UsesPid import UsesPid
from Shade.pa_control.PulseAudio import PulseAudio
from Shade.pa_control import Ping
import Shade.pa_control.ShowVolumeGtk as GUI

class PaControl(UsesLock, UsesQueue, UsesPid):
    def __init__(self, args):
        self.__register_sighandler()
        UsesPid.__init__(self, 'pa-control')
        UsesLock.__init__(self, 'pa-control')
        self.get_lock()
        UsesQueue.__init__(self, 'pa-control')
        self.push_queue(args)
        # Check if we should be the worker.
        self.worker_pid()
        self.release_lock()
        self.__loop_ended = False

    def __register_sighandler(self):
        # Register a SIGUSR1 handler.
        def handler(signum, frame):
            Ping.set(True)
        signal.signal(signal.SIGUSR1, handler)
        # Don't interrupt system cals on SIGUSR1.
        signal.siginterrupt(signal.SIGUSR1, False)

    def loop(self):
        if self.__loop_ended:
            raise Exception('loop can only be called once')
        self.__loop_ended = True

        if self.is_worker():
            GUI.init()
            pa = PulseAudio()
            while True:
                self.get_lock()
                (args, left, ) = self.pop_queue()
                if args is None:
                    self.worker_done()
                elif left == 0:
                    Ping.set(False)
                self.release_lock()

                if args is None:
                    break
                elif args.mute:
                    pa.mute()
                elif args.unmute:
                    pa.unmute()
                elif args.mute_switch:
                    pa.mute_switch()
                elif args.volume is not None:
                    pa.set_volume(args.volume)
                elif args.volume_up:
                    pa.volume_up()
                elif args.volume_down:
                    pa.volume_down()

                GUI.update(pa.get_volume(), pa.is_muted())

        self.close_lock()
