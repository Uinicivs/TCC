import bcrypt

# rounds padrão; pode ajustar (12 a 14 é bom pra prod)
BCRYPT_ROUNDS = 12


def hash_password(password: str) -> str:
    if not isinstance(password, str):
        raise TypeError("Password must be a string")

    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        raise TypeError("Both arguments must be strings")

    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError:
        return False
