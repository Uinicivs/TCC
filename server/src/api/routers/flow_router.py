from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.services import flow_service
from src.app.db.connection import get_database
from src.api.dtos.flow_dtos import (
    CreateFlowInDTO,
    ReadFlowOutDTO,
    UpdateFlowInDTO,
)


router = APIRouter(
    prefix='/decision_flows',
    tags=['Decision Flows']
)


@router.post('/', response_model=ReadFlowOutDTO)
async def create_flow(flow_in: CreateFlowInDTO,
                      db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.create_flow(
        db,
        flow_in.flowName,
        flow_in.flowDescription
    )


@router.get('/', response_model=list[ReadFlowOutDTO])
async def get_flows(db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.get_flows(db)


@router.get('/{id}', response_model=ReadFlowOutDTO)
async def get_flow(id: str,
                   db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.get_flow(db, id)


@router.patch('/{id}')
async def update_flow_metadata(id: str,
                               flow_in: UpdateFlowInDTO,
                               db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.update_flow_metadata(
        db,
        id,
        flow_in.flowName,
        flow_in.flowDescription
    )


@router.delete('/{id}')
async def delete_flow(id: str,
                      db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.delete_flow(db, id)
