from collections.abc import Callable
import functools
import typing

from async_lru import alru_cache


class _AlwaysEquals:
    def __init__(self, original_object: typing.Any):
        self.original_object = original_object

    def __eq__(self, other):
        return True

    def __hash__(self):
        return 0


def alru_method_shared_cache(*args, **kwargs):
    """
    Wrapper for alru_cache that ignores "self" method argument.
    This way we can share cache between instances.
    """

    def decorator(fn: Callable):
        @alru_cache(*args, **kwargs)
        async def helper(dummy_arg: _AlwaysEquals, *args, **kwargs):
            return await fn(dummy_arg.original_object, *args, **kwargs)

        @functools.wraps(fn)
        async def method(self, *args, **kwargs):
            return await helper(_AlwaysEquals(self), *args, **kwargs)

        return method

    return decorator
