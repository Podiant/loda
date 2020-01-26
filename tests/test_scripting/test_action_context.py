from loda.exceptions import ConfigError
from loda.scripting import Script
import pytest


def test_generator_type():
    script = Script(
        {
            'actors': [
                'tests.generator'
            ],
            'default': ['generate']
        }
    )

    script.run()
    bucket = script.storage.bucket('tests.actors.generator')
    assert bucket.get('counter') == 5


def test_greedy_actor():
    script = Script(
        {
            'actors': [
                'tests.greedy'
            ],
            'default': [
                {
                    'line': 'perform'
                }
            ]
        }
    )

    script.run()


def test_tags_false():
    script = Script(
        {
            'actors': ['tests.generator'],
            'default': {
                'tags': 'performed',
                'lines': ['generate']
            }
        }
    )

    script.run()
    bucket = script.storage.bucket('tests.actors.generator')
    assert bucket.get('counter') is None


def test_tags_invalid():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'actors': ['tests.generator'],
                'default': {
                    'tags': 1,
                    'lines': ['generate']
                }
            }
        )

    assert ctx.value.args[0] == 'tags must be a string or list.'


def test_tags_true():
    script = Script(
        {
            'actors': [
                'tests.greedy',
                'tests.generator'
            ],
            'perform': ['perform'],
            'generate': {
                'tags': 'performed',
                'lines': ['generate']
            }
        }
    )

    script.run()
    bucket = script.storage.bucket('tests.actors.generator')
    assert bucket.get('counter') == 5


def test_exclude_tags():
    script = Script(
        {
            'actors': [
                'tests.greedy',
                'tests.generator'
            ],
            'perform': {
                'lines': ['perform']
            },
            'generate': {
                'exclude_tags': 'performed',
                'lines': ['generate']
            }
        }
    )

    script.run()
    bucket = script.storage.bucket('tests.actors.generator')
    assert bucket.get('counter') is None


def test_exclude_tags_invalid():
    with pytest.raises(ConfigError) as ctx:
        Script(
            {
                'actors': ['tests.generator'],
                'default': {
                    'exclude_tags': False,
                    'lines': ['generate']
                }
            }
        )

    assert ctx.value.args[0] == 'exclude_tags must be a string or list.'
