from logging import getLogger
from ..exceptions import FixtureError
import os
import yaml


class FixtureStore(object):
    def __init__(self):
        self.__fixtures = {}

    def add(self, name, config):
        self.__fixtures[name] = Fixture(config)

    def get(self, name):
        return self.__fixtures[name].read()


class Fixture(object):
    def __init__(self, filename):
        self.__logger = getLogger('loda')
        self.__filename = filename

    def read(self):
        if not hasattr(self, '__data'):
            self.__logger.debug(
                'Loading %s.' % os.path.split(self.__filename)[-1]
            )

            with open(self.__filename, 'rb') as f:
                try:
                    self.__data = yaml.load(
                        f,
                        Loader=yaml.FullLoader
                    )
                except yaml.error.YAMLError:
                    raise FixtureError('Syntax is invalid.')

        return self.__data
