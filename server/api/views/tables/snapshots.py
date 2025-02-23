import dataclasses
import datetime

from django.http import JsonResponse

from api.helpers import aget_object_or_404_json, Dispatcher
from api.helpers.model_converters import (
    ModelToDataclassConverter,
    ModelToDictConverter,
)
from api.views.api_view import api_view
from investment_tables.models import TableSnapshot, TableTemplate
from portfolio.models import Portfolio


@dataclasses.dataclass
class TableTemplateSchema:
    id: int
    name: str
    slug: str


@dataclasses.dataclass
class TableSnapshotSchema:
    id: int
    name: str
    created_at: datetime.datetime
    template: TableTemplateSchema


@api_view(login_required=True)
async def table_snapshot_list(request):
    user_snapshots = (
        TableSnapshot.objects.select_related('template')
        .owned_by(request.user)
        .active()
    )

    converter = ModelToDictConverter(
        source=user_snapshots,
        schema=TableSnapshotSchema,
        many=True,
        fields_map={
            'template': ModelToDataclassConverter(
                schema=TableTemplateSchema,
                fields_map={
                    field: f'template__{field}'
                    for field in TableTemplateSchema.__dataclass_fields__
                },
            ),
        },
    )

    return JsonResponse({'snapshots': await converter.convert()})


@dataclasses.dataclass
class TableSnapshotCreateSchema:
    name: str | None
    portfolio_id: int
    template_id: int

    def validate_portfolio_id(self):
        if self.portfolio_id < 0:
            raise ValueError('invalid portfolio id')

    def validate_template_id(self):
        if self.portfolio_id < 0:
            raise ValueError('invalid template id')


@api_view(login_required=True, request_schema=TableSnapshotCreateSchema)
async def create_table_snapshot(request):
    request_snapshot: TableSnapshotCreateSchema = request.populated_schema
    portfolio = await aget_object_or_404_json(
        Portfolio.objects.filter(owner=request.user),
        pk=request_snapshot.portfolio_id,
    )
    template = await aget_object_or_404_json(
        TableTemplate,
        pk=request_snapshot.template_id,
    )

    table_snapshot = await TableSnapshot.objects.acreate(
        name=request_snapshot.name,
        portfolio=portfolio,
        template=template,
    )
    converter = ModelToDictConverter(
        source=table_snapshot,
        schema=TableSnapshotSchema,
        skip_fields=('template',),
    )
    return JsonResponse({'snapshot': await converter.convert()})


dispatcher = Dispatcher(get=table_snapshot_list, post=create_table_snapshot)
