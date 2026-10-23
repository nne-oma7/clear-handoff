import re

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
REFERENCE_PATTERN = re.compile(r"^(?:CH-?)?0*(\d{1,9})$", re.IGNORECASE)


def clean_email(value: str) -> str:
    return value.strip().lower()


def is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value))


def clean_phone(value: str) -> str:
    value = value.strip()
    plus = "+" if value.startswith("+") else ""
    return plus + re.sub(r"\D", "", value)


def is_valid_phone(value: str) -> bool:
    digits = re.sub(r"\D", "", value)
    return 7 <= len(digits) <= 15


def phone_key(value: str) -> str:
    # Last 10 digits, so 08012345678 and +2348012345678 match.
    return re.sub(r"\D", "", value)[-10:]


def parse_reference(value: str):
    match = REFERENCE_PATTERN.match(value.strip())
    return int(match.group(1)) if match else None


def contact_matches(record, supplied: str) -> bool:
    supplied = supplied.strip()

    if "@" in supplied:
        return (
            bool(record.contact_email)
            and clean_email(supplied) == record.contact_email
        )

    key = phone_key(supplied)

    return (
        len(key) >= 7
        and bool(record.contact_phone)
        and key == phone_key(record.contact_phone)
    )