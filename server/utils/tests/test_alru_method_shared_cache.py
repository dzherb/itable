from django.test import TestCase

from utils.cache import alru_method_shared_cache


class MethodSharedCacheTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.real_calls_count = 0

        class DummyClass:
            @alru_method_shared_cache()
            async def simple_method(self, arg: int | None = None):
                cls.real_calls_count += 1

        cls.dummy_class = DummyClass

    async def test_cache_is_shared(self):
        first_instance = self.dummy_class()
        second_instance = self.dummy_class()

        await first_instance.simple_method()
        self.assertEqual(self.real_calls_count, 1)

        await second_instance.simple_method()
        self.assertEqual(self.real_calls_count, 1)

        await first_instance.simple_method(arg=1)
        self.assertEqual(self.real_calls_count, 2)

        await second_instance.simple_method(arg=1)
        self.assertEqual(self.real_calls_count, 2)
