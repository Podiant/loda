class Condition(object):
    def __init__(self, expr):
        self.expr = expr

    def met(self, context):
        compiled = eval(self.expr, {}, dict(**context))
        return self._met(compiled)

    def _met(self, value):  # pragma: no cover
        raise NotImplementedError('Method not implemented')


class PositiveCondition(Condition):
    def _met(self, value):
        return not not value


class NegativeCondition(Condition):
    def _met(self, value):
        return not value
