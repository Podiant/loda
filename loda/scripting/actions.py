from logging import getLogger
from ..actors.builtin import HoldingHelper
from ..eventing import EventEmitter
from ..exceptions import ConfigError
from .lines import Line


class Action(EventEmitter):
    def __init__(self, script, name):
        super().__init__()
        self._logger = getLogger('loda')
        self._script = script
        self._lines = []
        self.name = name

    def add(self, **config):
        try:
            line = Line(self, **config)
        except TypeError:
            raise ConfigError(
                'Line configruation invalid.', config
            )

        self._logger.debug(
            'Adding \'%s\' line to \'%s\' action.' % (
                line.expr,
                self.name
            )
        )

        self._lines.append(line)
        return line

    def run(self):
        self._logger.debug('Running \'%s\' action.' % self.name)
        context = dict(
            holding=HoldingHelper(self._script.storage)
        )

        for line in self._lines:
            context.update(
                dict(**self._script.context)
            )

            if line.matches_condition(context):
                line.run()


class ActionTemplate(Action):
    def run(self, loop_context):
        self._logger.debug('Running \'%s\' action.' % self.name)
        context = dict(
            holding=HoldingHelper(self._script.storage)
        )

        for line in self._lines:
            context.update(
                dict(**self._script.context)
            )

            context.update(
                dict(**loop_context)
            )

            if line.matches_condition(context):
                line.run()
