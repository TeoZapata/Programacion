import base64
import hashlib
import hmac
import secrets


PBKDF2_ALGORITHM = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 260_000
SALT_BYTES = 16


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    salt_b64 = base64.b64encode(salt).decode("ascii")
    hash_b64 = base64.b64encode(digest).decode("ascii")
    return f"{PBKDF2_ALGORITHM}${PBKDF2_ITERATIONS}${salt_b64}${hash_b64}"


def verify_password(password: str, hashed: str) -> bool:
    if not hashed:
        return False
    try:
        if hashed.startswith(f"{PBKDF2_ALGORITHM}$"):
            _, raw_iterations, salt_b64, hash_b64 = hashed.split("$", 3)
            iterations = int(raw_iterations)
            salt = base64.b64decode(salt_b64.encode("ascii"))
            expected = base64.b64decode(hash_b64.encode("ascii"))
            current = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
            return hmac.compare_digest(current, expected)

        salt, legacy_hash = hashed.split(":", 1)
        expected = hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()
        return hmac.compare_digest(expected, legacy_hash)
    except Exception:
        return False


def password_needs_upgrade(hashed: str) -> bool:
    if not hashed or not hashed.startswith(f"{PBKDF2_ALGORITHM}$"):
        return True
    try:
        _, raw_iterations, _, _ = hashed.split("$", 3)
        return int(raw_iterations) < PBKDF2_ITERATIONS
    except Exception:
        return True
