from loda.scripting.logic import PositiveCondition, NegativeCondition


def test_positive_condition_met():
    condition = PositiveCondition('foo')
    assert condition.met({'foo': True}) is True


def test_positive_condition_unmet():
    condition = PositiveCondition('foo')
    assert condition.met({'foo': False}) is False


def test_positive_condition_ambiguous():
    condition = PositiveCondition('foo')
    assert condition.met({'foo': 1}) is True


def test_negative_condition_met():
    condition = NegativeCondition('foo')
    assert condition.met({'foo': True}) is False


def test_negative_condition_unmet():
    condition = NegativeCondition('foo')
    assert condition.met({'foo': False}) is True


def test_negative_condition_ambiguous():
    condition = NegativeCondition('foo')
    assert condition.met({'foo': 1}) is False
