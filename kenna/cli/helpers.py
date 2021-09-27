from typing import Union, Iterable


def parse_variable_names(keys: Union[str, Iterable[str]]):
    keys = keys if isinstance(keys, str) else ','.join(keys)
    for old, new in (
        ('-', '_'),
        (' ', ''),
    ):
        keys = keys.replace(old, new)
    return sorted([key for key in keys.split(',') if key])
