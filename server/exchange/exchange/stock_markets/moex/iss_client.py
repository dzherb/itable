import typing

import aiohttp
import aiomoex


class ISSClient(typing.Protocol):
    async def get(self) -> aiomoex.TablesDict:
        pass


class ISSClientFactory(typing.Protocol):
    def get_client(
        self,
        session: aiohttp.ClientSession,
        resource: str,
        arguments: aiomoex.client.WebQuery | None = None,
    ) -> ISSClient:
        pass


class ISSClientFactoryImpl(ISSClientFactory):
    BASE_URL = 'https://iss.moex.com/iss'

    def get_client(
        self,
        session: aiohttp.ClientSession,
        resource: str,
        arguments: aiomoex.client.WebQuery | None = None,
    ) -> ISSClient:
        return aiomoex.ISSClient(
            session,
            self.BASE_URL + resource,
            arguments,
        )
