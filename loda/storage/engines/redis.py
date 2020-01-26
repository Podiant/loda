from loda.exceptions import ConfigError
from loda.storage import EngineBase
import pickle
import os


REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')


class RedisEngine(EngineBase):
    def __init__(self):
        try:
            from redis import StrictRedis
        except Exception:  # pragma: no cover
            raise ConfigError('loda.redis requires redis.')

        super().__init__()
        self.__redis = StrictRedis.from_url(REDIS_URL)

    def _bucket_exists(self, name):
        return name in self.__redis

    def _create_bucket(self, name):
        pass

    def _has_value_in_key(self, bucket, key, value):
        if self.__redis.hexists(bucket, key):
            pickled = self.__redis.hget(bucket, key)
            unpickled = pickle.loads(pickled)
            return value in unpickled

        return False

    def _has_key(self, bucket, key):
        return self.__redis.hexists(bucket, key)

    def _get_value(self, bucket, key, default=None):
        if self.__redis.hexists(bucket, key):
            pickled = self.__redis.hget(bucket, key)
            unpickled = pickle.loads(pickled)
            return unpickled

        return default

    def _get_values(self, bucket, key):
        if self.__redis.hexists(bucket, key):
            pickled = self.__redis.hget(bucket, key)
            unpickled = pickle.loads(pickled)

            for value in unpickled:
                yield value

    def _pop_value(self, bucket, key, default=None):
        if self.__redis.hexists(bucket, key):
            pickled = self.__redis.hget(bucket, key)
            unpickled = pickle.loads(pickled)
            value = unpickled.pop()
            pickled = pickle.dumps(unpickled)
            self.__redis.hset(bucket, key, pickled)
            return value

        return default

    def _append_value(self, bucket, key, value):
        if self.__redis.hexists(bucket, key):
            pickled = self.__redis.hget(bucket, key)
            unpickled = pickle.loads(pickled)
            unpickled.append(value)
        else:
            unpickled = [value]

        pickled = pickle.dumps(unpickled)
        self.__redis.hset(bucket, key, pickled)

    def _set_value(self, bucket, key, value):
        pickled = pickle.dumps(value)
        self.__redis.hset(bucket, key, pickled)

    def _delete_value(self, bucket, key):
        if self.__redis.hexists(bucket, key):
            self.__redis.hdel(bucket, key)
