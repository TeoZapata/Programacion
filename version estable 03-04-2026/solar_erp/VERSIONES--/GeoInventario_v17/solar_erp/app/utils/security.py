import hashlib
import secrets


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    return f"{salt}:{hashed}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        salt, hash_val = hashed.split(":")
        expected = hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
        return expected == hash_val
    except Exception:
        return False
