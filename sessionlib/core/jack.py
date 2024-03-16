import dbus

from ..events import Event, Pub


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
