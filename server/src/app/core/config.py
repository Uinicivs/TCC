from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_URL: str = ''
    DB_NAME: str = ''
    API_PORT: int = 8000
    API_HOST: str = 'localhost'
    API_RELOAD: bool = False
    JWT_SECRET_KEY: str = ''
    JWT_ALGORITHM: str = ''
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 2

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()
