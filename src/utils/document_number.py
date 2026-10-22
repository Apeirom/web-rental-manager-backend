import re


_ALLOWED_DOCUMENT_CHARACTERS = re.compile(r"^[\d./\-\s]+$")


def _document_digits(value: str) -> str:
    if not isinstance(value, str) or not _ALLOWED_DOCUMENT_CHARACTERS.fullmatch(value.strip()):
        raise ValueError("Documento deve conter somente números e pontuação de CPF/CNPJ.")
    return re.sub(r"\D", "", value)


def _calculate_check_digit(digits: str, weights: tuple[int, ...]) -> str:
    remainder = sum(int(number) * weight for number, weight in zip(digits, weights)) % 11
    return str(0 if remainder < 2 else 11 - remainder)


def is_valid_cpf(value: str) -> bool:
    try:
        digits = _document_digits(value)
    except ValueError:
        return False
    if len(digits) != 11 or len(set(digits)) == 1:
        return False

    first_digit = _calculate_check_digit(digits[:9], tuple(range(10, 1, -1)))
    second_digit = _calculate_check_digit(
        digits[:9] + first_digit,
        tuple(range(11, 1, -1)),
    )
    return digits[-2:] == first_digit + second_digit


def is_valid_cnpj(value: str) -> bool:
    try:
        digits = _document_digits(value)
    except ValueError:
        return False
    if len(digits) != 14 or len(set(digits)) == 1:
        return False

    first_digit = _calculate_check_digit(
        digits[:12],
        (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2),
    )
    second_digit = _calculate_check_digit(
        digits[:12] + first_digit,
        (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2),
    )
    return digits[-2:] == first_digit + second_digit


def normalize_document_number(value: str) -> str:
    digits = _document_digits(value)
    if len(digits) == 11 and is_valid_cpf(digits):
        return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"
    if len(digits) == 14 and is_valid_cnpj(digits):
        return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
    raise ValueError("Informe um CPF ou CNPJ válido.")


def normalize_cnpj(value: str) -> str:
    normalized = normalize_document_number(value)
    if len(_document_digits(normalized)) != 14:
        raise ValueError("Informe um CNPJ válido.")
    return normalized


def document_number_type(value: str) -> str:
    normalized = normalize_document_number(value)
    return "PJ" if len(_document_digits(normalized)) == 14 else "PF"
