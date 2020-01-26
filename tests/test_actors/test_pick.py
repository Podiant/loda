from loda.actors.builtin.pick import Actor
from loda.storage.engines.locmem import LocalMemoryEngine


def test_first():
    engine = LocalMemoryEngine()
    actor = Actor(
        engine,
        {
            'list': [1, 2, 3]
        },
        {}
    )

    args, func = actor.match('pick 2 from list')
    result = list(func(*args))
    count = sum(result)
    assert count == 3


def test_random():
    engine = LocalMemoryEngine()
    actor = Actor(
        engine,
        {
            'list': [1, 2, 3]
        },
        {}
    )

    args, func = actor.match('pick 3 from list at random')
    result = list(func(*args))
    count = sum(result)
    assert count == 6
