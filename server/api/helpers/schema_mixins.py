class ValidateNameSchemaMixin:
    def validate_name(self):
        if not self.name:
            raise ValueError('name cannot be empty')
