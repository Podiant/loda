from logging import getLogger
from ..eventing import EventEmitter
from ..exceptions import ConfigError
from .logic import PositiveCondition, NegativeCondition


class Line(EventEmitter):
    def __init__(self, action, expr, **kwargs):
        super().__init__()
        self.__logger = getLogger('loda')
        self.__action = action
        self.__conditions = []
        self.expr = expr

        conditions = kwargs.pop('if', [])
        if isinstance(conditions, str):
            self.__conditions.append(
                PositiveCondition(conditions)
            )
        elif isinstance(conditions, list):
            for condition in conditions:
                self.__conditions.append(
                    PositiveCondition(condition)
                )
        else:
            raise ConfigError('if conditions must be a string or list.')

        conditions = kwargs.pop('unless', [])
        if isinstance(conditions, str):
            self.__conditions.append(
                NegativeCondition(conditions)
            )
        elif isinstance(conditions, list):
            for condition in conditions:
                self.__conditions.append(
                    NegativeCondition(condition)
                )
        else:
            raise ConfigError('unless conditions must be a string or list.')

        self.__loop = kwargs.pop('each', None)

        for key in kwargs.keys():
            raise TypeError(
                '__init__() got unexpected keyword argument \'%s\'' % key
            )

    def matches_condition(self, context):
        for condition in self.__conditions:
            if not condition.met(context):
                return False

        return True

    def run(self):
        def callback(result, script):
            if self.__loop:
                self.emit('loop.iterate', self.__loop[1:], result)

        if self.__loop:
            self.emit('loop.start', self.__loop[1:])

        self.emit('run', self.expr, callback)

        if self.__loop:
            self.emit('loop.end', self.__loop[1:])
