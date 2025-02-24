from collections.abc import Iterable
import typing


class SecurityDict(typing.TypedDict):
    short_name: str
    ticker: str
    price: float
    lot_size: int
    last_dividend_value: typing.NotRequired[float]


class StockMarketProtocol(typing.Protocol):
    async def get_securities(
        self,
        tickers: Iterable[str],
    ) -> list[SecurityDict]: ...
