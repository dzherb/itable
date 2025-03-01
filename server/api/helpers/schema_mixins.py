from collections.abc import Callable
import typing


class ValidateNameSchemaMixin:
    name: str | None

    def validate_name(self) -> None:
        if not self.name:
            raise ValueError('name cannot be empty')


class _ValidateIdFieldsMetaclass(type):
    def __new__(
        cls,
        name: str,
        bases: tuple[typing.Any, ...],
        attrs: dict[str, typing.Any],
    ) -> '_ValidateIdFieldsMetaclass':
        mixin_class = super().__new__(cls, name, bases, attrs)

        def validator_method_constructor(
            field: str,
        ) -> Callable[['_ValidateIdFieldsMetaclass'], None]:
            def method(self: _ValidateIdFieldsMetaclass) -> None:
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
