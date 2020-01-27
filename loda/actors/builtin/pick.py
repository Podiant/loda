from ...acting import ActorBase
from random import sample as random_sample


class Actor(ActorBase):
    receive = {
        'random': [
            r'^pick.* (\d).* from ([\w]+) at random$'
        ],
        'first': [
            r'^pick.* (\d).* from ([\w]+)$'
        ]
    }

    def random(self, count, fixture_name):
        items = self.fixture(fixture_name)
        count = int(count)
        choices = random_sample(items, count)

        for choice in choices:
            yield choice

    def test_random(self, count, fixture_name):
        return self.random(count, fixture_name)

    def first(self, count, fixture_name):
        items = self.fixture(fixture_name)
        count = int(count)
        choices = items[:count]

        for choice in choices:
            yield choice

    def test_first(self, count, fixture_name):
        return self.first(count, fixture_name)
