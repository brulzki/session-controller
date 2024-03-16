import pyudev
from pyudev.glib import MonitorObserver

from ..events import Event, Pub


class UdevMonitor(Pub):
    def __init__(self, debug=False):
        super().__init__()
        self._debug = debug
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='sound')
        self.observer = MonitorObserver(self.monitor)
        self.observer.connect('device-event', self.device_event)
        self.monitor.start()

    def refresh(self):
        for device in self.context.list_devices(subsystem='sound'):
            self.post(Event('snd_device', name=device.sys_name,
                            path=device.device_path,
                            vendor=device.get('ID_VENDOR_FROM_DATABASE'),
                            model=device.get('ID_MODEL'),
                            ))

            if self._debug:
                print(list(device.properties))
                try:
                    print(device.properties['ID_VENDOR'])
                    print(device.properties['ID_VENDOR_FROM_DATABASE'])
                    print(device.properties['ID_MODEL'])
                    print(device.properties['ID_MODEL_FROM_DATABASE'])
                except:
                    pass

    def device_event(self, observer, device):
        if device.action in ['add', 'change']:
            self.post(Event('snd_%s' % device.action, name=device.sys_name,
                            path=device.device_path,
                            vendor=device.get('ID_VENDOR_FROM_DATABASE'),
                            model=device.get('ID_MODEL'),
                            ))
        else:
            self.post(Event('snd_%s' % device.action, name=device.sys_name,
                            path=device.device_path))

        if self._debug:
            #print(device.sys_path)
            #print(device.sys_name)
            print(device.sys_number)
            #print(device.device_path)
            print(list(device.tags))
            #print(device.subsystem)
            #print(device.driver)
            #print(device.device_type)
            #print(device.device_node)
            print(device.device_number)
            print(list(device.device_links))
            print(device.is_initialized)
            #print(device.time_since_initialized)
            print(list(device.properties))
            print(device.attributes)
            #print(list(device.children))
            try:
                print(device.properties['ID_VENDOR'])
                print(device.properties['ID_VENDOR_FROM_DATABASE'])
                print(device.properties['ID_MODEL'])
                print(device.properties['ID_MODEL_FROM_DATABASE'])
            except:
                pass
