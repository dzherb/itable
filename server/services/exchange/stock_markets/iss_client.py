import typing
from typing import override

import aiohttp
import aiomoex

type WebQuery = aiomoex.client.WebQuery
type TablesDict = aiomoex.TablesDict


class ISSClient(typing.Protocol):
    async def get(self) -> TablesDict:
        pass


class ISSClientFactory(typing.Protocol):
    def get_client(
        self,
        session: aiohttp.ClientSession,
        resource: str,
        arguments: WebQuery | None = None,
    ) -> ISSClient:
        pass


class ISSClientFactoryImpl(ISSClientFactory):
    BASE_URL = 'https://iss.moex.com/iss'

    @override
    def get_client(
        self,
        session: aiohttp.ClientSession,
        resource: str,
        arguments: WebQuery | None = None,
    ) -> ISSClient:
        return aiomoex.ISSClient(
            session,
            self.BASE_URL + resource,
            arguments,
        )
