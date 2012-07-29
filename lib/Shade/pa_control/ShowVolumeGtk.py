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

import gtk, gobject
from time import sleep

import Ping

def get_stock_icon(name):
    icon = gtk.Image()
    icon.set_from_icon_name(name, gtk.ICON_SIZE_DIALOG)
    return icon

def init():
    global STOCK_VOLUME_MAX
    global STOCK_VOLUME_MED
    global STOCK_VOLUME_MIN
    global STOCK_VOLUME_MUTE
    global volume_icon, progress, box

    STOCK_VOLUME_MAX = get_stock_icon('stock_volume-max')
    STOCK_VOLUME_MED = get_stock_icon('stock_volume-med')
    STOCK_VOLUME_MIN = get_stock_icon('stock_volume-min')
    STOCK_VOLUME_MUTE = get_stock_icon('stock_volume-mute')

    window = gtk.Window()
    window.set_type_hint(gtk.gdk.WINDOW_TYPE_HINT_SPLASHSCREEN)
    window.set_position(gtk.WIN_POS_CENTER_ALWAYS)
    window.set_keep_above(True)

    box = gtk.VBox()
    frame = gtk.Frame()
    frame.set_border_width(1)
    frame.add(box)
    window.add(frame)

    volume_icon = STOCK_VOLUME_MUTE
    box.pack_start(volume_icon)
    progress = gtk.ProgressBar()
    box.pack_end(progress)

    window.show_all()

def update(volume, mute):
    global volume_icon, progress, box

    box.remove(volume_icon)
    if mute:
        volume_icon = STOCK_VOLUME_MUTE
        volume = 0
    elif volume == 0:
        volume_icon = STOCK_VOLUME_MIN
    elif volume == 100:
        volume_icon = STOCK_VOLUME_MAX
    else:
        volume_icon = STOCK_VOLUME_MED
    box.pack_start(volume_icon)
    volume_icon.show()

    progress.set_text(str(volume))
    progress.set_fraction(max(0.0, min(1.0, float(volume) / 100.0)))

    for i in range(100):
        # Stop when another action is pending.
        if Ping.get():
            break
        # Do some GTK+ rendering.
        while gtk.events_pending():
            gtk.main_iteration(block = False)
        sleep(0.01)
