import unittest

from pydantic import BaseModel, ValidationError

from cache.common import PickleMixin, ValueDeserializationError


class MyModel(BaseModel):
    id: int
    name: str


class DummyCache(PickleMixin):
    pass


class TestSerialization(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache()

    def test_serialize_bytes(self):
        value = b'raw-bytes'
        self.assertEqual(self.cache.serialize(value), value)

    def test_serialize_string(self):
        value = 'hello'
        self.assertEqual(self.cache.serialize(value), value)

    def test_serialize_int(self):
        value = 123
        self.assertEqual(self.cache.serialize(value), value)

    def test_serialize_float(self):
        value = 12.34
        self.assertEqual(self.cache.serialize(value), value)

    def test_serialize_dict(self):
        value = {'key': 'value', 'num': 1}
        result = self.cache.serialize(value)
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b'{"key": "value", "num": 1}')

    def test_serialize_list(self):
        value = [{'a': 1}, {'b': 2}]
        result = self.cache.serialize(value)
        self.assertIsInstance(result, bytes)
        self.assertEqual(result, b'[{"a": 1}, {"b": 2}]')

    def test_serialize_pydantic_model(self):
        model = MyModel(id=1, name='Test')
        result = self.cache.serialize(model)
        self.assertEqual(result, model.model_dump_json().encode())


class TestDeserialization(unittest.TestCase):
    def setUp(self):
        self.cache = DummyCache()

    def test_deserialize_none(self):
        result = self.cache.deserialize(None, as_type=int)
        self.assertIsNone(result)

    def test_deserialize_dict_from_json(self):
        raw = '{"key": "value"}'
        result = self.cache.deserialize(raw, as_type=dict)
        self.assertEqual(result, {'key': 'value'})

    def test_deserialize_list_from_json(self):
        raw = '[{"a": 1}, {"b": 2}]'
        result = self.cache.deserialize(raw, as_type=list)
        self.assertEqual(result, [{'a': 1}, {'b': 2}])

    def test_deserialize_model_from_json(self):
        raw = '{"id": 5, "name": "Hello"}'
        result = self.cache.deserialize(raw, as_type=MyModel)
        self.assertIsInstance(result, MyModel)
        self.assertEqual(result.id, 5)
        self.assertEqual(result.name, 'Hello')

    def test_deserialize_model_from_json_bytes(self):
        raw = b'{"id": 7, "name": "Test"}'
        result = self.cache.deserialize(raw, as_type=MyModel)
        self.assertIsInstance(result, MyModel)
        self.assertEqual(result.id, 7)

    def test_deserialize_raises_on_type_mismatch(self):
        with self.assertRaises(ValueDeserializationError):
            self.cache.deserialize(123, as_type=MyModel)

    def test_deserialize_model_with_missing_fields_raises(self):
        raw = '{"wrong_field": 1}'
        with self.assertRaises(ValueDeserializationError) as context:
            self.cache.deserialize(raw, as_type=MyModel)

        self.assertIsInstance(context.exception.__cause__, ValidationError)
