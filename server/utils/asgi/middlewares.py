from collections.abc import Callable
import contextlib
import traceback
import typing

from asgiref.typing import (
    ASGI3Application,
    ASGIReceiveCallable,
    ASGISendCallable,
    Scope,
)


class LifespanMiddleware:
    def __init__(
        self,
        app: ASGI3Application,
        *,
        lifespan: Callable[
            [],
            contextlib.AbstractAsyncContextManager[typing.Any, None],
        ],
    ) -> None:
        self.app = app
        self.lifespan = lifespan

    async def __call__(
        self,
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
    ) -> None:
        if scope['type'] == 'lifespan':
            await self.handle_lifespan(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def handle_lifespan(
        self,
        scope: Scope,
        receive: ASGIReceiveCallable,
        send: ASGISendCallable,
    ) -> None:
        assert scope['type'] == 'lifespan'
        message = await receive()
        assert message['type'] == 'lifespan.startup'
        started = False
        try:
            async with self.lifespan() as state:
                if state is not None:
                    scope['state'].update(state)
                await send({'type': 'lifespan.startup.complete'})
                started = True
                message = await receive()
                assert message['type'] == 'lifespan.shutdown'
        except BaseException:
            exc_message = traceback.format_exc()
            if started:
                await send(
                    {
                        'type': 'lifespan.shutdown.failed',
                        'message': exc_message,
                    },
                )
            else:
                await send(
                    {
                        'type': 'lifespan.startup.failed',
                        'message': exc_message,
                    },
                )
            raise
        await send({'type': 'lifespan.shutdown.complete'})
