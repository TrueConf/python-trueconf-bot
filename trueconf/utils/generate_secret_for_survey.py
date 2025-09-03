import hashlib
import secrets


async def generate_secret_for_survey(title: str) -> str:
    random_str = secrets.token_hex(8)
    combined = title + random_str
    hash_ = hashlib.sha1(combined.encode("utf-8")).hexdigest()

    return hash_