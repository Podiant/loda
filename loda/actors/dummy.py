from loda.acting import ActorBase
import sys


class Actor(ActorBase):  # pragma: no cover
    receive = ['(.*)']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def perform(self, *args):
        sys.stdout.write(
            '%s\n' % ', '.join(
                str(a) for a in args
            )
        )
