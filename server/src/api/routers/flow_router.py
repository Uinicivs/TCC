from fastapi import APIRouter, Request, Depends, status

from src.api.dtos import flow_dtos
from src.app.services import FlowService, UserService
from src.app.models.user_model import User
from src.api.dependencies import (
    get_limiter,
    get_flow_service,
    get_user_service,
    get_current_user,
    get_authorized_user,
)


router = APIRouter(
    prefix='/decision_flows',
    tags=['Decision Flows']
)
limiter = get_limiter()


@router.post('', response_model=flow_dtos.ReadFlowOutDTO, status_code=status.HTTP_201_CREATED)
async def create_flow(flow_in: flow_dtos.CreateFlowInDTO,
                      current_user: User = Depends(get_current_user),
                      flow_service: FlowService = Depends(get_flow_service),
                      user_service: UserService = Depends(get_user_service)):
    assert current_user.id is not None

    await user_service.increment_flow_count(current_user.id)

    created_flow = await flow_service.create_flow(
        owner_id=current_user.id,
        flow_name=flow_in.flowName,
        flow_description=flow_in.flowDescription,
    )

    return created_flow


@router.get(
    '',
    response_model=list[flow_dtos.ReadFlowsOutDTO],
)
async def get_flows(current_user: User = Depends(get_current_user),
                    service: FlowService = Depends(get_flow_service)):
    assert current_user.id is not None
    return await service.get_flows(owner_id=current_user.id)


@router.get(
    '/{id}',
    response_model=flow_dtos.ReadFlowOutDTO,
    dependencies=[Depends(get_authorized_user)],
)
async def get_flow(id: str, service: FlowService = Depends(get_flow_service)):
    return await service.get_flow(id=id)


@router.patch(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_authorized_user)],
)
async def update_flow_metadata(id: str, flow_in: flow_dtos.UpdateFlowInDTO,
                               service: FlowService = Depends(get_flow_service)):
    await service.update_flow_metadata(
        id=id,
        flow_name=flow_in.flowName,
        flow_description=flow_in.flowDescription
    )
    return


@router.delete(
    '/{id}',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_authorized_user)],
)
async def delete_flow(id: str,
                      current_user: User = Depends(get_current_user),
                      flow_service: FlowService = Depends(get_flow_service),
                      user_service: UserService = Depends(get_user_service)):
    assert current_user.id is not None

    await user_service.decrement_flow_count(current_user.id)
    await flow_service.delete_flow(id)
    return


@router.put(
    '/{id}/nodes',
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(get_authorized_user)],
)
async def update_flow_nodes(id: str,
                            nodes_in: list[flow_dtos.UpdateNodesInDTO],
                            service: FlowService = Depends(get_flow_service)):
    await service.update_flow_nodes(
        id=id,
        nodes=nodes_in
    )
    return


@router.post(
    '/{id}/evaluate',
    dependencies=[Depends(get_authorized_user)],
    response_model=flow_dtos.EvaluateFlowResponseDTO,
)
async def evaluate_flow(id: str,
                        payload: flow_dtos.EvaluateFlowPayloadDTO,
                        service: FlowService = Depends(get_flow_service)):
    return await service.evaluate_flow(
        id=id,
        payload=payload.model_dump()
    )


@router.get(
    '/{id}/test',
    dependencies=[Depends(get_authorized_user)],
    response_model=flow_dtos.TestFlowResponseDTO,
)
@limiter.limit('10/minute')
async def symbolic_evaluate_flow(request: Request,
                                 id: str,
                                 service: FlowService = Depends(get_flow_service)):
    return await service.symbolic_evaluate_flow(id=id)
