from loda.acting import ActorBase


class Actor(ActorBase):
    receive = {
        'save': ['save value'],
        'fixture_': ['get fixture'],
        'error': ['raise exception']
    }

    def save(self):
        self.untag('foo')
        self.put('faulty', True)

    def fixture_(self):
        return self.fixture('foo')

    def error(self):
        raise Exception('Foo')
