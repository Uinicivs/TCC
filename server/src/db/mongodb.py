from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from contextlib import asynccontextmanager
from src.core.config import get_settings


settings = get_settings()

client: AsyncIOMotorClient | None = None
db: AsyncIOMotorDatabase | None = None


@asynccontextmanager
async def connect_to_db():
    client = AsyncIOMotorClient(settings.DB_URL)
    db = client[settings.DB_NAME]

    try:
        yield db
    except Exception:
        pass
    finally:
        client.close()
