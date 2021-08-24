
class Event:
    def __init__(self, eventid, **kwargs):
        self.id = eventid
        self._kwargs = kwargs

    def __repr__(self):
        return 'Event<%s: %s>' % (self.id, self._kwargs)

    def __getitem__(self, name):
        return self._kwargs[name]

    def __getattr__(self, name):
        return self._kwargs[name]

class Pub:
    def __init__(self):
        self._observers = []

    def attach(self, observer):
        self._observers.append(observer)

    def detach(self, observer):
        self._observers.remove(observer)

    def post(self, event):
        for observer in self._observers:
            observer.process_event(event)


if __name__ == '__main__':
    print(Event('test'))
    print(Event('test2', arg=1))
    print(Event('test2', arg=1)['arg'])
    print(Event('test2', arg=1).arg)
    print(Event('test2', arg=1).id)
