from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.services import FlowService
from src.app.db.connection import get_database


def get_flow_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return FlowService(database=db)
