from collections import defaultdict
from loda.storage import EngineBase


class TestEngine(EngineBase):
    def __init__(self):
        super().__init__()
        self.__buckets = {}

    def _bucket_exists(self, name):
        return name in self.__buckets

    def _create_bucket(self, name):
        self.__buckets[name] = defaultdict(dict)

    def _has_value_in_key(self, bucket, key, value):
        return value in self.__buckets[bucket].get(key, [])

    def _has_key(self, bucket, key):
        return key in self.__buckets[bucket]

    def _get_value(self, bucket, key, default=None):
        return self.__buckets[bucket].get(key, default)

    def _get_values(self, bucket, key):
        for value in self.__buckets[bucket].get(key, list):
            yield value

    def _pop_value(self, bucket, key, default=None):
        return self.__buckets[bucket].pop(key, default)

    def _append_value(self, bucket, key, value):
        li = self.__buckets[bucket].get(key, [])
        li.append(value)

        return value

    def _set_value(self, bucket, key, value):
        if key == 'faulty' and value:
            raise Exception('Storage engine faulty')

        self.__buckets[bucket][key] = value

    def _delete_value(self, bucket, key):
        self.__buckets[bucket].pop(key)
