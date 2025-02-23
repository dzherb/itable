import copy
from http import HTTPStatus
import json

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.test import AsyncClient, TestCase
from django.urls import reverse

from exchange.models import Security
from investment_tables.models import (
    TableSnapshot,
    TableSnapshotItem,
    TableTemplate,
)
from portfolio.models import Portfolio

User = get_user_model()


class SnapshotsFixtureMixin:
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='test_user',
            password='password',
        )
        cls.another_user = User.objects.create_user(
            username='another_test_user',
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
    def setUp(self):
        self.client = AsyncClient()

    async def test_user_can_get_table_snapshot_list(self):
        await self.client.aforce_login(self.user)
        response = await self.client.get(reverse('api:table_snapshots'))

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
        await self.client.aforce_login(self.user)
        response = await self.client.get(reverse('api:table_snapshots'))
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

        await self.client.aforce_login(self.user)
        response = await self.client.get(reverse('api:table_snapshots'))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        snapshots = json.loads(response.content)['snapshots']
        self.assertEqual(len(snapshots), 1)
        self.assertEqual(snapshots[0]['name'], 'second snapshot')


class TestSnapshotCreationTestCase(SnapshotsFixtureMixin, TestCase):
    def setUp(self):
        self.client = AsyncClient()
        self.create_data = {
            'name': 'my third snapshot',
            'portfolio_id': self.portfolio.id,
            'template_id': self.template.id,
        }

    async def test_user_can_create_snapshot(self):
        await self.client.aforce_login(self.user)
        response = await self.client.post(
            reverse('api:table_snapshots'),
            data=self.create_data,
            content_type='application/json',
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        snapshot = json.loads(response.content)['snapshot']
        last_snapshot = await self.portfolio.table_snapshots.alast()
        self.assertEqual(last_snapshot.name, 'my third snapshot')
        self.assertEqual(snapshot['name'], 'my third snapshot')

    async def test_user_can_create_snapshot_without_name(self):
        await self.client.aforce_login(self.user)
        del self.create_data['name']
        response = await self.client.post(
            reverse('api:table_snapshots'),
            self.create_data,
            content_type='application/json',
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

    async def test_user_cannot_create_snapshot_with_nonexistent_entities(self):
        await self.client.aforce_login(self.user)

        cases = (
            ('portfolio_id', 'portfolio not found'),
            ('template_id', 'table template not found'),
        )
        for field, error_message in cases:
            with self.subTest(field=field):
                wrong_data = copy.deepcopy(self.create_data)
                wrong_data[field] = 999
                response = await self.client.post(
                    reverse('api:table_snapshots'),
                    data=wrong_data,
                    content_type='application/json',
                )
                content = json.loads(response.content)

                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertEqual(content['error'], error_message)
                self.assertEqual(await TableSnapshot.objects.acount(), 2)

    async def test_user_cannot_create_snapshot_with_invalid_data(self):
        await self.client.aforce_login(self.user)

        cases = (
            {
                'name': 1,
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
            {'name': 'new snapshot', 'portfolio_id': self.portfolio.id},
        )

        for case in cases:
            with self.subTest(case=case):
                response = await self.client.post(
                    reverse('api:table_snapshots'),
                    data=case,
                    content_type='application/json',
                )
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
                self.assertEqual(await TableSnapshot.objects.acount(), 2)
