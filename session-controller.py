#!/usr/bin/python

import dbus
import dbus.mainloop.glib
import pyudev
from pyudev_glib import MonitorObserver

import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

from gi.repository import GLib
from pyalsa import alsaseq
import rtmidi

from sessionlib.events import Event, Pub

class Error(Exception):
    def __init__(self, string):
        self.msg = string


class AlsaseqMonitor(Pub):
    def __init__(self, debug=False):
        super().__init__()
        self._debug = debug
        self.seq = alsaseq.Sequencer(clientname='session-control-monitor')
        self.port = self.seq.create_simple_port(
            name='System Announce Receiver',
            type=alsaseq.SEQ_PORT_TYPE_APPLICATION,
            caps=alsaseq.SEQ_PORT_CAP_WRITE|alsaseq.SEQ_PORT_CAP_NO_EXPORT)
        self.seq.connect_ports((alsaseq.SEQ_CLIENT_SYSTEM, alsaseq.SEQ_PORT_SYSTEM_ANNOUNCE),
                               (self.seq.client_id, self.port))

    def refresh(self):
        # initialise connections
        for clientname, clientid, portlist in self.seq.connection_list():
            #self.connect_device(clientid, clientname, portlist)
            self.post(Event('seq_client_start', clientid=clientid,
                            clientname=clientname, portlist=portlist))

    def update(self, timeout=1000):
        events = self.seq.receive_events(timeout=timeout, maxevents=1)
        for event in events:
            if self._debug:
                print(event.type)
                print(event.get_data())
            if event.type == alsaseq.SEQ_EVENT_CLIENT_START:
                for clientname, clientid, portlist in self.seq.connection_list():
                    if clientid == event.get_data()['addr.client']:
                        self.post(Event('seq_client_start', clientid=clientid,
                                        clientname=clientname, portlist=portlist))
            elif event.type == alsaseq.SEQ_EVENT_CLIENT_EXIT:
                self.post(Event('seq_client_exit', clientid=event.get_data()['addr.client']))


# jack_retry decorator
# org.freedesktop.DBus.Error.ServiceUnknown occurs if the Jack DBus service
# has exited since the interface was initialised; reconnect and retry
def jack_retry(func):
    def inner(obj, *args, **kwargs):
        try:
            return func(obj, *args, **kwargs)
        except dbus.exceptions.DBusException as e:
            print('jack_retry failed:', e.get_dbus_name())
            obj._reconnect()
            return func(obj, *args, **kwargs)
    return inner


class JackMonitor(Pub):
    def __init__(self, bus=None):
        super().__init__()
        self.bus = bus or dbus.SessionBus()
        self.connect('ServerStarted', self.on_started)
        self.connect('ServerStopped', self.on_stopped)
        self._reconnect()

    def _reconnect(self):
        self.jack = self.bus.get_object('org.jackaudio.service', '/org/jackaudio/Controller')
        self.jackctl = dbus.Interface(self.jack, dbus_interface='org.jackaudio.JackControl')
        self.jackcfg = dbus.Interface(self.jack, dbus_interface='org.jackaudio.Configure')

    def connect(self, signal, callback):
        self.bus.add_signal_receiver(callback, dbus_interface='org.jackaudio.JackControl',
                                     signal_name=signal)

    def on_started(self, *args, **kwargs):
        self.post(Event('jack_started'))

    def on_stopped(self, *args, **kwargs):
        self.post(Event('jack_stopped'))

    @jack_retry
    def is_started(self):
        return self.jackctl.IsStarted()

    @jack_retry
    def start(self):
        return self.jackctl.StartServer()

    @jack_retry
    def stop(self):
        return self.jackctl.StopServer()

    @jack_retry
    def get_engine_parameter(self, parameter):
        return self.jackcfg.GetParameterValue(['engine', parameter])[2]

    @jack_retry
    def set_engine_parameter(self, parameter, value):
        if value is None:
            return bool(self.jackcfg.ResetParameterValue(['engine', parameter]))
        else:
            return bool(self.jackcfg.SetParameterValue(['engine', parameter], value))

    @jack_retry
    def get_driver_parameter(self, parameter):
        return self.jackcfg.GetParameterValue(['driver', parameter])[2]

    @jack_retry
    def set_driver_parameter(self, parameter, value):
        if value is None:
            return bool(self.jackcfg.ResetParameterValue(['driver', parameter]))
        else:
            return bool(self.jackcfg.SetParameterValue(['driver', parameter], value))


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
