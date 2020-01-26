from loda.acting import ActorBase
from loda.exceptions import StorageError, PerformanceError
from loda.storage import EngineBase
from loda.storage.engines.locmem import LocalMemoryEngine
from mock import patch
import pytest


class BrokenEngine(EngineBase):
    def bucket(self):
        raise Exception('Bucket error')


class FaultyEngine(LocalMemoryEngine):
    def _has_key(self, key):
        raise Exception('Bucket error')

    def _get_value(self, key, default):
        raise Exception('Bucket error')

    def _pop_value(self, bucket, key, default=None):
        raise Exception('Bucket error')

    def _append_value(self, bucket, key, value):
        raise Exception('Bucket error')

    def _delete_value(self, bucket, key):
        raise Exception('Bucket error')


def test_bucket_error():
    with pytest.raises(StorageError) as ctx:
        engine = BrokenEngine()
        ActorBase(engine, [], {})

    assert ctx.value.args[0] == 'Error obtaining bucket.'


def _log(logger_method, actor_method=None):
    if not actor_method:
        actor_method = logger_method

    logs = []
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})
    func = getattr(actor, actor_method)

    with patch('logging.Logger.%s' % logger_method, logs.append):
        func(
            {
                'foo': 'bar'
            }
        )

    assert logs == ['{\n    "foo": "bar"\n}']


def test_debug():
    _log('debug')


def test_info():
    _log('info')


def test_warn():
    _log('warn', 'warning')


def test_fail():
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})

    with pytest.raises(PerformanceError):
        actor.fail('Failure')


def test_has():
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})
    assert not actor.has('foo')


def test_has_broken():
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})

    with pytest.raises(StorageError):
        actor.has('foo')


def test_get():
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})
    assert not actor.get('foo')


def test_get_broken():
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})

    with pytest.raises(StorageError):
        actor.get('foo')


def test_pull():
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})
    actor.push('foo', 1)
    assert list(actor.pull('foo')) == [1]


def test_pull_broken():
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})

    with pytest.raises(StorageError):
        list(actor.pull('foo'))


def test_pop():
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})
    actor.push('foo', 1)
    assert actor.pop('foo') == 1


def test_pop_broken():
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})

    with pytest.raises(StorageError):
        actor.pop('foo')


def test_push():
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})
    actor.push('foo', 1)
    assert actor.get('foo') == [1]


def test_push_broken():
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})

    with pytest.raises(StorageError):
        actor.push('foo', 1)


def test_delete():
    engine = LocalMemoryEngine()
    actor = ActorBase(engine, [], {})
    actor.put('foo', True)
    actor.delete('foo')
    assert actor.get('foo') is None


def test_delete_broken():
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})

    with pytest.raises(StorageError):
        actor.put('foo', True)
        actor.delete('foo')


def test_tag():
    tags = []
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})
    actor.on('tag', lambda t: tags.append(t))
    actor.tag('tag')
    assert tags == ['tag']


def test_untag():
    tags = []
    engine = FaultyEngine()
    actor = ActorBase(engine, [], {})
    actor.on('untag', lambda t: tags.append(t))
    actor.untag('tag')
    assert tags == ['tag']
