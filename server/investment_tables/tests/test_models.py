from django.db import IntegrityError
from django.test import TestCase

import exchange.models
import investment_tables.models


class TableTemplateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.stock1 = exchange.models.Security.objects.create(ticker='A')
        cls.stock2 = exchange.models.Security.objects.create(ticker='B')
        cls.table_template = (
            investment_tables.models.TableTemplate.objects.create(
                name='test table',
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

        with self.assertRaises(IntegrityError):
            await self.table_template.securities.aadd(
                self.stock2,
                through_defaults={'weight': -1},
            )
