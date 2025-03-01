import dataclasses
import datetime

from django.http import JsonResponse

from api.helpers import aget_object_or_404_json
from api.helpers.dispatcher import create_dispatcher
from api.helpers.model_converters import (
    ModelToDataclassConverter,
    ModelToDictConverter,
)
from api.helpers.schema_mixins import (
    ValidateIdFieldsMixin,
    ValidateNameSchemaMixin,
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
class TableSnapshotCreateSchema(
    ValidateNameSchemaMixin,
    ValidateIdFieldsMixin,
):
    name: str | None
    portfolio_id: int
    template_id: int


@api_view(login_required=True, request_schema=TableSnapshotCreateSchema)
async def create_table_snapshot(request):
    table_snapshot_schema: TableSnapshotCreateSchema = request.populated_schema
    portfolio = await aget_object_or_404_json(
        Portfolio.objects.filter(owner=request.user),
        pk=table_snapshot_schema.portfolio_id,
    )
    template = await aget_object_or_404_json(
        TableTemplate,
        pk=table_snapshot_schema.template_id,
    )

    table_snapshot = await TableSnapshot.from_template(
        portfolio=portfolio,
        template=template,
        name=table_snapshot_schema.name,
    )
    converter = ModelToDictConverter(
        source=table_snapshot,
        schema=TableSnapshotSchema,
        skip_fields=('template',),
    )
    return JsonResponse({'snapshot': await converter.convert()})


dispatcher = create_dispatcher(
    get=table_snapshot_list,
    post=create_table_snapshot,
)
