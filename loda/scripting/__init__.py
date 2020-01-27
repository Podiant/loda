from logging import getLogger
from jinja2 import Template
from ..actors import default as default_actors
from ..actors.builtin import HoldActor, PickActor
from ..eventing import EventEmitter
from ..settings import SettingsContainer
from ..storage import default as default_storage
from ..exceptions import (
    ConfigError,
    ProgrammingError,
    ScriptError,
    StorageError,
    PerformanceError,
    FixtureError
)

from .actions import ActionTemplate
from .action_context import ActionContext, ActionTemplateContext
from .fixtures import FixtureStore
from .stages import Stage
import importlib
import os
import yaml


class Script(EventEmitter):
    def __init__(self, config):
        if not isinstance(config, dict):
            raise ConfigError('Config must be a dict.')

        super().__init__()
        self.dry_run = False
        self.__logger = getLogger('loda')
        self.__tags = []

        # Get storage handler
        storage = config.pop('storage', default_storage)
        if not isinstance(storage, str):
            raise ConfigError('storage must be a string.')

        try:
            self.storage = self.__find_storage(storage)
        except (ConfigError, ProgrammingError):
            raise

        self.fixtures = FixtureStore()
        self.context = {}

        # Get action handlers
        actors = config.pop('actors', default_actors)
        if not isinstance(actors, list):
            raise ConfigError('actors must be a list.')

        self.actors = [self.__find_actor(a) for a in actors]
        self.actors.extend(
            (
                self.__wake_actor(HoldActor),
                self.__wake_actor(PickActor)
            )
        )

        # Get action stages
        stages = config.pop('stages', ['default'])
        if not isinstance(stages, list):
            raise ConfigError('stages must be a list.')

        self.stages = [Stage(self, c) for c in stages]
        self.action_templates = {}

        for action_name, action_config in config.items():
            if isinstance(action_config, list):
                action_config = {
                    'lines': action_config
                }

            if not isinstance(action_config, dict):
                if not action_name.startswith('$'):
                    raise ConfigError(
                        'stage config must be a dict or list.'
                    )

            if not action_name.startswith('$'):
                action = None
                stage_name = action_config.pop('stage', 'default')

                for stage in self.stages:
                    if stage.name == stage_name:
                        action = stage.add(action_name)
                        break

                if action is None:
                    raise ConfigError(
                        (
                            'Action \'%s\' will not run as it '
                            'does not belong to any defined stage.'
                        ) % action_name
                    )

                action = ActionContext(
                    self,
                    action_name,
                    action_config,
                    action
                )

                action.prep()
            else:
                action = ActionTemplateContext(
                    self,
                    action_name[1:],
                    action_config,
                    ActionTemplate(self, action_name)
                )

                self.action_templates[action_name[1:]] = action

    @classmethod
    def from_file(self, filename):
        logger = getLogger('loda')
        logger.debug('Configuring script.')

        if not os.path.exists(filename):
            raise ConfigError('Script not found.')

        logger.debug('Loading script.yaml.')

        try:
            config = yaml.load(
                open(filename, 'r'),
                Loader=yaml.FullLoader
            )
        except yaml.error.YAMLError:
            raise ConfigError('Script file syntax is invalid.')

        if not isinstance(config, dict):
            raise ConfigError(
                'Script must be a collection of key-value pairs.'
            )

        fixtures = config.pop('fixtures', [])

        try:
            obj = Script(config)
        except (ConfigError, ProgrammingError, ScriptError, StorageError):
            raise

        if any(fixtures):
            logger.debug('Loading fixtures.')
            for fixture_name in fixtures:
                fixture_filename = os.path.join(
                    os.path.dirname(filename),
                    'fixtures',
                    '%s.yaml' % fixture_name
                )

                if not os.path.exists(fixture_filename):
                    raise FixtureError(
                        'Fixture \'%s\' not found.' % fixture_name
                    )

                obj.fixtures.add(fixture_name, fixture_filename)

        settings_filename = os.path.join(
            os.path.dirname(filename),
            'settings.yaml'
        )

        if os.path.exists(settings_filename):
            self.settings = SettingsContainer.from_file(
                settings_filename
            )
        else:
            self.settings = SettingsContainer({})

        return obj

    def __find_actor(self, name):
        split = name.rsplit('.', 1)
        full_name = '%s.actors.%s' % tuple(split)

        try:
            try:
                module = importlib.import_module(full_name)
            except ModuleNotFoundError:
                raise ConfigError('Actor \'%s\' not found.' % name)

            try:
                klass = getattr(module, 'Actor')
            except AttributeError:
                raise ProgrammingError('Actor class not found.')

            return self.__wake_actor(klass)

        except (ConfigError, ProgrammingError):
            raise
        except Exception:
            raise ProgrammingError('Error loading \'%s\' actor.' % name)

    def __wake_actor(self, klass):
        actor = klass(self.storage, self.fixtures, self.context)
        actor.on('tag', self.__tag)
        actor.on('untag', self.__untag)
        actor.on('settings.load', self.__load_group_settings)
        return actor

    def __load_group_settings(self, group, callback):
        settings = getattr(self.settings, group)
        callback(settings)

    def __find_storage(self, name):
        try:
            module, klass = name.rsplit('.', 1)

            try:
                module = importlib.import_module(module)
            except ModuleNotFoundError:
                raise ConfigError(
                    'Storage engine module \'%s\' not found.' % module
                )

            try:
                klass = getattr(module, klass)
            except AttributeError:
                raise ConfigError(
                    'Storage engine class \'%s\' not found.' % klass
                )

            return klass()

        except (ConfigError, ProgrammingError):
            raise
        except Exception:
            raise ProgrammingError(
                'Error loading \'%s\' storage engine.' % name
            )

    def run(self):
        for stage in self.stages:
            try:
                stage.run()
            except (ScriptError, StorageError, FixtureError):
                raise
            except PerformanceError as ex:
                self.emit('line.error', ex)

    def compile_expression(self, expr, extra_context={}):
        context = dict(**self.context)
        context.update(extra_context)

        template = Template(expr)
        compiled = template.render(**context)

        return compiled

    def tagged(self, name):
        return name in self.__tags

    def __tag(self, name):
        if name not in self.__tags:
            self.__logger.debug('Set #%s tag' % name)
            self.__tags.append(name)

    def __untag(self, name):
        try:
            index = self.__tags.index(name)
        except ValueError:
            return

        self.__tags.pop(index)
        self.__logger.debug('Unset #%s tag' % name)
