from loda.storage.engines.redis import RedisEngine
from mock import patch
from fakeredis import FakeStrictRedis


@patch('redis.StrictRedis', FakeStrictRedis)
def test():
    engine = RedisEngine()
    bucket = engine.bucket('foo')
    assert not bucket.has('foo')
    bucket.put('foo', 'bar')

    bucket = engine.bucket('foo')
    assert bucket.has('foo')
    assert bucket.get('foo') == 'bar'

    assert not bucket.has('items', 'one')
    assert not bucket.pop('items')
    assert not bucket.get('items')

    bucket.push('items', 'one')
    bucket.push('items', 'two')
    assert list(bucket.pull('items')) == ['one', 'two']
    assert bucket.has('items', 'one')
    bucket.pop('items', 'two')
    assert not bucket.has('items', 'two')

    bucket.delete('items')
    assert not bucket.has('items')
