from loda.acting import ActorBase


class Actor(ActorBase):
    receive = ['perform']
    greedy = True

    def perform(self):
        self.tag('performed')
        return True
