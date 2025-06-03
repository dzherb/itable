import re

_undo_camel_case_pattern = re.compile(
    r'((?<=[a-z])[A-Z]|(?<!\A)[A-Z](?=[a-z]))',
)


def undo_camel_case(string: str) -> str:
    return re.sub(_undo_camel_case_pattern, r' \1', string)
