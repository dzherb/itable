from typing import override

from django.http import HttpRequest

from api.helpers.aget_object_or_404_json import aget_object_or_404_json
from api.permissions.permission_protocol import Permission
from portfolio.models import Portfolio


class IsPortfolioOwner(Permission):
    def __init__(self, argument_name='pk'):
        self.argument_name = argument_name

    @override
    async def has_permission(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> bool:
        # We don't want other users to know
        # about not theirs portfolios.
        # That's why we return 404 on check fail.
        await aget_object_or_404_json(
            Portfolio.objects.active().only(),
            pk=kwargs[self.argument_name],
            owner=request.user.id,
        )

        return True
