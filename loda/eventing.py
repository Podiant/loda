from collections import defaultdict


class EventEmitter(object):
    def __init__(self, *args, **kwargs):
        self.__callbacks = defaultdict(list)
        super().__init__(*args, **kwargs)

    def on(self, event, callback):
        self.__callbacks[event].append(callback)

    def off(self, event, callback=None):
        if callback is None:
            self.__callbacks[event] = []
        else:
            try:
                found = self.__callbacks[event].index(callback)
            except ValueError:
                return

            self.__callbacks[event].pop(found)

    def emit(self, event, *args, **kwargs):
        for callback in self.__callbacks[event]:
            callback(*args, **kwargs)
