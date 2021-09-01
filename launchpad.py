
import rtmidi

from events import Event, Pub

# colours
RED = 0x0f
AMBER = 0x3f
GREEN = 0x3C

class LPRule:
    def check(self, event, ctl):
        if event.id == 'seq_client_start':
            if event.clientname == 'Launchpad Mini':
                ctl.add_device(LPController(ctl, event.clientid, event.clientname))
                return True


class LPController(Pub):
    def __init__(self, session, clientid, clientname):
        super().__init__()
        self._session = session
        self._session.jack.attach(self)
        self.clientid = clientid
        self.midiin = rtmidi.MidiIn(rtapi=rtmidi.API_LINUX_ALSA, name="Session Controller In")
        self.midiin.open_port(self._find_port(self.midiin.get_ports(), clientname))
        self.midiin.set_callback(self.on_midi_in)

        self.midiout = rtmidi.MidiOut(rtapi=rtmidi.API_LINUX_ALSA, name="Session Controller")
        self.midiout.open_port(self._find_port(self.midiout.get_ports(), clientname),
                               name='Launchpad')
        if self._session.jack.is_started():
            self.midiout.send_message([0xb0, 0x68, GREEN])
        else:
            self.midiout.send_message([0xb0, 0x68, RED])
        # test colours
        self.midiout.send_message([0x90, 0, 0x63])

    def __del__(self):
        print('delete', self)
        #self.midiin.close_port()
        self.midiin.delete()
        #self.midiout.close_port()
        self.midiout.delete()

    def _find_port(self, ports, clientname):
        prefix = clientname + ':'
        for (portnum, port) in enumerate(ports):
            if port.startswith(prefix):
                return portnum
        raise Error('port not found')

    def on_midi_in(self, msg, data):
        print('0x%x' % msg[0][0], msg)
        if msg[0] == [0xb0, 0x68, 0x7f]:
            if self._session.jack.is_started():
                print('starting')
                self._session.jack.stop()
            else:
                print('stopping')
                self._session.jack.start()

    def disconnect(self):
        self.midiin.close_port()
        self.midiout.close_port()
        #del self.midiin
        #del self.midiout
        #self.midiin.delete()
        #self.midiout.delete()

    def process_event(self, event):
        if event.id == 'jack_started':
            self.midiout.send_message([0xb0, 0x68, GREEN])
        elif event.id == 'jack_stopped':
            self.midiout.send_message([0xb0, 0x68, RED])
