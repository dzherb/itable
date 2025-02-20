from typing import override

from django.http import HttpRequest

from api import exceptions
from api.helpers.aget_object_or_404_json import aget_object_or_404_json
from api.permissions.permission_protocol import Permission
from portfolio.models import Portfolio


class IsPortfolioOwner(Permission):
    @override
    async def has_permission(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> bool:
        portfolio = await aget_object_or_404_json(
            Portfolio.objects.only('owner_id'),
            pk=kwargs['pk'],
        )
        if portfolio.owner_id != request.user.id:
            # We don't want other users to know
            # about not theirs portfolios.
            raise exceptions.NotFoundError

        return True
