# License
Shade is free software under the X11 license, you are welcome to copy it and/or
modify it.  See `COPYING` file for the full license text.

# Installation
Shade uses Python’s distutils so you can install it as any other Python package.

## Gentoo
There is a Gentoo ebuild available, to create a Gentoo package:

    make clean
    make dist
    sudo cp dist/shade-*.tar.gz /usr/portage/distfiles
    make package-gentoo

Now you can copy the `dist/app-misc` tree to an overlay or install Shade
directly with:

    sudo ebuild dist/app-misc/shade/shade-*.ebuild merge

# Usage
Shade uses sudo for all commands that need elevated privileges so your user has
to be able to use it.

## Open
Display built-in help:

    open --help

Open a file:

    open my_file.txt

Open a file in background:

    open --backgound my_file.txt

Open first file in current directory, useful for directories with photos or
similar files:

    open --first

List remembered mime type, handling application pairs:

    open --list

Record a handler for a mime type:

    open --mime text/plain --app vim
    open my_file.txt --app vim
    open --first --app vim

Forget an application associated with a mime type:

    open --mime text/plain --forget
    open my_file.txt --forget
    open --first --forget

## PulseAudio control
Switch between muted/unmuted settings on all sinks:

    pa-control --mute
    pa-control --unmute
    pa-control --mute-switch

Set volume (value from 0 to 100):

    pa-control --volume 50

Increase/decrease volume by 5:

    pa-control --volume-up
    pa-control --volume-down

## Shade
Put computer to sleep:

    shade --sleep suspend
    shade --sleep hibernate

Lock the screen (using xscreensaver):

    shade --sleep lock

Switch between “power save” and “performance” power management modes:

    shade --power-management powersave
    shade --power-management performance

Switch between display modes:

    shade --display new_mode

Display modes are specified in `~/.shade/display.conf`.  Display names are the
ones you get from the xrandr utility.  Example configuration:

    [internal]
    LVDS1=main

    [external]
    VGA1=main

    [both]
    VGA1=main
    LVDS1=right-of VGA1

    [presentation]
    VGA1=main
    LVDS1=same-as VGA1

    [Properties]
    LVDS1=scaling mode:Full aspect

    [OnSwitch]
    command=~/scripts/restart_xscreensaver_and_other_stuff.sh

`Properties` section is optional.  Properties are set using `xrandr --output
OUTPUT --set PROPERTY VALUE`, you can get a list of valid properties with
`xrandr --prop`.  The `OnSwitch` section is also optional and specifies a
command that should be run after the display mode is switched, you can use it to
restart some applications like xscreensaver or Conky.

## Storage
Running `storage` will give you a prompt where you can use following commands:

- `list` — print all plugged USB drives and their partitions.  This is the
  default command, if you hit enter on an empty line this command will be
  called.

- `update` — refresh the list of available devices.  Normally this will not be
  necessary, as Storage dynamically updates the list of devices as they are
  plugged in/out.  In the event that something goes wrong and automatic updates
  don’t work it is here though.

- `exit` — exit the command prompt.

- `mount [partition]` — mount selected partition.

- `umount [partition]` — unmount selected partition.

- `unmount [partition]` — unmount selected partition.

- `lock [partition]` — lock a LUKS partition.

- `unlock [partition]` — unlock a LUKS partition.

- `detach [device]` — detach (power off) a device.

# Development
The executables in `bin` won’t be able to access the libraries in `lib` by
default.  You should add the `lib` directory to your `PYTHONPATH` for them to
work.  If you’re using shell for development, you can source the provided
`devenv.sh` script to do so.
