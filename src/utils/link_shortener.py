import secrets
import string
from src.config import get_settings

settings = get_settings()


def gen_short_code(length: int = settings.short_code_length) -> str:
    alphabet = string.ascii_letters + string.digits + "-_"
    return "".join(secrets.choice(alphabet) for _ in range(length))
