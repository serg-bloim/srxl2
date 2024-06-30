import time
from typing import TypeVar, Generic, List


def delay(ms):
    time.sleep(ms / 1000)


def cap(v, a, b):
    if v < a:
        return a
    elif v > b:
        return b
    else:
        return v


T = TypeVar('T')


class EventsHandler(Generic[T]):
    _listeners: List[T] = []

    def add_event_listener(self, el: T):
        self._listeners.append(el)

    def fire_event(self, evt_method, *args, **kwargs):
        for l in self._listeners:
            evt_method(l, *args, **kwargs)
