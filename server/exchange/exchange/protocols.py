import typing


class SecurityDict(typing.TypedDict):
    ticker: str
    short_name: str
    weight: float
    price: float
    lot_size: int
    last_dividend_value: typing.NotRequired[float]


class IndexAPIProtocol(typing.Protocol):
    async def get_index_content(self) -> list[SecurityDict]:
        pass
