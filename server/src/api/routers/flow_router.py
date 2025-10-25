from fastapi import APIRouter, Depends, status

from src.api.dtos import flow_dtos
from src.app.services import FlowService
from src.api.dependencies import get_api_key, get_flow_service


router = APIRouter(
    prefix='/decision_flows',
    tags=['Decision Flows'],
    dependencies=[Depends(get_api_key)]
)


@router.post('/', response_model=flow_dtos.ReadFlowOutDTO, status_code=status.HTTP_201_CREATED)
async def create_flow(flow_in: flow_dtos.CreateFlowInDTO,
                      service: FlowService = Depends(get_flow_service)):
    return await service.create_flow(
        flow_name=flow_in.flowName,
        flow_description=flow_in.flowDescription
    )


@router.get('/', response_model=list[flow_dtos.ReadFlowsOutDTO])
async def get_flows(service: FlowService = Depends(get_flow_service)):
    return await service.get_flows()


@router.get('/{id}', response_model=flow_dtos.ReadFlowOutDTO)
async def get_flow(id: str, service: FlowService = Depends(get_flow_service)):
    return await service.get_flow(id=id)


@router.patch('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_flow_metadata(id: str, flow_in: flow_dtos.UpdateFlowInDTO,
                               service: FlowService = Depends(get_flow_service)):
    await service.update_flow_metadata(
        id=id,
        flow_name=flow_in.flowName,
        flow_description=flow_in.flowDescription
    )
    return


@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_flow(id: str, service: FlowService = Depends(get_flow_service)):
    await service.delete_flow(id=id)
    return


@router.put('/{id}/nodes', status_code=status.HTTP_204_NO_CONTENT)
async def update_flow_nodes(id: str,
                            nodes_in: list[flow_dtos.UpdateNodesInDTO],
                            service: FlowService = Depends(get_flow_service)):
    await service.update_flow_nodes(
        id=id,
        nodes=nodes_in
    )
    return


@router.post('/{id}/evaluate', response_model=flow_dtos.EvaluateFlowResponseDTO)
async def evaluate_flow(id: str,
                        payload: flow_dtos.EvaluateFlowPayloadDTO,
                        service: FlowService = Depends(get_flow_service)):
    return await service.evaluate_flow(
        id=id,
        payload=payload.model_dump()
    )


@router.get('/{id}/test')
async def symbolic_evaluate_flow(id: str,
                                 service: FlowService = Depends(get_flow_service)):
    return await service.symbolic_evaluate_flow(id=id)
