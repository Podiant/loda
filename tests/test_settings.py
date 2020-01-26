from loda.exceptions import ConfigError
from loda.settings import SettingsContainer, SettingsGroup
import os
import pytest


def test_container_not_dict():
    with pytest.raises(ConfigError) as ctx:
        SettingsContainer(None)

    assert ctx.value.args[0] == 'Settings must be a dict.'


def test_group_not_dict():
    with pytest.raises(ConfigError) as ctx:
        SettingsGroup(None, 'foo')

    assert ctx.value.args[0] == 'Settings must be a dict.'


def test_file_not_found():
    with pytest.raises(ConfigError) as ctx:
        SettingsContainer.from_file(
            os.path.join(
                os.path.dirname(__file__),
                'fixtures',
                'test_settings',
                'settings.yml'
            )
        )

    assert ctx.value.args[0] == 'Settings file not found.'


def test_bad_file():
    with pytest.raises(ConfigError) as ctx:
        SettingsContainer.from_file(
            os.path.join(
                os.path.dirname(__file__),
                'fixtures',
                'test_settings',
                'invalid.yaml'
            )
        )

    assert ctx.value.args[0] == 'Settings file syntax is invalid.'
