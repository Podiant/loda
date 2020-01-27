from ...acting import ActorBase
import dateparser
import datetime
import time


LANGUAGE = 'en'


class Actor(ActorBase):
    receive = {
        'hold': [
            r'^hold ([^ ]+) for (.*)',
            r'^hold ([^ ]+) until (.*)'
        ],
        'release': [
            r'^release (.*)'
        ]
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def hold(self, name, timeframe):
        current_timestamp = time.mktime(
            datetime.datetime.utcnow().timetuple()
        )

        deadline = dateparser.parse(
            'in %s' % timeframe,
            languages=[LANGUAGE],
            settings={
                'PREFER_DATES_FROM': 'future'
            }
        )

        timestamp = time.mktime(deadline.timetuple())

        if timestamp > current_timestamp:
            self.put(name, int(timestamp))

    def test_hold(self, name, timeframe):
        pass

    def release(self, name):
        if self.has(name):
            self.delete(name)

    def test_release(self, name):
        pass


class HoldingHelper(dict):
    def __init__(self, storage):
        self.__bucket = storage.bucket(
            type(self).__module__
        )

    def __getitem__(self, key):
        timestamp = self.__bucket.get(key)
        if timestamp is None:
            return False

        current_timestamp = time.mktime(
            datetime.datetime.utcnow().timetuple()
        )

        if current_timestamp >= timestamp:
            self.__bucket.delete(key)
            return False

        return True
