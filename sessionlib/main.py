import argparse
import configparser

from gi.repository import GLib
import dbus.mainloop.glib

from xdg import BaseDirectory as xdgbase

from .controller import SessionController

def main():
    parser = argparse.ArgumentParser(
        prog='session-controller',
        description='Manage a studio session')
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config_file = xdgbase.load_first_config('session-controller', 'config')
    if config_file:
        config.read(config_file)

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    controller = SessionController(config=config, debug=args.debug)

    controller.refresh()
    GLib.idle_add(controller.update)

    loop = GLib.MainLoop()
    loop.run()
