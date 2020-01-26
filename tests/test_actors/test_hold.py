from datetime import datetime, timedelta
from loda.actors.builtin.hold import Actor, HoldingHelper
from loda.storage.engines.locmem import LocalMemoryEngine
from mock import patch


EPOCH = datetime(2020, 1, 1, 0, 0, 0)


class MockDatetime(datetime):
    @classmethod
    def utcnow(cls):
        return EPOCH


def parse(**td_kwargs):
    def f(str, *args, **kwargs):
        return EPOCH + timedelta(**td_kwargs)

    return f


@patch('datetime.datetime', MockDatetime)
@patch('dateparser.parse', parse(seconds=60))
def test_hold_value_for():
    engine = LocalMemoryEngine()
    actor = Actor(engine, [], {})

    args, func = actor.match('hold foo for 1 minute')
    func(*args)

    bucket = engine.bucket('loda.actors.builtin.hold')
    assert bucket.get('foo') == 1577836860


@patch('datetime.datetime', MockDatetime)
@patch('dateparser.parse', parse(hours=24))
def test_hold_value_until():
    engine = LocalMemoryEngine()
    actor = Actor(engine, [], {})

    args, func = actor.match('hold foo for until tomorrow')
    func(*args)

    bucket = engine.bucket('loda.actors.builtin.hold')
    assert bucket.get('foo') == 1577923200


def test_release():
    engine = LocalMemoryEngine()
    bucket = engine.bucket('loda.actors.builtin.hold')
    bucket.put('foo', 0)
    actor = Actor(engine, [], {})

    args, func = actor.match('release foo')
    func(*args)
    assert not bucket.has('foo')


@patch('datetime.datetime', MockDatetime)
def test_expired():
    engine = LocalMemoryEngine()
    bucket = engine.bucket('loda.actors.builtin.hold')
    bucket.put('foo', 1577836800)
    helper = HoldingHelper(engine)
    assert not helper['foo']
    assert not helper['foo']


@patch('datetime.datetime', MockDatetime)
def test_future():
    engine = LocalMemoryEngine()
    bucket = engine.bucket('loda.actors.builtin.hold')
    bucket.put('foo', 1577923200)
    helper = HoldingHelper(engine)
    assert helper['foo']
