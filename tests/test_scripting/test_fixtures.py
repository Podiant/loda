from loda.scripting.fixtures import Fixture
import os


def test_load_again():
    fixture = Fixture(
        os.path.join(
            os.path.dirname(
                os.path.dirname(
                    __file__
                )
            ),
            'fixtures',
            'test_simple.yaml'
        )
    )

    assert fixture.read()['foo'] == 'bar'
    assert fixture.read()['foo'] == 'bar'
