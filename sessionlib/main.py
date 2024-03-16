from gi.repository import GLib
import dbus.mainloop.glib

from .controller import SessionController

def main():
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    controller = SessionController()

    controller.refresh()
    GLib.idle_add(controller.update)

    loop = GLib.MainLoop()
    loop.run()
