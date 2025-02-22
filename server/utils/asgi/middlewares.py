import traceback


class LifespanMiddleware:
    def __init__(self, app, *, lifespan):
        self.app = app
        self.lifespan = lifespan

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'lifespan':
            await self.handle_lifespan(scope, receive, send)
            return

        await self.app(scope, receive, send)

    async def handle_lifespan(self, scope, receive, send):
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
            event_type = (
                'lifespan.shutdown.failed'
                if started
                else 'lifespan.startup.failed'
            )
            await send({'type': event_type, 'message': traceback.format_exc()})
            raise
        await send({'type': 'lifespan.shutdown.complete'})
