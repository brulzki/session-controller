import argparse

from gi.repository import GLib
import dbus.mainloop.glib

from .controller import SessionController

def main():
    parser = argparse.ArgumentParser(
        prog='session-controller',
        description='Manage a studio session')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    controller = SessionController(debug=args.debug)

    controller.refresh()
    GLib.idle_add(controller.update)

    loop = GLib.MainLoop()
    loop.run()
