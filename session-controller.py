#!/usr/bin/python

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from gi.repository import GLib
import dbus.mainloop.glib

try:
    from straight.plugin import load
except ModuleNotFoundError:
    import sys
    sys.path.append('straight.plugin')
    from straight.plugin import load

import sessionlib
from sessionlib.controller import SessionController

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    controller = SessionController()

    plugin_classes = load('plugins', subclasses=sessionlib.Plugin)
    plugins = plugin_classes.produce(controller)

    controller.refresh()
    GLib.idle_add(controller.update)

    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
