from loda.acting import ActorBase


class Actor(ActorBase):
    receive = ['generate']
    greedy = True

    def perform(self):
        self.tag('generating')
        self.context.pop('counter', None)
        for i in range(1, 6):
            self.context['counter'] = i
            self.put('counter', i)

            yield {
                'number': i
            }

        self.untag('generating')
