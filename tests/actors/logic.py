from loda.acting import ActorBase


class Actor(ActorBase):
    receive = {
        'set': [r'^set (.+) = (.+)$'],
        'increment': [r'increment (.+)']
    }

    def set(self, key, value):
        self.put(key, value)

    def increment(self, key):
        value = self.get(key, 0)
        value += 1
        self.put(key, value)
