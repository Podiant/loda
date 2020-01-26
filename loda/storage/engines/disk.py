from loda.storage import EngineBase
import json
import os


class FileSystemEngine(EngineBase):
    def __init__(self):
        super().__init__()
        self.__dir = os.path.join(os.getcwd(), '.loda')

        if not os.path.exists(self.__dir):
            os.mkdir(self.__dir)

    def __get_bucket_filename(self, name):
        return os.path.join(
            self.__dir,
            '%s.json' % name.replace('.', '__')
        )

    def _bucket_exists(self, name):
        filename = self.__get_bucket_filename(name)
        return os.path.exists(filename)

    def _create_bucket(self, name):
        filename = self.__get_bucket_filename(name)
        with open(filename, 'w') as f:
            f.write('{}')

    def _load_bucket(self, name):
        filename = self.__get_bucket_filename(name)
        with open(filename, 'rb') as f:
            return json.load(f)

    def _save_bucket(self, name, data):
        filename = self.__get_bucket_filename(name)
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def _has_value_in_key(self, bucket, key, value):
        li = self._load_bucket(bucket).get(key, [])
        return value in li

    def _has_key(self, bucket, key):
        return key in self._load_bucket(bucket)

    def _get_value(self, bucket, key, default=None):
        bk = self._load_bucket(bucket)
        return bk.get(key, default)

    def _get_values(self, bucket, key):
        bk = self._load_bucket(bucket)
        for value in bk.get(key, list):
            yield value

    def _pop_value(self, bucket, key, default=None):
        bk = self._load_bucket(bucket)
        value = bk.pop(key, default)
        self._save_bucket(bucket, bk)
        return value

    def _append_value(self, bucket, key, value):
        bk = self._load_bucket(bucket)
        li = bk.get(key, [])
        li.append(value)
        bk[key] = li
        self._save_bucket(bucket, bk)

        return value

    def _set_value(self, bucket, key, value):
        bk = self._load_bucket(bucket)
        bk[key] = value
        self._save_bucket(bucket, bk)

    def _delete_value(self, bucket, key):
        bk = self._load_bucket(bucket)
        bk.pop(key, None)
        self._save_bucket(bucket, bk)
