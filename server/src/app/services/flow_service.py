from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Any
from datetime import datetime, timezone
from bson import ObjectId
from src.app.models.flow_model import Flow, AnyNode
from src.app.core.exceptions import (
    NotFoundException,
    UpdateFailedException,
    InvalidObjectIdException,
    translate_mongo_error,
)


async def create_flow(db: AsyncIOMotorDatabase,
                      flow_name: str, flow_description: str) -> Flow:
    try:
        new_flow = Flow(
            flowName=flow_name,
            flowDescription=flow_description,
        )
        flow_dict = new_flow.model_dump(by_alias=True)
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
