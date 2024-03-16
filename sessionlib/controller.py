import dbus

from .events import Event, Pub

from .core.alsaseq import AlsaseqMonitor
from .core.jack import JackMonitor
from .core.udev import UdevMonitor


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
    def __init__(self, bus=None):
        super().__init__()
        if bus is None:
            bus = dbus.SessionBus()
        self.jack = JackMonitor(bus)
        self.jack.attach(self)
        self.seq = AlsaseqMonitor()
        self.seq.attach(self)
        self.udev = UdevMonitor()
        self.udev.attach(self)

    def refresh(self):
        # refresh udev before seq, or it causes conflicts for jack
        self.udev.refresh()
        self.seq.refresh()

    def update(self, timeout=100):
        self.seq.update(timeout)
        return True

    def process_event(self, event):
        print(event)
