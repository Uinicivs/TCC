import pytest
import asyncio
from src.app.services import flow_service


@pytest.mark.asyncio
async def test_create_flow_success(db):
    name = 'Fluxo de teste'
    desc = 'UMa descrição do fluxo'

    created_flow = await flow_service.create_flow(db, name, desc)

    assert created_flow is not None
    assert created_flow.flowName == name
    assert created_flow.flowDescription == desc

    saved_flow = await db['decision_flows'].find_one({'_id': created_flow.flowId})

    assert saved_flow is not None
    assert saved_flow['flowName'] == name


@pytest.mark.asyncio
async def test_get_flow_success(db):
    name = 'Fluxo de teste'
    desc = 'UMa descrição do fluxo'

    created_flow = await flow_service.create_flow(db, name, desc)
    found_flow = await flow_service.get_flow(db, str(created_flow.flowId))

    assert found_flow is not None
    assert found_flow.flowName == created_flow.flowName


@pytest.mark.asyncio
async def test_get_flows_success(db):
    await flow_service.create_flow(db, "Fluxo 1", "Desc 1")
    await flow_service.create_flow(db, "Fluxo 2", "Desc 2")

    all_flows = await flow_service.get_flows(db)

    assert len(all_flows) == 2
    assert all_flows[0].flowName == "Fluxo 1"
    assert all_flows[1].flowName == "Fluxo 2"


@pytest.mark.asyncio
async def test_update_flow_success(db):
    original_flow = await flow_service.create_flow(db, "Nome Original", "Desc Original")

    await asyncio.sleep(0.25)

    await flow_service.update_flow_metadata(
        db,
        str(original_flow.flowId),
        "Nome Atualizado",
        None
    )

    updated_flow = await flow_service.get_flow(db, str(original_flow.flowId))

    assert updated_flow.flowName == "Nome Atualizado"
    assert updated_flow.flowDescription == "Desc Original"
    assert updated_flow.updatedAt > original_flow.updatedAt


@pytest.mark.asyncio
async def test_delete_flow_success(db):
    # Arrange
    flow_to_delete = await flow_service.create_flow(db, "Fluxo para Deletar", "...")
    flow_id_str = str(flow_to_delete.flowId)

    # Act
    await flow_service.delete_flow(db, flow_id_str)

    flow_from_db = await flow_service.get_flow(db, flow_id_str)

    assert flow_from_db is None
