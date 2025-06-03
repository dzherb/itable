import typing


class SecurityWeightDict(typing.TypedDict):
    ticker: str
    weight: float


class SecurityWeightDictWithId(SecurityWeightDict):
    id: typing.NotRequired[int]


class IndexSynchronizerProtocol(typing.Protocol):
    async def synchronize(self) -> None: ...


class IndexProviderProtocol(typing.Protocol):
    async def get_index_content(self) -> list[SecurityWeightDict]:
        pass
