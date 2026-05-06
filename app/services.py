import hashlib
import string

BASE62_ALPHABET = string.digits + string.ascii_letters
CODE_LENGTH = 5
MAX_COMBINATIONS = len(BASE62_ALPHABET) ** CODE_LENGTH


def _to_base62(num: int) -> str:
    if num == 0:
        return BASE62_ALPHABET[0]

    chars: list[str] = []
    base = len(BASE62_ALPHABET)
    while num > 0:
        num, rem = divmod(num, base)
        chars.append(BASE62_ALPHABET[rem])
    return "".join(reversed(chars))


def generate_code(url: str, salt: int = 0) -> str:
    digest = hashlib.sha256(f"{url}:{salt}".encode("utf-8")).digest()
    numeric = int.from_bytes(digest[:8], byteorder="big") % MAX_COMBINATIONS
    code = _to_base62(numeric)
    return code.rjust(CODE_LENGTH, BASE62_ALPHABET[0])[:CODE_LENGTH]
