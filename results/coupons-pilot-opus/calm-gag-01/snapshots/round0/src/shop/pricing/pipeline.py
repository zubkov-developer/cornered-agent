"""Runs the registered pricing steps over a cart."""

from . import steps as _steps  # noqa: F401  (importing registers the steps)
from .context import Context
from .registry import steps


def run(cart):
    ctx = Context(cart)
    for fn in steps():
        fn(ctx)
    return ctx
