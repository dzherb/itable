import dataclasses
import datetime
from http import HTTPStatus
import json

from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.test import RequestFactory, TestCase
from django.utils import timezone
from parameterized import parameterized

from api.helpers import Dispatcher
from api.helpers.api_view import api_view
from api.helpers.model_converters import (
    ModelToDataclassConverter,
)
from api.helpers.schema_mixins import ValidateIdFieldsMixin
from api.helpers.strings import undo_camel_case
from exchange.models import Security
from portfolio.models import Portfolio, PortfolioItem

User = get_user_model()


@api_view
async def _get_handler(request):
    return JsonResponse({'method': 'GET'})


@api_view
async def _post_handler(request):
    return JsonResponse({'method': 'POST'})


@api_view
async def _delete_handler(request):
    return JsonResponse({'method': 'DELETE'})


class DispatcherTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.factory = RequestFactory()

    def _assertMethodInResponse(self, response, method):  # noqa N802
        content = json.loads(response.content)
        self.assertEqual(content['method'], method)

    async def test_dispatcher_handles_different_methods(self):
        dispatcher = Dispatcher(
            get=_get_handler,
            post=_post_handler,
            delete=_delete_handler,
        )
        dispatcher_view = dispatcher.as_view()

        request = self.factory.get('/handler')
        response = await dispatcher_view(request)
        self._assertMethodInResponse(response, 'GET')

        request = self.factory.post('/handler')
        response = await dispatcher_view(request)
        self._assertMethodInResponse(response, 'POST')

        request = self.factory.delete('/handler')
        response = await dispatcher_view(request)
        self._assertMethodInResponse(response, 'DELETE')

    async def test_dispatcher_returns_method_not_allowed(self):
        dispatcher = Dispatcher(get=_get_handler)
        dispatcher_view = dispatcher.as_view()

        request = self.factory.post('/handler')
        response = await dispatcher_view(request)
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


class ModelToDataclassConverterTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.security = Security.objects.create(ticker='AAPL')

    async def test_model_to_dataclass_full_convertion(self):
        @dataclasses.dataclass
        class Schema:
            id: int
            ticker: str
            created_at: datetime.datetime
            updated_at: datetime.datetime

        converter = ModelToDataclassConverter(
            source=self.security,
            schema=Schema,
        )
        dataclass_instance: Schema = await converter.convert()

        self.assertEqual(dataclass_instance.id, self.security.id)
        self.assertEqual(dataclass_instance.ticker, 'AAPL')
        self.assertIsInstance(dataclass_instance.created_at, datetime.datetime)
        self.assertIsInstance(dataclass_instance.updated_at, datetime.datetime)

    async def test_model_to_dataclass_partial_conversion(self):
        @dataclasses.dataclass
        class Schema:
            ticker: str

        converter = ModelToDataclassConverter(
            source=self.security,
            schema=Schema,
        )
        dataclass_instance: Schema = await converter.convert()

        self.assertFalse(hasattr(dataclass_instance, 'id'))
        self.assertFalse(hasattr(dataclass_instance, 'created_at'))
        self.assertFalse(hasattr(dataclass_instance, 'updated_at'))
        self.assertEqual(dataclass_instance.ticker, 'AAPL')

    async def test_model_to_dataclass_impossible_conversion(self):
        @dataclasses.dataclass
        class Schema:
            id: int
            nonexistent_field: str

        converter = ModelToDataclassConverter(
            source=self.security,
            schema=Schema,
        )

        with self.assertRaises(AttributeError):
            await converter.convert()

    async def test_model_to_dataclass_invalid_type_conversion(self):
        @dataclasses.dataclass
        class Schema:
            id: str
            ticker: str

        converter = ModelToDataclassConverter(
            source=self.security,
            schema=Schema,
        )

        with self.assertRaises(TypeError):
            await converter.convert()

    async def test_model_to_dataclass_mapping_fields_conversion(self):
        @dataclasses.dataclass
        class Schema:
            id: int
            name: str
            created: datetime.datetime

        converter = ModelToDataclassConverter(
            source=self.security,
            schema=Schema,
            fields_map={
                'name': 'ticker',
                'created': 'created_at',
            },
        )
        dataclass_instance: Schema = await converter.convert()
        self.assertEqual(dataclass_instance.id, 1)
        self.assertEqual(dataclass_instance.name, 'AAPL')
        self.assertIsInstance(dataclass_instance.created, datetime.datetime)

    async def test_model_to_dataclass_complex_field_lookups_conversion(self):
        @dataclasses.dataclass
        class Schema:
            ticker: str
            quantity: int
            portfolio_name: str
            owner_email: str

        user = await sync_to_async(User.objects.create_user)(
            email='test_user',
            password='password',
        )
        portfolio = await Portfolio.objects.acreate(
            name='Test Portfolio',
            owner=user,
        )
        await portfolio.securities.aadd(
            self.security,
            through_defaults={'quantity': 5},
        )

        converter = ModelToDataclassConverter(
            source=await PortfolioItem.objects.select_related(
                'security',
                'portfolio',
                'portfolio__owner',
            ).afirst(),
            schema=Schema,
            fields_map={
                'ticker': 'security__ticker',
                'quantity': 'quantity',
                'portfolio_name': 'portfolio__name',
                'owner_email': 'portfolio__owner__email',
            },
        )
        dataclass_instance: Schema = await converter.convert()
        self.assertEqual(dataclass_instance.ticker, 'AAPL')
        self.assertEqual(dataclass_instance.quantity, 5)
        self.assertEqual(dataclass_instance.portfolio_name, 'Test Portfolio')
        self.assertEqual(dataclass_instance.owner_email, 'test_user')

    async def test_model_to_dataclass_handles_optional_fields(self):
        @dataclasses.dataclass
        class Schema:
            id: int
            name: str | None

        class ModelMock:
            def __init__(self):
                self.id = 1
                self.name = None

        converter = ModelToDataclassConverter(
            source=ModelMock(),
            schema=Schema,
        )
        dataclass_instance = await converter.convert()
        self.assertEqual(dataclass_instance.id, 1)
        self.assertIsNone(dataclass_instance.name)

    async def test_model_to_dataclass_handles_union_fields(self):
        @dataclasses.dataclass
        class Schema:
            id: int
            name: str | int | dict

        class ModelMock1:
            def __init__(self):
                self.id = 1
                self.name = 'name'

        class ModelMock2:
            def __init__(self):
                self.id = 1
                self.name = 123

        class ModelMock3:
            def __init__(self):
                self.id = 1
                self.name = None

        converter = ModelToDataclassConverter(
            source=ModelMock1(),
            schema=Schema,
        )
        dataclass_instance = await converter.convert()
        self.assertEqual(dataclass_instance.name, 'name')

        converter = ModelToDataclassConverter(
            source=ModelMock2(),
            schema=Schema,
        )
        dataclass_instance = await converter.convert()
        self.assertEqual(dataclass_instance.name, 123)

        with self.assertRaises(TypeError):
            await ModelToDataclassConverter(
                source=ModelMock3(),
                schema=Schema,
            ).convert()

    async def test_model_to_dataclass_keeps_timezone(self):
        @dataclasses.dataclass
        class Schema:
            id: int
            created: datetime.datetime

        class ModelMock:
            def __init__(self):
                self.id = 1
                self.created = timezone.now()

        converter = ModelToDataclassConverter(
            source=ModelMock(),
            schema=Schema,
        )

        dataclass_instance = await converter.convert()
        self.assertTrue(timezone.is_aware(dataclass_instance.created))

    async def test_model_to_dataclass_nested_conversion(self):
        @dataclasses.dataclass
        class ChildSchema:
            id: int
            name: str

        @dataclasses.dataclass
        class ParentSchema:
            id: int
            name: str
            child: ChildSchema

        class ChildModelMock:
            def __init__(self):
                self.id = 2
                self.name = 'child name'

        class ParentModelMock:
            def __init__(self):
                self.id = 1
                self.name = 'parent name'

        converter = ModelToDataclassConverter(
            source=ParentModelMock(),
            schema=ParentSchema,
            fields_map={
                'child': ModelToDataclassConverter(
                    source=ChildModelMock(),
                    schema=ChildSchema,
                ),
            },
        )
        parent: ParentSchema = await converter.convert()
        self.assertEqual(parent.id, 1)
        self.assertEqual(parent.name, 'parent name')
        self.assertEqual(parent.child.id, 2)
        self.assertEqual(parent.child.name, 'child name')

    async def test_model_to_dataclass_many_conversion(self):
        @dataclasses.dataclass
        class SecuritySchema:
            id: int
            ticker: str

        await Security.objects.acreate(ticker='SBER')
        await Security.objects.acreate(ticker='T')

        converter = ModelToDataclassConverter(
            source=Security.objects.all(),
            schema=SecuritySchema,
            many=True,
        )
        securities = await converter.convert()

        self.assertEqual(len(securities), 3)
        self.assertEqual(securities[0].ticker, 'AAPL')
        self.assertEqual(securities[1].ticker, 'SBER')
        self.assertEqual(securities[2].ticker, 'T')

    async def test_model_to_dataclass_auto_source(self):
        user = await sync_to_async(User.objects.create_user)(
            email='test_user',
            password='password',
        )
        await Portfolio.objects.acreate(
            name='Test Portfolio 1',
            owner=user,
        )
        await Portfolio.objects.acreate(
            name='Test Portfolio 2',
            owner=user,
        )

        @dataclasses.dataclass
        class UserSchema:
            id: int
            email: str

        @dataclasses.dataclass
        class PortfolioSchema:
            id: int
            name: str
            owner: UserSchema

        converter = ModelToDataclassConverter(
            source=Portfolio.objects.select_related('owner'),
            schema=PortfolioSchema,
            fields_map={
                'owner': ModelToDataclassConverter(
                    schema=UserSchema,
                    fields_map={
                        'id': 'owner__id',
                        'email': 'owner__email',
                    },
                ),
            },
            many=True,
        )
        portfolios = await converter.convert()
        self.assertEqual(len(portfolios), 2)
        self.assertEqual(portfolios[0].name, 'Test Portfolio 1')
        self.assertEqual(portfolios[0].owner.email, 'test_user')

    async def test_model_to_dataclass_auto_source_fail(self):
        @dataclasses.dataclass
        class Schema:
            id: int
            name: str

        converter = ModelToDataclassConverter(schema=Schema)

        with self.assertRaises(AttributeError):
            await converter.convert()


class StringsHelpersTestCase(TestCase):
    @parameterized.expand(
        [
            ('CamelCase', 'Camel Case'),
            ('moreComplexExample', 'more Complex Example'),
            ('OldHTMLFile', 'Old HTML File'),
            ('simpleBigURL', 'simple Big URL'),
            ('SQLServer', 'SQL Server'),
        ],
    )
    def test_undo_camel_case(self, input_string, expected_result):
        self.assertEqual(
            undo_camel_case(input_string),
            expected_result,
        )


class TestSchemaMixins(TestCase):
    def test_validate_id_fields_mixin(self):
        @dataclasses.dataclass
        class Schema(ValidateIdFieldsMixin):
            id: int
            parent_id: int
            name: str

        self.assertTrue(hasattr(Schema, 'validate_id'))
        self.assertTrue(hasattr(Schema, 'validate_parent_id'))
        self.assertFalse(hasattr(Schema, 'validate_name'))

        instance = Schema(1, -2, 'test')
        instance.validate_id()  # expect no error to be raised

        with self.assertRaisesMessage(
            ValueError,
            'parent_id must be greater than 0',
        ):
            instance.validate_parent_id()
