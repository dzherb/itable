from asgiref.sync import async_to_sync

from users.authentication.jwt import TokenPair
from users.models import ItableUser


def generate_auth_header(user: ItableUser) -> dict[str, str]:
    token_pair: TokenPair = async_to_sync(user.generate_new_tokens)()
    return {
        'Authorization': f'Bearer {token_pair.access_token}',
    }


async def agenerate_auth_header(user: ItableUser) -> dict[str, str]:
    token_pair: TokenPair = await user.generate_new_tokens()
    return {
        'Authorization': f'Bearer {token_pair.access_token}',
    }
