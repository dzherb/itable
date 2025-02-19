import typing


class IndexSynchronizerProtocol(typing.Protocol):
    async def synchronize(self):
        pass
