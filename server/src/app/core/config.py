from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DB_URL: str = ''
    DB_NAME: str = ''
    API_PORT: int = 8000
    API_HOST: str = 'localhost'
    API_KEYS: set[str] = {''}

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


@lru_cache
def get_settings() -> Settings:
    return Settings()
