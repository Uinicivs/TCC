from jose import jwt, JWTError  # type: ignore
from datetime import datetime, timedelta, timezone

from src.app.core.config import get_settings

settings = get_settings()


def create_access_token(data: dict, token_type: str, expires_delta: timedelta | None = None) -> tuple[str, datetime]:
    expire = datetime.now(timezone.utc) + (
        expires_delta or (
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            if token_type == 'access'
            else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
    )

    to_encode = data.copy()
    to_encode.update({'exp': expire, 'type': token_type})

    encoded = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )

    return encoded, expire


def decode_access_token(token: str, expected_type: str = 'access'):
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        if not payload:
            raise ValueError('Token has expired')

        if payload.get('type') != expected_type:
            raise ValueError('Invalid token type')

        return payload
    except JWTError as e:
        raise e
