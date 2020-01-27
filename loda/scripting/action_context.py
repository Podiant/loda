from logging import getLogger
from types import GeneratorType
from ..eventing import EventEmitter
from ..exceptions import (
    ConfigError,
    ScriptError,
    StorageError,
    FixtureError,
    PerformanceError
)

from .interrupts import Break


class ActionContext(EventEmitter):
    def __init__(self, script, name, config, action):
        super().__init__()
        self._script = script
        self._logger = getLogger('loda')
        self._unless = config.pop('exclude_tags', [])
        self._only = config.pop('tags', [])

        if isinstance(self._unless, str):
            self._unless = [self._unless]

        if not isinstance(self._unless, list):
            raise ConfigError('exclude_tags must be a string or list.')

        if isinstance(self._only, str):
            self._only = [self._only]

        if not isinstance(self._only, list):
            raise ConfigError('tags must be a string or list.')

        self._lines = config.pop('lines', [])
        self._action = action

    def _compile(self, expr):
        return self._script.compile_expression(expr)

    def _run_line(self, expr, callback=None):
        for tag in self._unless:
            if self._script.tagged(tag):
                return

        can_run = not any(self._only)
        if not can_run:
            for tag in self._only:
                if self._script.tagged(tag):
                    can_run = True
                    break

        if not can_run:
            return

        if expr == 'break':
            raise Break()

        compiled = self._compile(expr)
        self._logger.debug('Running \'%s\'.' % compiled)

        for actor in self._script.actors:
            if self._script.dry_run:
                groups, func = actor.match_test(compiled)
            else:
                groups, func = actor.match(compiled)

            if groups is not None:
                try:
                    result = func(*groups)
                except (ScriptError, StorageError, FixtureError):
                    raise
                except Exception:
                    raise PerformanceError(
                        'Error running line \'%s\'' % compiled
                    )

                if isinstance(result, GeneratorType):
                    for item in result:
                        if callback is not None and callable(callable):
                            try:
                                callback(item, self._script)
                            except Break:
                                break

                    if actor.greedy:
                        return
                elif actor.greedy:
                    return result

    def _prep_loop(self, action_name):
        try:
            template = self._script.action_templates[action_name]
        except KeyError:
            raise ScriptError('Action template $%s not found.' % action_name)

        template.prep()

    def _run_loop(self, action_name, context):
        template = self._script.action_templates[action_name]
        template.run(context)

    def _end_loop(self, action_name):
        template = self._script.action_templates[action_name]
        template.end()

    def prep(self):
        for line in self._lines:
            if isinstance(line, str):
                line = {
                    'expr': line
                }
            else:
                line['expr'] = line.pop('line')

            line = self._action.add(**line)
            line.on('run', self._run_line)
            line.on('loop.start', self._prep_loop)
            line.on('loop.iterate', self._run_loop)
            line.on('loop.end', self._end_loop)


class ActionTemplateContext(ActionContext):
    def run(self, context):
        old_compile = self._compile

        def compile(expr):
            return self._script.compile_expression(expr, context)

        self._compile = compile
        self._action.run(context)
        self._compile = old_compile

    def end(self):
        for line in self._action._lines:
            line.off('run', self._run_line)
            line.off('loop.start', self._prep_loop)
            line.off('loop.iterate', self._run_loop)
            line.off('loop.end', self._end_loop)
