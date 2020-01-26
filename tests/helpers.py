from tempfile import mkdtemp
import json
import os


def getcwd(dirname=None, temp=False):
    def f():
        if temp:
            return mkdtemp()

        d = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            dirname.replace('.', '/')
        )

        if not os.path.exists(d):
            raise Exception('Fixture \'%s\' not found' % dirname)

        return d

    return f


class MockResponse(object):
    def __init__(self, content):
        self.content = content
        self.json = lambda: json.load(content)

    def raise_for_status(self):
        pass


def mock_response(filename, paged=None):
    def f(url, *args, **kwargs):
        params = kwargs.get('params', {})

        n = os.path.join(
            os.path.dirname(__file__),
            'fixtures',
            'responses',
            filename.replace('.', '/')
        )

        if paged:
            n += '_page%s' % params[paged]

        n += '.json'

        if not os.path.exists(n):
            raise Exception('Fixture \'%s\' not found' % filename)

        return MockResponse(
            open(n, 'rb')
        )

    return f
