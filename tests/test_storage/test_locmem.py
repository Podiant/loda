from loda.storage.engines.locmem import LocalMemoryEngine


def test():
    engine = LocalMemoryEngine()
    bucket = engine.bucket('foo')
    bucket.put('foo', 'bar')

    bucket = engine.bucket('foo')
    assert bucket.has('foo')
    assert bucket.get('foo') == 'bar'

    bucket.push('items', 'one')
    assert list(bucket.pull('items')) == ['one']
    assert bucket.has('items', 'one')
    bucket.pop('items', 'one')
    assert not bucket.has('items', 'one')

    bucket.delete('items')
    assert not bucket.has('items')
