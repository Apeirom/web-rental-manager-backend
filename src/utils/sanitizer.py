def sanitize_csv_cell(value: str | None) -> str:
    if value is None:
        return ""

    string_value = str(value)
    if not string_value:
        return ""

    dangerous_prefixes = ("=", "+", "-", "@", "\t", "\r")
    if string_value.startswith(dangerous_prefixes):
        return f"'{string_value}"

    return string_value


def sanitize_string(value: str | None) -> str:
    if value is None:
        return ""

    cleaned = str(value).replace("\x00", "").strip()
    return cleaned
