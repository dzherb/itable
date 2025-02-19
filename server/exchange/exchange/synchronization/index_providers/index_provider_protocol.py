import typing


class SecurityWeightDict(typing.TypedDict):
    ticker: str
    weight: float


class IndexProviderProtocol(typing.Protocol):
    async def get_index_content(self) -> list[SecurityWeightDict]:
        pass
