class ValidateNameSchemaMixin:
    name: str | None

    def validate_name(self):
        if not self.name:
            raise ValueError('name cannot be empty')


class _ValidateIdFieldsMetaclass(type):
    def __new__(cls, name, bases, attrs):
        mixin_class = super().__new__(cls, name, bases, attrs)

        def validator_method_constructor(field: str):
            def method(self):
                if getattr(self, field) <= 0:
                    raise ValueError(f'{field} must be greater than 0')

            return method

        for field in attrs.get('__annotations__', ()):
            if not (field.endswith('_id') or field == 'id'):
                continue

            setattr(
                mixin_class,
                f'validate_{field}',
                validator_method_constructor(field),
            )

        return mixin_class


class ValidateIdFieldsMixin(metaclass=_ValidateIdFieldsMetaclass): ...
