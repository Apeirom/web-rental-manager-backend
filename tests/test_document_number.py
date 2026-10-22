import pytest

from src.utils.document_number import (
    document_number_type,
    is_valid_cnpj,
    is_valid_cpf,
    normalize_document_number,
)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("52998224725", "529.982.247-25"),
        ("04.252.011/0001-10", "04.252.011/0001-10"),
        ("11144477735", "111.444.777-35"),
    ],
)
def test_normalize_document_number(value, expected):
    assert normalize_document_number(value) == expected


def test_document_type_uses_valid_cpf_or_cnpj():
    assert document_number_type("529.982.247-25") == "PF"
    assert document_number_type("04.252.011/0001-10") == "PJ"


@pytest.mark.parametrize(
    ("validator", "value"),
    [
        (is_valid_cpf, "111.111.111-11"),
        (is_valid_cpf, "529.982.247-24"),
        (is_valid_cnpj, "11.222.333/0001-00"),
        (is_valid_cnpj, "04.252.011/0001-11"),
    ],
)
def test_document_checksums_reject_invalid_values(validator, value):
    assert not validator(value)


def test_normalize_document_number_rejects_invalid_characters():
    with pytest.raises(ValueError):
        normalize_document_number("529.982.247-2X")
