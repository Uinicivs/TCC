from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.db.connection import get_database
from src.app.services import FlowService, UserService


def get_flow_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return FlowService(database=db)


def get_user_service(db: AsyncIOMotorDatabase = Depends(get_database)):
    return UserService(database=db)
