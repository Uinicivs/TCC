from fastapi import APIRouter, Depends, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.services import flow_service
from src.app.db.connection import get_database
from src.api.dependencies.auth import get_api_key
from src.api.dtos.flow_dtos import (
    CreateFlowInDTO,
    ReadFlowsOutDTO,
    ReadFlowOutDTO,
    UpdateFlowInDTO,
    UpdateNodesInDTO,
    EvaluateFlowPayloadDTO,
    EvaluateFlowResponseDTO,
)


router = APIRouter(
    prefix='/decision_flows',
    tags=['Decision Flows'],
    dependencies=[Depends(get_api_key)]
)


@router.post('/', response_model=ReadFlowOutDTO,
             status_code=status.HTTP_201_CREATED)
async def create_flow(flow_in: CreateFlowInDTO,
                      db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.create_flow(
        db,
        flow_in.flowName,
        flow_in.flowDescription
    )


@router.get('/', response_model=list[ReadFlowsOutDTO])
async def get_flows(db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.get_flows(db)


@router.get('/{id}', response_model=ReadFlowOutDTO)
async def get_flow(id: str,
                   db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.get_flow(db, id)


@router.patch('/{id}',
              status_code=status.HTTP_204_NO_CONTENT)
async def update_flow_metadata(id: str,
                               flow_in: UpdateFlowInDTO,
                               db: AsyncIOMotorDatabase = Depends(get_database)):

    await flow_service.update_flow_metadata(
        db,
        id,
        flow_in.flowName,
        flow_in.flowDescription
    )
    return


@router.delete('/{id}',
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_flow(id: str,
                      db: AsyncIOMotorDatabase = Depends(get_database)):

    await flow_service.delete_flow(db, id)
    return


@router.put('/{id}/nodes',
            status_code=status.HTTP_204_NO_CONTENT)
async def update_flow_nodes(id: str,
                            nodes_in: list[UpdateNodesInDTO],
                            db: AsyncIOMotorDatabase = Depends(get_database)):

    await flow_service.update_flow_nodes(
        db,
        id,
        nodes_in
    )
    return


@router.post('/{id}/evaluate', response_model=EvaluateFlowResponseDTO)
async def evaluate_flow(id: str,
                        payload: EvaluateFlowPayloadDTO,
                        db: AsyncIOMotorDatabase = Depends(get_database)):

    return await flow_service.evaluate_flow(
        db,
        id,
        payload.model_dump()
    )


# @router.get('/{id}/test')
# async def symbolic_evaluate_flow(id: str,
#                                  db: AsyncIOMotorDatabase = Depends(get_database)):
#     return await flow_service.symbolic_evaluate_flow(
#         db,
#         id
#     )
