from typing import Any
from bson import ObjectId
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.models.flow_model import Flow
# from src.app.transformers import evaluate_transfomer
from src.utils.validation import create_dynamic_model
from src.app.models.node_model import AnyNode, StartNode, ConditionalNode, EndNode
from src.app.core.exceptions import (
    ValidationError,
    NotFoundException,
    UpdateFailedException,
    InvalidObjectIdException,
    InvalidFlowException,
    InvalidPayloadException,
    RuntimeException,
    translate_mongo_error,
)


async def create_flow(db: AsyncIOMotorDatabase,
                      flow_name: str, flow_description: str) -> Flow:
    try:
        new_flow = Flow(
            flowName=flow_name,
            flowDescription=flow_description,
        )
        flow_dict = new_flow.model_dump(by_alias=True, exclude={'flowId'})
        result = await db.decision_flows.insert_one(flow_dict)
        new_flow.flowId = result.inserted_id

        return new_flow
    except Exception as e:
        raise translate_mongo_error(e)


async def get_flows(db: AsyncIOMotorDatabase) -> list[Flow]:
    try:
        flow_cursor = db.decision_flows.find({})
        flows_from_db = await flow_cursor.to_list(length=None)
    except Exception as e:
        raise translate_mongo_error(e)

    return [Flow.model_validate(flow) for flow in flows_from_db]


async def get_flow(db: AsyncIOMotorDatabase, id: str) -> Flow:
    try:
        if not ObjectId.is_valid(id):
            raise InvalidObjectIdException()

        flow_from_db = await db.decision_flows.find_one({'_id': ObjectId(id)})
    except Exception as e:
        raise translate_mongo_error(e)

    if not flow_from_db:
        raise NotFoundException()

    return Flow.model_validate(flow_from_db)


async def update_flow_metadata(db: AsyncIOMotorDatabase, id: str,
                               flow_name: str | None, flow_description: str | None):
    try:
        if not ObjectId.is_valid(id):
            raise InvalidObjectIdException()

        update_flow: dict[str, Any] = {}

        if flow_name is not None:
            update_flow['flowName'] = flow_name

        if flow_description is not None:
            update_flow['flowDescription'] = flow_description

        if not update_flow:
            return

        update_flow['updatedAt'] = datetime.now(timezone.utc)

        result = await db.decision_flows.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_flow}
        )
    except Exception as e:
        raise translate_mongo_error(e)

    if result.matched_count == 0:
        raise NotFoundException()

    if result.modified_count == 0:
        raise UpdateFailedException()


async def delete_flow(db: AsyncIOMotorDatabase, id: str):
    try:
        if not ObjectId.is_valid(id):
            raise InvalidObjectIdException()

        result = await db.decision_flows.delete_one({'_id': ObjectId(id)})
    except Exception as e:
        raise translate_mongo_error(e)

    if result.deleted_count == 0:
        raise NotFoundException()


async def update_flow_nodes(db: AsyncIOMotorDatabase, id: str,
                            nodes: list[AnyNode]):
    try:
        nodes_dict = [node.model_dump() for node in nodes]

        update_flow: dict[str, Any] = {
            'nodes': nodes_dict,
            'updatedAt': datetime.now(timezone.utc)
        }

        result = await db.decision_flows.update_one(
            {'_id': ObjectId(id)},
            {'$set': update_flow}
        )
    except Exception as e:
        raise translate_mongo_error(e)

    if result.matched_count == 0:
        raise NotFoundException()

    if result.modified_count == 0:
        raise UpdateFailedException()


def _evaluate_flow(nodes: list[AnyNode], start_node_id: str, env: dict) -> Any:
    current_node = next(
        (node for node in nodes if node.parentNodeId == start_node_id),
        None
    )
    assert current_node is not None

    while True:
        nodes.remove(current_node)
        if len(nodes) == 0:
            raise InvalidFlowException(
                'Flow is broken, could not find a response')

        match current_node.nodeType:
            case 'CONDITIONAL':
                assert isinstance(
                    current_node,
                    ConditionalNode
                )
                assert current_node.parentNodeId is not None

                result = evaluate_transfomer.evaluate(
                    current_node.metadata.expression.replace("'", '"').strip(),
                    env
                )

                next_node = next(
                    (node for node in nodes if node.parentNodeId == current_node.nodeId
                     and node.isFalseCase == (not result)),
                    None
                )

            case 'END':
                assert isinstance(
                    current_node,
                    EndNode
                )
                return current_node.metadata.response

        if next_node is None:
            raise InvalidFlowException(
                f'Flow is broken, could not find next node from {current_node.nodeId}')

        current_node = next_node


async def evaluate_flow(db: AsyncIOMotorDatabase, id: str,
                        payload: dict[str, Any]):

    flow = await get_flow(db, id)

    start_node = next(
        (node for node in flow.nodes if isinstance(node, StartNode)),
        None
    )

    if start_node is None:
        raise InvalidFlowException(
            'flow is broken, could not find start node')

    try:
        DynModel = create_dynamic_model(start_node.metadata)
        val_payload = DynModel(**payload)
    except ValidationError as e:
        raise InvalidPayloadException(e.errors())

    try:
        raw_resp = _evaluate_flow(
            flow.nodes,
            start_node.nodeId,
            val_payload.dict()
        )
        return {'response': raw_resp}
    except Exception as e:
        re = RuntimeException(f'Error while executing flow {str(e)}')
        setattr(re, 'originalErrorType', type(e).__name__)
        raise re from e


async def symbolic_executor(nodes: list[AnyNode]):
    visited = set()
    stack = [next(
        (node for node in nodes if isinstance(node, StartNode)),
        None)
    ]

    while stack
