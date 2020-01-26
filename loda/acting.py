from logging import getLogger
from .eventing import EventEmitter
from .exceptions import StorageError, PerformanceError
from .settings import SettingsGroup
import json
import re


class ActorBase(EventEmitter):
    receive = []
    greedy = False

    def __init__(self, storage, fixtures, context):
        super().__init__()

        self.__logger = getLogger('loda')

        try:
            self.__bucket = storage.bucket(
                type(self).__module__
            )
        except Exception:
            raise StorageError('Error obtaining bucket.')

        self.__fixtures = fixtures
        self.context = context

    def match(self, expr):
        if isinstance(self.receive, list):
            for regex in self.receive:
                match = re.search(regex, expr)
                if match is not None:
                    return match.groups(), self.perform
        elif isinstance(self.receive, dict):
            for func, regexes in self.receive.items():
                for regex in regexes:
                    match = re.search(regex, expr)
                    if match is not None:
                        return match.groups(), getattr(self, func)

        return None, None

    def perform(self, *args):  # pragma: no cover
        raise NotImplementedError('Method not implemented')

    def info(self, message):
        if not isinstance(message, str):
            message = json.dumps(message, indent=4)

        self.__logger.info(message)

    def debug(self, message):
        if not isinstance(message, str):
            message = json.dumps(message, indent=4)

        self.__logger.debug(message)

    def warn(self, message):
        if not isinstance(message, str):
            message = json.dumps(message, indent=4)

        self.__logger.warn(message)

    def warning(self, message):
        self.warn(message)

    def fail(self, *args, **kwargs):
        raise PerformanceError(*args, **kwargs)

    def has(self, key, value=None):
        try:
            return self.__bucket.has(key, value)
        except Exception:
            raise StorageError('Error checking for value in bucket')

    def get(self, key, default=None):
        try:
            return self.__bucket.get(key, default)
        except Exception:
            raise StorageError('Error getting value from bucket')

    def pull(self, key):
        try:
            for item in self.__bucket.pull(key):
                yield item
        except Exception:
            raise StorageError('Error pulling values from bucket')

    def pop(self, key, default=None):
        try:
            return self.__bucket.pop(key, default)
        except Exception:
            raise StorageError('Error popping value from bucket')

    def push(self, key, value):
        try:
            return self.__bucket.push(key, value)
        except Exception:
            raise StorageError('Error pushing value to bucket')

    def put(self, key, value):
        try:
            return self.__bucket.put(key, value)
        except Exception:
            raise StorageError('Error setting value in bucket.')

    def delete(self, key):
        try:
            return self.__bucket.delete(key)
        except Exception:
            raise StorageError('Error deleting value from bucket')

    def tag(self, name):
        self.emit('tag', name)

    def untag(self, name):
        self.emit('untag', name)

    def fixture(self, name):
        return self.__fixtures.get(name)

    @property
    def settings(self):
        if not hasattr(self, '_settings'):
            group_parts = type(self).__module__.split('.')
            new_group_parts = []

            for part in group_parts:
                if part in ('actors', 'acting', 'builtin'):
                    continue

                new_group_parts.append(part)

            group = '.'.join(new_group_parts)

            def callback(value):
                self._settings = value

            self.emit('settings.load', group, callback)

            if not hasattr(self, '_settings'):
                self._settings = SettingsGroup(
                    {},
                    new_group_parts[-1]
                )

        return self._settings
