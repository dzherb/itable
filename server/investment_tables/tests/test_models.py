from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase

import exchange.models
import investment_tables.models
import portfolio.models
from utils.db_helpers import AsyncAtomic


class TableTemplateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stock1 = exchange.models.Security.objects.create(ticker='A')
        cls.stock2 = exchange.models.Security.objects.create(ticker='B')
        cls.table_template = (
            investment_tables.models.TableTemplate.objects.create(
                name='test table',
                slug='test-table',
            )
        )

    async def test_can_add_securities_to_template(self):
        await self.table_template.securities.aadd(
            self.stock1,
            through_defaults={'weight': 35},
        )
        await self.table_template.securities.aadd(
            self.stock2,
            through_defaults={'weight': 32},
        )

        self.assertEqual(await self.table_template.securities.acount(), 2)
        self.assertEqual((await self.table_template.items.afirst()).weight, 35)
        self.assertEqual((await self.table_template.items.alast()).weight, 32)

    async def test_cant_add_same_security_twice(self):
        await self.table_template.securities.aadd(
            self.stock1,
            through_defaults={'weight': 1},
        )

        await self.table_template.securities.aadd(
            self.stock1,
            through_defaults={'weight': 2},
        )

        self.assertEqual(await self.table_template.securities.acount(), 1)
        self.assertEqual((await self.table_template.items.afirst()).weight, 1)

    async def test_cant_exceed_weight_limit(self):
        await self.table_template.securities.aadd(
            self.stock1,
            through_defaults={'weight': 100},
        )

        with self.assertRaises(IntegrityError):
            await self.table_template.securities.aadd(
                self.stock2,
                through_defaults={'weight': 101},
            )

    async def test_cant_set_negative_weight(self):
        await self.table_template.securities.aadd(
            self.stock1,
            through_defaults={'weight': 0},
        )

        async with AsyncAtomic():
            with self.assertRaises(IntegrityError):
                await self.table_template.securities.aadd(
                    self.stock2,
                    through_defaults={'weight': -1},
                )

        self.assertEqual(await self.table_template.securities.acount(), 1)


class TableSnapshotTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stock1 = exchange.models.Security.objects.create(ticker='A')
        cls.stock2 = exchange.models.Security.objects.create(ticker='B')
        cls.table_template = (
            investment_tables.models.TableTemplate.objects.create(
                name='test table',
            )
        )
        cls.table_template.securities.add(
            cls.stock1,
            through_defaults={'weight': 35},
        )
        cls.table_template.securities.add(
            cls.stock2,
            through_defaults={'weight': 32},
        )

        cls.user = get_user_model().objects.create_user(
            email='testuser',
            password='testpswd',
        )

        cls.portfolio = portfolio.models.Portfolio.objects.create(
            name='test portfolio',
            owner=cls.user,
        )

    async def test_can_create_snapshot_from_template(self):
        snapshot = await investment_tables.models.TableSnapshot.from_template(
            template=self.table_template,
            portfolio=self.portfolio,
        )

        self.assertEqual(await snapshot.template_items.acount(), 2)
        self.assertEqual((await snapshot.template_items.alast()).weight, 32)
        self.assertEqual(
            (
                await snapshot.template_items.select_related(
                    'security',
                ).alast()
            ).security.ticker,
            'B',
        )

    async def test_default_snapshot_item_coefficient(self):
        snapshot = await investment_tables.models.TableSnapshot.from_template(
            template=self.table_template,
            portfolio=self.portfolio,
        )

        snapshot_item: investment_tables.models.TableSnapshotItem = (
            await snapshot.items.aget(template_item__security__ticker='A')
        )
        self.assertEqual(snapshot_item.coefficient, 1)

    async def test_snapshot_item_coefficient_constraint(self):
        snapshot = await investment_tables.models.TableSnapshot.from_template(
            template=self.table_template,
            portfolio=self.portfolio,
        )

        snapshot_item: investment_tables.models.TableSnapshotItem = (
            await snapshot.items.aget(template_item__security__ticker='A')
        )
        snapshot_item.coefficient = -1

        async with AsyncAtomic():
            with self.assertRaises(IntegrityError):
                await snapshot_item.asave()

        await snapshot_item.arefresh_from_db()
        self.assertEqual(snapshot_item.coefficient, 1)

        snapshot_item.coefficient = 0
        await snapshot_item.asave()

        await snapshot_item.arefresh_from_db()
        self.assertEqual(snapshot_item.coefficient, 0)

    async def test_snapshot_default_name_comes_from_template(self):
        snapshot = await investment_tables.models.TableSnapshot.from_template(
            template=self.table_template,
            portfolio=self.portfolio,
        )

        self.assertEqual(snapshot.name, self.table_template.name)

    async def test_can_create_snapshot_with_custom_name(self):
        snapshot = await investment_tables.models.TableSnapshot.from_template(
            template=self.table_template,
            portfolio=self.portfolio,
            name='custom snapshot name',
        )

        self.assertEqual(snapshot.name, 'custom snapshot name')
