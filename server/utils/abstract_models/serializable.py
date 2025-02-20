from collections.abc import Iterable, Sequence


class Serializable:
    SERIALIZABLE_FIELDS: Sequence[str] = ('id',)

    def serialize(
        self,
        serializable_fields: Iterable[str] | None = None,
    ) -> dict:
        if serializable_fields is None:
            return {
                field: getattr(self, field)
                for field in self.SERIALIZABLE_FIELDS
            }

        return {field: getattr(self, field) for field in serializable_fields}
