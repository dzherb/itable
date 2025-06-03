from contextlib import asynccontextmanager

from asgi_lifespan import LifespanManager
from django.test import TestCase

from utils.asgi.middlewares import LifespanMiddleware


async def dummy_asgi_app(scope, receive, send):
    pass


class DummyLifespan:
    def __init__(self):
        self.entered = False
        self.exited = False

    def __call__(self):
        return self

    async def __aenter__(self):
        self.entered = True

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exited = True


class LifespanMiddlewareTestCase(TestCase):
    async def test_lifespan_middleware_cycle(self):
        lifespan = DummyLifespan()
        app = LifespanMiddleware(dummy_asgi_app, lifespan=lifespan)

        self.assertEqual(lifespan.entered, False)
        self.assertEqual(lifespan.exited, False)

        async with LifespanManager(app):
            self.assertEqual(lifespan.entered, True)
            self.assertEqual(lifespan.exited, False)

        self.assertEqual(lifespan.exited, True)

    async def test_lifespan_middleware_state(self):
        @asynccontextmanager
        async def lifespan():
            yield {'answer': 42}

        app = LifespanMiddleware(dummy_asgi_app, lifespan=lifespan)
        async with LifespanManager(app) as manager:
            self.assertEqual(manager._state['answer'], 42)
