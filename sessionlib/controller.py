import dbus

from .events import Event, Pub

from .core.alsaseq import AlsaseqMonitor
from .core.jack import JackMonitor
from .core.udev import UdevMonitor
from . import plugin


class Error(Exception):
    def __init__(self, string):
        self.msg = string


# device config
#  - type = usb midi / alsa hw / jack client
#  - name (used to match against)
#  - vendor
#  - model
#  - usb port ? (how do I get that ?)
#  - connect action
#  - disconnect action
#  - input handler
#  - (or just a handler class for all 3 of the above ?)


class SessionController(Pub):
    def __init__(self, config=None, bus=None, debug=False):
        super().__init__()
        if bus is None:
            bus = dbus.SessionBus()
        self.debug = debug
        self.jack = JackMonitor(bus)
        self.jack.attach(self)
        self.seq = AlsaseqMonitor()
        self.seq.attach(self)
        self.udev = UdevMonitor()
        self.udev.attach(self)
        if config:
            plugin_path = config.get('defaults', 'plugin_path', fallback='plugins')
        if plugin_path:
            self.plugins = plugin.Manager(plugin_path, self)

    def refresh(self):
        # refresh udev before seq, or it causes conflicts for jack
        self.udev.refresh()
        self.seq.refresh()

    def update(self, timeout=100):
        self.seq.update(timeout)
        return True

    def process_event(self, event):
        if self.debug:
            print(event)
