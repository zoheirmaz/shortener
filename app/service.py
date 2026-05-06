import hashlib
import string

ALPHABET = string.ascii_letters + string.digits
BASE = len(ALPHABET)
MAX_CODE_LENGTH = 5


def _base62_encode(number: int) -> str:
    if number == 0:
        return ALPHABET[0]

    encoded = []
    while number > 0:
        number, remainder = divmod(number, BASE)
        encoded.append(ALPHABET[remainder])
    return "".join(reversed(encoded))


def make_code(url: str, attempt: int = 0) -> str:
    digest_input = f"{url}:{attempt}".encode("utf-8")
    digest = hashlib.sha256(digest_input).digest()
    number = int.from_bytes(digest[:8], byteorder="big")
    code = _base62_encode(number)
    return code[:MAX_CODE_LENGTH]
