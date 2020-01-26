from loda.eventing import EventEmitter


def test_on_off():
    pushed = []

    def callback(arg):
        pushed.append(arg)

    emitter = EventEmitter()
    emitter.on('test', callback)

    emitter.emit('test', 1)
    emitter.emit('test', 1)
    emitter.emit('test', 1)
    emitter.off('test', callback)
    emitter.off('test', lambda x: x)
    emitter.emit('test', 1)

    emitter.on('test', callback)
    emitter.off('test')
    emitter.emit('test', 1)

    assert sum(pushed) == 3
