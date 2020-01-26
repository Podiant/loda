from logging import getLogger
from .exceptions import ConfigError
import os
import yaml


class SettingsGroup(object):
    def __init__(self, store, name):
        if not isinstance(store, dict):
            raise ConfigError('Settings must be a dict.')

        self.__store = dict(
            [
                (
                    key.upper(),
                    value
                ) for (
                    key,
                    value
                ) in store.items()
            ]
        )

        self.__name = name

    def __getattr__(self, attr):
        if attr in self.__store:
            return self.__store[attr]

        env = '%s_%s' % (
            self.__name.upper(),
            attr.upper()
        )

        return os.getenv(env)


class SettingsContainer(object):
    def __init__(self, store):
        if not isinstance(store, dict):
            raise ConfigError('Settings must be a dict.')

        self.__store = store
        self.__groups = {}
        self.__locked = True

    def __getattr__(self, attr):
        if attr not in self.__groups:
            self.__groups[attr] = SettingsGroup(
                self.__store.get(attr, {}),
                attr.split('.')[-1]
            )

        return self.__groups[attr]

    @classmethod
    def from_file(self, filename):
        logger = getLogger('loda')

        if not os.path.exists(filename):
            raise ConfigError('Settings file not found.')

        logger.debug('Loading settings.yaml.')

        try:
            config = yaml.load(
                open(filename, 'r'),
                Loader=yaml.FullLoader
            )
        except yaml.error.YAMLError:
            raise ConfigError('Settings file syntax is invalid.')

        return SettingsContainer(config)
