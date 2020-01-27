from loda.exceptions import ConfigError, ScriptError
from loda.scripting import Script
import pytest


def test_if():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            'default': [
                'generate',
                {
                    'line': 'set foo = bar',
                    'if': 'counter == 5'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    script.on('line.error', err)
    script.run()

    assert script.context['counter'] == 5
    bucket = script.storage.bucket('tests.actors.logic')
    assert bucket.get('foo') == 'bar'


def test_if_list():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            'default': [
                {
                    'line': 'generate',
                    'if': ['True']
                },
                {
                    'line': 'set foo = bar',
                    'if': 'counter == 5'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    script.on('line.error', err)
    script.run()

    assert script.context['counter'] == 5
    bucket = script.storage.bucket('tests.actors.logic')
    assert bucket.get('foo') == 'bar'


def test_if_invalid():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'default': [
                    {
                        'line': 'do',
                        'if': True
                    }
                ]
            }
        )

    assert ctx.value.args[0] == 'if conditions must be a string or list.'


def test_unless():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            'default': [
                'generate',
                {
                    'line': 'set foo = bar',
                    'unless': 'counter == 5'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    script.on('line.error', err)
    script.run()

    assert script.context['counter'] == 5
    bucket = script.storage.bucket('tests.actors.logic')
    assert bucket.get('foo') is None


def test_unless_list():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            'default': [
                {
                    'line': 'generate',
                    'unless': ['False']
                },
                {
                    'line': 'set foo = bar',
                    'unless': 'counter == 5'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    script.on('line.error', err)
    script.run()

    assert script.context['counter'] == 5
    bucket = script.storage.bucket('tests.actors.logic')
    assert bucket.get('foo') is None


def test_unless_invalid():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'default': [
                    {
                        'line': 'do',
                        'unless': True
                    }
                ]
            }
        )

    assert ctx.value.args[0] == 'unless conditions must be a string or list.'


def test_extra_config():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'default': [
                    {
                        'line': 'do',
                        'foo': 'bar'
                    }
                ]
            }
        )

    assert ctx.value.args[0] == 'Line configruation invalid.'


def test_each_increment():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            '$loop': ['increment foo'],
            'default': [
                {
                    'line': 'generate',
                    'each': '$loop'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    script.on('line.error', err)
    script.run()

    assert script.context['counter'] == 5
    bucket = script.storage.bucket('tests.actors.logic')
    assert bucket.get('foo') == 5


def test_each_set():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            '$loop': ['set foo = {{ counter }}'],
            'default': [
                {
                    'line': 'generate',
                    'each': '$loop'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    script.on('line.error', err)
    script.run()

    assert script.context['counter'] == 5
    bucket = script.storage.bucket('tests.actors.logic')
    assert bucket.get('foo') == '5'


def test_each_break():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            '$loop': [
                'increment foo',
                'break'
            ],
            'default': [
                {
                    'line': 'generate',
                    'each': '$loop'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    script.on('line.error', err)
    script.run()

    assert script.context['counter'] == 1
    bucket = script.storage.bucket('tests.actors.logic')
    assert bucket.get('foo') == 1


def test_each_invalid():
    script = Script(
        {
            'actors': [
                'tests.generator',
                'tests.logic'
            ],
            'default': [
                {
                    'line': 'generate',
                    'each': '$loop'
                }
            ]
        }
    )

    def err(ex):
        raise ex

    with pytest.raises(ScriptError):
        script.run()
