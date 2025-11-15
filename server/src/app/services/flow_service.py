import time
from typing import Any
from bson import ObjectId
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.models.flow_model import Flow
from src.utils.pool import run_in_threadpool
from src.app.models.node_model import AnyNode
from src.utils.validation import create_dynamic_model
from src.app.services.telemetry_service import TelemetryService
from src.app.evaluators.executors import ConcreteExecutor, SymbolicExecutor
from src.app.models.symbolic_model import SymbolicReport, SymbolicExecution
from src.app.core.metrics import (
    # per flow
    tests_total,
    evolution_index,
    inconsistencies_ratio,
    time_to_modification_seconds,

    # globals
    execution_errors_total,
    execution_timeouts_total,
    execution_duration_seconds,
)
from src.app.core.exceptions import (
    translate_mongo_error,

    ValidationError,
    RuntimeException,
    NotFoundException,
    InvalidFlowException,
    UpdateFailedException,
    InvalidPayloadException,
    InvalidObjectIdException,
    SymbolicTimeoutException,
)


class FlowService:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database
        self.telemetry_service = TelemetryService(database)

    async def create_flow(self, flow_name: str, flow_description: str, owner_id: str) -> Flow:
        try:
            new_flow = Flow(
                flowName=flow_name,
                flowDescription=flow_description,
                ownerId=owner_id
            )
            flow_dict = new_flow.model_dump(by_alias=True, exclude={'flowId'})
            result = await self.database.decision_flows.insert_one(flow_dict)
            new_flow.flowId = result.inserted_id

            return new_flow
        except Exception as e:
            raise translate_mongo_error(e)

    async def get_flows(self, owner_id: str) -> list[Flow]:
        try:
            flow_cursor = self.database.decision_flows.find(
                {'ownerId': owner_id})
            flows_from_db = await flow_cursor.to_list(length=None)
        except Exception as e:
            raise translate_mongo_error(e)

        return [Flow.model_validate(flow) for flow in flows_from_db]

    async def get_flow(self, id: str) -> Flow:
        try:
            if not ObjectId.is_valid(id):
                raise InvalidObjectIdException()

            flow_from_db = await self.database.decision_flows.find_one({'_id': ObjectId(id)})
        except Exception as e:
            raise translate_mongo_error(e)

        if not flow_from_db:
            raise NotFoundException()

        return Flow.model_validate(flow_from_db)

    async def update_flow_metadata(self, id: str, flow_name: str | None, flow_description: str | None) -> None:
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

            result = await self.database.decision_flows.update_one(
                {'_id': ObjectId(id)},
                {'$set': update_flow}
            )
        except Exception as e:
            raise translate_mongo_error(e)

        if result.matched_count == 0:
            raise NotFoundException()

        if result.modified_count == 0:
            raise UpdateFailedException()

    async def delete_flow(self, id: str) -> None:
        try:
            if not ObjectId.is_valid(id):
                raise InvalidObjectIdException()

            result = await self.database.decision_flows.delete_one({'_id': ObjectId(id)})
        except Exception as e:
            raise translate_mongo_error(e)

        if result.deleted_count == 0:
            raise NotFoundException()

    async def update_flow_nodes(self, id: str, nodes: list[AnyNode]) -> None:
        if not ObjectId.is_valid(id):
            raise InvalidObjectIdException()

        before = await self.telemetry_service.get_last_symbolic_execution_timestamp(id)
        now = datetime.now(timezone.utc)

        try:
            nodes_dict = [node.model_dump() for node in nodes]

            update_flow: dict[str, Any] = {
                'nodes': nodes_dict,
                'updatedAt': now
            }

            result = await self.database.decision_flows.update_one(
                {'_id': ObjectId(id)},
                {'$set': update_flow}
            )
        except Exception as e:
            raise translate_mongo_error(e)

        if result.matched_count == 0:
            raise NotFoundException()

        if result.modified_count == 0:
            raise UpdateFailedException()

        if before:
            delta = (now - before).total_seconds()
            time_to_modification_seconds.labels(
                flow_id=id
            ).set(delta)

    async def evaluate_flow(self, id: str, payload: dict[str, Any]) -> dict:
        flow = await self.get_flow(id)

        start_node = next(
            (node for node in flow.nodes if node.nodeType == 'START'),
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

        executor = ConcreteExecutor(flow.nodes)

        try:
            raw_resp = executor.execute(
                payload=val_payload.dict(),
                start_node_id=start_node.nodeId
            )
            return {'response': raw_resp}
        except Exception as e:
            re = RuntimeException(f'Error while executing flow {str(e)}')
            setattr(re, 'originalErrorType', type(e).__name__)
            raise re from e

    async def symbolic_evaluate_flow(self, id: str) -> SymbolicReport:
        flow = await self.get_flow(id)
        start = time.perf_counter()

        num_start_nodes = sum(1 for n in flow.nodes if n.nodeType == 'START')
        num_end_nodes = sum(1 for n in flow.nodes if n.nodeType == 'END')

        if num_start_nodes != 1:
            raise InvalidFlowException(
                f'Flow is broken, it has {num_start_nodes} START NODEs, '
                'it should be 1'
            )

        if num_end_nodes < 2:
            raise InvalidFlowException(
                f'Flow is broken, it has {num_end_nodes} END NODEs, '
                'it should have at least 2'
            )

        try:
            executor = SymbolicExecutor(flow.nodes)
            result: SymbolicReport = await run_in_threadpool(executor.execute)

        except Exception as e:
            if isinstance(e, SymbolicTimeoutException):
                execution_timeouts_total.inc()

            execution_errors_total.inc()

            re = RuntimeException(f'Error while testing flow {str(e)}')
            setattr(re, 'originalErrorType', type(e).__name__)
            raise re from e

        duration = time.perf_counter() - start
        execution_duration_seconds.observe(duration)

        tests_total.labels(flow_id=id).inc()

        total_conds = sum(1 for n in flow.nodes if n.nodeType == 'CONDITIONAL')
        pruned_node_ids = {p.nodeId for p in result.pruned}
        reduction_node_ids = {r.nodeId for r in result.reductions}
        uncovered_node_ids = {u.nodeId for u in result.uncovered}

        affected_nodes = pruned_node_ids | reduction_node_ids | uncovered_node_ids
        ratio = len(affected_nodes) / total_conds if total_conds else 0.0
        inconsistencies_ratio.labels(flow_id=id).set(ratio)

        await self.telemetry_service.store_symbolic_execution(
            SymbolicExecution(
                flowId=id,
                pruned=len(result.pruned),
                reductions=len(result.reductions),
                uncovered=len(result.uncovered),
                coverage=(result.coverage.endCount / num_end_nodes)
            )
        )

        sei = await self.telemetry_service.compute_symbolic_evolution_index(id)
        evolution_index.labels(flow_id=id).set(sei)

        return result
