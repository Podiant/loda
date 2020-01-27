from logging import getLogger
from ..eventing import EventEmitter
from ..exceptions import (
    StorageError,
    FixtureError,
    PerformanceError
)

from .actions import Action


class Stage(EventEmitter):
    def __init__(self, script, name):
        super().__init__()
        self.__logger = getLogger('loda')
        self.__script = script
        self.__actions = []
        self.name = name

    def add(self, name):
        action = Action(self.__script, name)
        self.__logger.debug(
            'Adding \'%s\' action to \'%s\' stage.' % (
                action.name,
                self.name
            )
        )

        self.__actions.append(action)
        return action

    def run(self):
        self.__logger.debug('Running \'%s\' stage.' % self.name)

        for action in self.__actions:
            try:
                action.run()
            except (StorageError, FixtureError):
                raise
            except PerformanceError as ex:
                self.__script.emit('action.error', ex)
