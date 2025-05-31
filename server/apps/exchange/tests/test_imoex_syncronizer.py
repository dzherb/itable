from django.test import TestCase

from apps import investment_tables
from apps.exchange.services.synchronization.imoex_synchronizer import (
    IMOEXSynchronizer,
)
from apps.exchange.services.synchronization.index_providers import (
    IndexProviderProtocol,
    SecurityWeightDict,
)


class MockIMOEXProvider(IndexProviderProtocol):
    async def get_index_content(self) -> list[SecurityWeightDict]:
        return [
            {
                'ticker': 'A',
                'weight': 14.0,
            },
            {
                'ticker': 'B',
                'weight': 32.5,
            },
            {
                'ticker': 'C',
                'weight': 22.5,
            },
            {
                'ticker': 'D',
                'weight': 5.0,
            },
            {
                'ticker': 'E',
                'weight': 26.0,
            },
        ]


class MockIMOEXLessSecuritiesProvider(IndexProviderProtocol):
    async def get_index_content(self) -> list[SecurityWeightDict]:
        return [
            {
                'ticker': 'A',
                'weight': 14.0,
            },
            {
                'ticker': 'B',
                'weight': 32.5,
            },
            {
                'ticker': 'C',
                'weight': 22.5,
            },
        ]


class MockIMOEXDifferentWeightsProvider(IndexProviderProtocol):
    async def get_index_content(self) -> list[SecurityWeightDict]:
        return [
            {
                'ticker': 'A',
                'weight': 13.5,
            },
            {
                'ticker': 'B',
                'weight': 31.3,
            },
            {
                'ticker': 'C',
                'weight': 23.7,
            },
            {
                'ticker': 'D',
                'weight': 6.5,
            },
            {
                'ticker': 'E',
                'weight': 25.0,
            },
        ]


class IMOEXSynchronizerTestCase(TestCase):
    async def test_synchronization_initial_run(self):
        synchronizer = IMOEXSynchronizer(provider=MockIMOEXProvider())
        await synchronizer.synchronize()

        template = await self._get_imoex_template()

        self.assertEqual(await template.items.active().acount(), 5)

        template_item = await template.items.filter(
            security__ticker='C',
        ).aget()
        self.assertEqual(template_item.weight, 22.5)

    async def test_synchronization_can_run_multiple_times(self):
        synchronizer = IMOEXSynchronizer(provider=MockIMOEXProvider())
        await synchronizer.synchronize()
        await synchronizer.synchronize()
        await synchronizer.synchronize()

        template = await self._get_imoex_template()

        self.assertEqual(await template.items.active().acount(), 5)

    async def test_synchronization_can_add_new_securities(self):
        synchronizer = IMOEXSynchronizer(
            provider=MockIMOEXLessSecuritiesProvider(),
        )
        await synchronizer.synchronize()

        template = await self._get_imoex_template()

        self.assertEqual(await template.items.active().acount(), 3)

        synchronizer = IMOEXSynchronizer(provider=MockIMOEXProvider())
        await synchronizer.synchronize()
        await template.arefresh_from_db()

        self.assertEqual(await template.items.active().acount(), 5)

    async def test_synchronization_updates_weights(self):
        synchronizer = IMOEXSynchronizer(provider=MockIMOEXProvider())
        await synchronizer.synchronize()

        template = await self._get_imoex_template()
        template_item: investment_tables.models.TableTemplateItem = (
            await template.items.filter(security__ticker='C').aget()
        )
        self.assertEqual(template_item.weight, 22.5)

        synchronizer = IMOEXSynchronizer(
            provider=MockIMOEXDifferentWeightsProvider(),
        )
        await synchronizer.synchronize()
        await template_item.arefresh_from_db()

        self.assertEqual(template_item.weight, 23.7)

    async def test_synchronization_can_remove_inactive_securities(self):
        synchronizer = IMOEXSynchronizer(provider=MockIMOEXProvider())
        await synchronizer.synchronize()

        template = await self._get_imoex_template()
        self.assertEqual(await template.items.active().acount(), 5)

        synchronizer = IMOEXSynchronizer(
            provider=MockIMOEXLessSecuritiesProvider(),
        )
        await synchronizer.synchronize()

        self.assertEqual(await template.items.active().acount(), 3)
        self.assertFalse(
            await template.items.active()
            .filter(security__ticker='D')
            .aexists(),
        )

    async def test_synchronization_can_make_security_active_again(self):
        synchronizer = IMOEXSynchronizer(provider=MockIMOEXProvider())
        synchronizer_with_less_securities = IMOEXSynchronizer(
            provider=MockIMOEXLessSecuritiesProvider(),
        )
        await synchronizer.synchronize()
        await synchronizer_with_less_securities.synchronize()

        template = await self._get_imoex_template()
        self.assertFalse(
            await template.items.active()
            .filter(security__ticker='D')
            .aexists(),
        )

        await synchronizer.synchronize()
        self.assertTrue(
            await template.items.active()
            .filter(security__ticker='D')
            .aexists(),
        )

    async def _get_imoex_template(
        self,
    ) -> investment_tables.models.TableTemplate:
        return await investment_tables.models.TableTemplate.objects.aget(
            slug=IMOEXSynchronizer.IMOEX_TABLE_TEMPLATE_SLUG,
        )
