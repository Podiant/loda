from loda.exceptions import ConfigError, ProgrammingError
from loda.scripting import Script
from mock import patch
import os
import pytest


def test_config_not_dict():
    with pytest.raises(ConfigError) as ctx:
        Script([])

    assert ctx.value.args[0] == 'Config must be a dict.'


def test_storage_bad_string():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'storage': ['foo.bar']
            }
        )

    assert ctx.value.args[0] == 'storage must be a string.'


def test_storage_not_found():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'storage': 'foo.bar'
            }
        )

    assert ctx.value.args[0] == (
        'Storage engine module \'foo\' not found.'
    )


def test_storage_class_not_found():
    def imp(module):
        if module == 'loda.storage.engines.locmem':
            from loda.storage.engines import locmem
            return locmem

        if module == 'foo':
            class Module(object):
                pass

            return Module()

        pytest.fail('Untested module import \'%s\'' % module)

    with pytest.raises(ConfigError) as ctx:
        with patch('importlib.import_module', imp):
            Script(
                {
                    'storage': 'foo.bar'
                }
            )

    assert ctx.value.args[0] == 'Storage engine class \'bar\' not found.'


def test_storage_broken():
    def imp(module):
        if module == 'loda.storage.engines.locmem':
            from loda.storage.engines import locmem
            return locmem

        if module == 'foo':
            class Klass(object):
                def __init__(self, *args, **kwargs):
                    raise Exception('Foo')

            class Module(object):
                def __init__(self):
                    self.bar = Klass()

            return Module()

        pytest.fail('Untested module import \'%s\'' % module)

    with pytest.raises(ProgrammingError) as ctx:
        with patch('importlib.import_module', imp):
            Script(
                {
                    'storage': 'foo.bar'
                }
            )

    assert ctx.value.args[0] == 'Error loading \'foo.bar\' storage engine.'


def test_actors_not_list():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'actors': 'foo.bar'
            }
        )

    assert ctx.value.args[0] == 'actors must be a list.'


def test_actor_not_found():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'actors': ['foo.bar']
            }
        )

    assert ctx.value.args[0] == 'Actor \'foo.bar\' not found.'


def test_actor_class_not_found():
    def imp(module):
        if module == 'loda.storage.engines.locmem':
            from loda.storage.engines import locmem
            return locmem

        if module == 'foo.actors.bar':
            class Module(object):
                pass

            return Module()

        pytest.fail('Untested module import \'%s\'' % module)

    with pytest.raises(ProgrammingError) as ctx:
        with patch('importlib.import_module', imp):
            Script(
                {
                    'actors': ['foo.bar']
                }
            )

    assert ctx.value.args[0] == 'Actor class not found.'


def test_actor_broken():
    def imp(module):
        if module == 'loda.storage.engines.locmem':
            from loda.storage.engines import locmem
            return locmem

        if module == 'foo.actors.bar':
            class Module(object):
                def __init__(self, *args, **kwargs):
                    raise Exception('Foo')

            return Module()

        pytest.fail('Untested module import \'%s\'' % module)

    with pytest.raises(ProgrammingError) as ctx:
        with patch('importlib.import_module', imp):
            Script(
                {
                    'actors': ['foo.bar']
                }
            )

    assert ctx.value.args[0] == 'Error loading \'foo.bar\' actor.'


def test_stages_not_list():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'stages': 'foo'
            }
        )

    assert ctx.value.args[0] == 'stages must be a list.'


def test_action_not_dict():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'foo': None
            }
        )

    assert ctx.value.args[0] == 'stage config must be a dict or list.'


def test_action_not_in_stage():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'foo': {
                    'stage': 'foo'
                }
            }
        )

    assert ctx.value.args[0] == (
        'Action \'foo\' will not run as it does not belong to any defined '
        'stage.'
    )


def test_from_file():
    filename = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        'fixtures',
        'test_settings',
        'script.yaml'
    )

    def err(ex):
        raise ex

    script = Script.from_file(filename)
    script.on('line.error', err)
    script.run()
    bucket = script.storage.bucket('tests.actors.settings')
    assert bucket.get('foo') == 'baz'


def test_bad_file():
    filename = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        'fixtures',
        'test_settings',
        'empty.yaml'
    )

    with pytest.raises(ConfigError) as ctx:
        Script.from_file(filename)

    assert ctx.value.args[0] == (
        'Script must be a collection of key-value pairs.'
    )


def test_dry_run():
    filename = os.path.join(
        os.path.dirname(
            os.path.dirname(__file__)
        ),
        'fixtures',
        'test_items.yaml'
    )

    script = Script(
        {
            'actors': [
                'loda.inoreader',
                'loda.twitter'
            ],
            'builtin': [
                'hold foo for 1 minute',
                'release foo',
                'pick 1 from items',
                'pick 1 from items at random'
            ],
            'rss': [
                'get latest articles in starred folder'
            ],
            'twitter': [
                'follow @jack',
                'follow #podcasters',
                'find tweets from:jack',
                'tweet "hello Jack"',
                'rt 12345'
            ]
        }
    )

    script.fixtures.add('items', filename)
    script.dry_run = True
    script.run()
