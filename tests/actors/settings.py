from loda.acting import ActorBase


class Actor(ActorBase):
    receive = {
        'set': [r'^set (.+) from (.+)$']
    }

    def set(self, key, setting_name):
        setting = getattr(self.settings, setting_name)
        self.put(key, setting)
