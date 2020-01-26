from logging import getLogger


class Bucket(object):
    def __init__(self, name, engine):
        self.name = name
        self.__logger = getLogger('loda')
        self.__engine = engine

    def has(self, key, value=None):
        if value is not None:
            return self.__engine._has_value_in_key(self.name, key, value)

        return self.__engine._has_key(self.name, key)

    def get(self, key, default=None):
        return self.__engine._get_value(self.name, key, default)

    def pull(self, key):
        for item in self.__engine._get_values(self.name, key):
            yield item

    def pop(self, key, default=None):
        return self.__engine._pop_value(self.name, key, default)

    def push(self, key, value):
        return self.__engine._append_value(self.name, key, value)

    def put(self, key, value):
        return self.__engine._set_value(self.name, key, value)

    def delete(self, key):
        return self.__engine._delete_value(self.name, key)


class EngineBase(object):
    def __init__(self):
        self.__logger = getLogger('loda')

    def _bucket_exists(self, name):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _create_bucket(self, name):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _has_key(self, bucket, key):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _has_value_in_key(self, bucket, key, value):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _get_value(self, bucket, key, default=None):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _get_values(self, bucket, key):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _pop_value(self, bucket, key, default=None):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _append_value(self, bucket, key, value):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _set_value(self, bucket, key, value):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def _delete_value(self, bucket, key):  # pragma: no cover
        raise NotImplementedError('Method not impleented')

    def bucket(self, name):
        if not self._bucket_exists(name):
            self._create_bucket(name)

        return Bucket(name, self)


default = 'loda.storage.engines.locmem.LocalMemoryEngine'
