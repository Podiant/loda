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

    def first(self, count, fixture_name):
        items = self.fixture(fixture_name)
        count = int(count)
        choices = items[:count]

        for choice in choices:
            yield choice
