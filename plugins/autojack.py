
import dbus

# Tascam hw:US16x08

class AutoJackPlugin:
    def __init__(self, session):
        self._session = session
        self._session.jack.attach(self)
        self._session.udev.attach(self)
        self._card = None

    def process_event(self, event):
        #print('autojack:', event.id)
        if event.id in ('snd_change', 'snd_device') and not self._session.jack.is_started():
            if event.vendor == 'M-Audio' and event.model == 'M-Track':
                print('autojack: start', event.vendor)
                self._session.jack.set_engine_parameter('driver', 'alsa')
                self._session.jack.set_driver_parameter('device', 'hw:MTrack')
                self._session.jack.set_driver_parameter('capture', None)
                self._session.jack.set_driver_parameter('playback', None)
                self._session.jack.set_driver_parameter('rate', dbus.UInt32(48000))
                self._session.jack.set_driver_parameter('period', dbus.UInt32(128))
                self._session.jack.set_driver_parameter('nperiods', dbus.UInt32(3))
                self._session.jack.set_driver_parameter('midi-driver', None)
                self._session.jack.start()
                self._card = event.path

            elif event.vendor == 'TEAC Corp.' and event.model == 'US-16x08':
                # Tascam US-16x08
                print('autojack: start Tascam')
                self._session.jack.set_engine_parameter('driver', 'alsa')
                self._session.jack.set_driver_parameter('device', 'hw:US16x08')
                self._session.jack.set_driver_parameter('capture', None)
                self._session.jack.set_driver_parameter('playback', None)
                self._session.jack.set_driver_parameter('rate', dbus.UInt32(48000))
                self._session.jack.set_driver_parameter('period', dbus.UInt32(64))
                self._session.jack.set_driver_parameter('nperiods', dbus.UInt32(3))
                self._session.jack.set_driver_parameter('midi-driver', 'seq')
                self._session.jack.start()
                self._card = event.path

        elif event.id == 'snd_remove' and event.path == self._card:
            #self._session.jack.stop()
            self._session.jack.set_engine_parameter('driver', 'dummy')
            if self._session.jack.is_started():
                self._session.jack.jackctl.SwitchMaster()
            #self._session.jack.jackctl.Exit()
