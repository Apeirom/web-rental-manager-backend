from pydantic import BeforeValidator
from typing import Annotated

def extract_enumerator_value(value):
    if hasattr(value, 'enumerator'):
        return value.enumerator
    return value

EnumeratorString = Annotated[str, BeforeValidator(extract_enumerator_value)]