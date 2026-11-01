"""Pricing steps register themselves here and run in ascending ``order``.

    @step(order=20)
    def promotions(ctx): ...
"""

_STEPS = []


def step(order):
    def register(fn):
        _STEPS.append((order, fn))
        return fn
    return register


def steps():
    return [fn for _, fn in sorted(_STEPS, key=lambda item: item[0])]
