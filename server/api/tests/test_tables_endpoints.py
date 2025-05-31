from http import HTTPStatus
import json

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse
from parameterized import parameterized

from api.tests.helpers import generate_auth_header
from apps.exchange.models import Security
from apps.investment_tables.models import (
    TableSnapshot,
    TableSnapshotItem,
    TableTemplate,
)
from apps.portfolios.models import Portfolio
from utils.db_helpers import AsyncAtomic

User = get_user_model()


class SnapshotsFixtureMixin:
    def setUp(self):
        self.client = AsyncClient()
        self.credentials = generate_auth_header(self.user)

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email='test_user@test.com',
            password='password',
        )
        cls.another_user = User.objects.create_user(
            email='another_test_user@test.com',
            password='password',
        )

        cls.portfolio = Portfolio.objects.create(
            name='test portfolio',
            owner=cls.user,
        )
        cls.another_user_portfolio = Portfolio.objects.create(
            name='another user test portfolio',
            owner=cls.another_user,
        )

        securities = [
            Security(ticker='TSLA'),
            Security(ticker='AAPL'),
            Security(ticker='SBER'),
            Security(ticker='T'),
            Security(ticker='YDEX'),
        ]
        Security.objects.bulk_create(securities)

        cls.template = TableTemplate.objects.create(
            name='super profitable index',
            slug='spindx',
        )

        cls.template.securities.add(
            *Security.objects.all(),
            through_defaults={'weight': 1 / 5 * 100},
        )

        snapshot_from_template = async_to_sync(TableSnapshot.from_template)
        cls.first_snapshot: TableSnapshot = snapshot_from_template(
            template=cls.template,
            portfolio=cls.portfolio,
            name='first snapshot',
        )
        cls.second_snapshot: TableSnapshot = snapshot_from_template(
            template=cls.template,
            portfolio=cls.portfolio,
            name='second snapshot',
        )

        snapshot_item: TableSnapshotItem = cls.first_snapshot.items.get(
            template_item__security__ticker='TSLA',
        )
        snapshot_item.coefficient = 2
        snapshot_item.save(update_fields=['coefficient'])


class TableSnapshotListTestCase(SnapshotsFixtureMixin, TestCase):
    async def test_user_can_get_table_snapshot_list(self):
        response = await self.client.get(
            reverse('api:table_snapshots'),
            headers=self.credentials,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        snapshots = json.loads(response.content)['snapshots']
        self.assertEqual(len(snapshots), 2)
        self.assertEqual(snapshots[0]['name'], 'first snapshot')
        self.assertEqual(
            snapshots[0]['template'],
            {
                'id': self.template.id,
                'name': 'super profitable index',
                'slug': 'spindx',
            },
        )

    async def test_user_can_get_only_own_snapshots(self):
        await TableSnapshot.from_template(
            template=self.template,
            portfolio=self.another_user_portfolio,
            name='another user snapshot',
        )
        response = await self.client.get(
            reverse('api:table_snapshots'),
            headers=self.credentials,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        snapshots = json.loads(response.content)['snapshots']

        self.assertEqual(len(snapshots), 2)

        for snapshot in snapshots:
            self.assertNotEqual(snapshot['name'], 'another user snapshot')

    async def test_anonymous_user_cannot_get_snapshot_list(self):
        response = await self.client.get(reverse('api:table_snapshots'))
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    async def test_user_can_get_only_active_snapshots(self):
        self.first_snapshot.is_active = False
        await self.first_snapshot.asave(update_fields=['is_active'])

        response = await self.client.get(
            reverse('api:table_snapshots'),
            headers=self.credentials,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        snapshots = json.loads(response.content)['snapshots']
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0]['name'], 'second snapshot')


class TestSnapshotCreationTestCase(SnapshotsFixtureMixin, TestCase):
    def setUp(self):
        super().setUp()

        self.create_data = {
            'name': 'my third snapshot',
            'portfolio_id': self.portfolio.id,
            'template_id': self.template.id,
        }

    async def test_user_can_create_snapshot(self):
        response = await self.client.post(
            reverse('api:table_snapshots'),
            data=self.create_data,
            content_type='application/json',
            headers=self.credentials,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        snapshot = json.loads(response.content)['snapshot']
        last_snapshot = await self.portfolio.table_snapshots.alast()
        self.assertEqual(last_snapshot.name, 'my third snapshot')
        self.assertEqual(snapshot['name'], 'my third snapshot')

    async def test_user_can_create_snapshot_without_name(self):
        del self.create_data['name']
        response = await self.client.post(
            reverse('api:table_snapshots'),
            self.create_data,
            content_type='application/json',
            headers=self.credentials,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        snapshot = json.loads(response.content)['snapshot']
        last_snapshot = await self.portfolio.table_snapshots.alast()
        self.assertEqual(last_snapshot.name, self.template.name)
        self.assertEqual(snapshot['name'], self.template.name)

    async def test_anonymous_user_cannot_create_snapshot(self):
        response = await self.client.post(
            reverse('api:table_snapshots'),
            data=self.create_data,
            content_type='application/json',
        )
        self.assertEqual(response.status_code, HTTPStatus.UNAUTHORIZED)

    @parameterized.expand(
        [
            ('portfolio_id', 'portfolio not found'),
            ('template_id', 'table template not found'),
        ],
    )
    async def test_user_cannot_create_snapshot_with_nonexistent_entities(
        self,
        field,
        error_message,
    ):
        response = await self.client.post(
            reverse('api:table_snapshots'),
            data=self.create_data | {field: 999},  # send incorrect id
            content_type='application/json',
            headers=self.credentials,
        )
        content = json.loads(response.content)

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(content['error'], error_message)
        self.assertEqual(await TableSnapshot.objects.acount(), 2)

    async def test_user_cannot_create_snapshot_with_invalid_data(self):
        cases = (
            {
                'name': 1,
                'portfolio_id': self.portfolio.id,
                'template_id': self.template.id,
            },
            {
                'name': '',
                'portfolio_id': self.portfolio.id,
                'template_id': self.template.id,
            },
            {
                'name': 'new snapshot',
                'portfolio_id': -10,
                'template_id': self.template.id,
            },
            {
                'name': 'new snapshot',
                'portfolio_id': 'wrong_type',
                'template_id': self.template.id,
            },
            {
                'name': 'new snapshot',
                'portfolio_id': self.portfolio.id,
                'template_id': -33,
            },
            {'name': 'new snapshot', 'portfolio_id': self.portfolio.id},
        )

        for case in cases:
            with self.subTest(case=case):
                async with AsyncAtomic():
                    response = await self.client.post(
                        reverse('api:table_snapshots'),
                        data=case,
                        content_type='application/json',
                        headers=self.credentials,
                    )
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.BAD_REQUEST,
                    )
                    self.assertEqual(await TableSnapshot.objects.acount(), 2)
