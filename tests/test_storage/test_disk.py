from loda.storage.engines.disk import FileSystemEngine
from ..helpers import getcwd
from mock import patch


@patch('os.getcwd', getcwd(temp=True))
def test():
    engine = FileSystemEngine()
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
