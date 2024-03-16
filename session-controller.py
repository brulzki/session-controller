#!/usr/bin/python

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from gi.repository import GLib
import dbus.mainloop.glib

import sessionlib
from sessionlib.controller import SessionController

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    controller = SessionController()

    controller.refresh()
    GLib.idle_add(controller.update)

    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
