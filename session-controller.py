#!/usr/bin/python

from pyalsa import alsaseq
import rtmidi

from events import Event, Pub

class Error(Exception):
    def __init__(self, string):
        self.msg = string


class AlsaseqMonitor(Pub):
    def __init__(self, debug=False):
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


class SessionController(Pub):
    def __init__(self):
        self.pad = None

    def process_event(self, event):
        if event.id == 'seq_client_start':
            if event.clientname == 'Launchpad Mini':
                self.pad = LPController(event.clientid, event.clientname)
                print(self.pad)
                
        elif event.id == 'seq_client_exit':
            print(event)
            if self.pad and event.clientid == self.pad.clientid:
                print('disconnected')
                self.pad.disconnect()
                self.pad = None

        else:
            print(event)

    def on_connect(self, id, name, portlist):
        if name == 'Launchpad Mini':
            print(name)
            for x in portlist:
                print(x)
            self.seq.connect_ports((self.seq.client_id, self.port),
                                   (id, 0))
            #self.port
            print('ports connected')
            print(int(alsaseq.SEQ_EVENT_NOTEON))
            event = alsaseq.SeqEvent(type=alsaseq.SEQ_EVENT_NOTEON)
            #print(event)
            event.dest = (id, 0)
            event.queue = alsaseq.SEQ_QUEUE_DIRECT
            event.time = 0.0
            event.set_data({'note.note': 16, 'note.velocity': 60})
            #print('event: %s %s' % (event, event.get_data()))
            print(event)
            self.seq.output_event(event)
            self.seq.drain_output()
        

class LPController(Pub):
    def __init__(self, clientid, clientname):
        self.clientid = clientid
        self.midiin = rtmidi.MidiIn(rtapi=rtmidi.API_LINUX_ALSA, name="Session Controller In")
        self.midiin.open_port(self._find_port(self.midiin.get_ports(), clientname))
        self.midiin.set_callback(self.on_midi_in)

        self.midiout = rtmidi.MidiOut(rtapi=rtmidi.API_LINUX_ALSA, name="Session Controller")
        self.midiout.open_port(self._find_port(self.midiout.get_ports(), clientname),
                               name='Launchpad')
        self.midiout.send_message([0xb0, 0x68, 0x60])
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

    def disconnect(self):
        self.midiin.close_port()
        self.midiout.close_port()
        #del self.midiin
        #del self.midiout
        #self.midiin.delete()
        #self.midiout.delete()

    def process_event(self, event):
        pass


if __name__ == '__main__':
    controller = SessionController()
    monitor = AlsaseqMonitor()
    monitor.attach(controller)
    monitor.refresh()

    while True:
        monitor.update()

