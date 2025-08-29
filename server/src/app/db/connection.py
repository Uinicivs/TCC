from fastapi import FastAPI
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.app.core.config import get_settings


settings = get_settings()

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global client, db

    client = AsyncIOMotorClient(settings.DB_URL, tz_aware=True)
    db = client[settings.DB_NAME]

    yield

    if client:
        client.close()


def get_database() -> AsyncIOMotorDatabase | None:
    return db
