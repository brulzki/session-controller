#!/usr/bin/python

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from gi.repository import GLib
import dbus.mainloop.glib
from sessionlib.controller import SessionController

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    controller = SessionController()

    from plugins.autojack import AutoJackPlugin
    autojack = AutoJackPlugin(controller)
    from plugins.launchpad import LaunchpadPlugin
    lp = LaunchpadPlugin(controller)

    controller.refresh()
    GLib.idle_add(controller.update)

    loop = GLib.MainLoop()
    loop.run()

if __name__ == '__main__':
    main()
