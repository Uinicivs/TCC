from bson import ObjectId
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from src.app.models.symbolic_model import SymbolicExecution
from src.app.core.exceptions import (
    translate_mongo_error,
    InvalidObjectIdException,
)


class TelemetryService:
    def __init__(self, database: AsyncIOMotorDatabase) -> None:
        self.database = database

    async def store_symbolic_execution(self, execution: SymbolicExecution) -> None:
        try:
            execution_dict = execution.model_dump(
                by_alias=True, exclude={'id'})

            count = await self.database.symbolic_events.count_documents(
                {'flowId': execution.flowId}
            )
            if count > 1:
                oldest_doc = await self.database.symbolic_events.find_one(
                    {'flowId': execution.flowId},
                    sort=[('timestamp', 1)]
                )
                if oldest_doc:
                    await self.database.symbolic_events.delete_one(
                        {'_id': oldest_doc['_id']}
                    )

            await self.database.symbolic_events.insert_one(execution_dict)
        except Exception as e:
            raise translate_mongo_error(e)

    async def get_last_symbolic_execution_time(self, flow_id: str) -> datetime | None:
        try:
            if not ObjectId.is_valid(flow_id):
                raise InvalidObjectIdException()

            execution_from_db = await self.database.symbolic_events.find_one(
                {'flowId': ObjectId(flow_id)},
                sort=[('timestamp', -1)],
                projection={'timestamp': 1}
            )
        except Exception as e:
            raise translate_mongo_error(e)

        if not execution_from_db:
            return None

        return SymbolicExecution.model_validate(execution_from_db).timestamp

    async def compare_with_previous_report(self, flow_id: str) -> bool:
        try:
            if not ObjectId.is_valid(flow_id):
                raise InvalidObjectIdException()

            last_two = await self.database.symbolic_events.find(
                {'flowId': flow_id}
            ).sort('timestamp', -1).limit(2).to_list(2)
        except Exception as e:
            raise translate_mongo_error(e)

        if len(last_two) < 2:
            return False

        current, previous = (
            SymbolicExecution.model_validate(last_two[0]),
            SymbolicExecution.model_validate(last_two[1])
        )

        delta_pruned = previous.pruned - current.pruned
        delta_reductions = previous.reductions - current.reductions

        resolved = (delta_pruned + delta_reductions) > 0

        return resolved

    async def compute_symbolic_evolution_index(self, flow_id: str) -> float:
        try:
            if not ObjectId.is_valid(flow_id):
                raise InvalidObjectIdException()

            last_two = await self.database.symbolic_events.find(
                {'flowId': flow_id}
            ).sort('timestamp', -1).limit(2).to_list(2)
        except Exception as e:
            raise translate_mongo_error(e)

        if len(last_two) < 2:
            return 0.0

        curr, prev = (
            SymbolicExecution.model_validate(last_two[0]),
            SymbolicExecution.model_validate(last_two[1])
        )

        def delta(a: float, b: float) -> float:
            if a == b == 0:
                return 0
            return (a - b) / (abs(b) + 1e-6)

        metrics = [
            ('pruned', prev.pruned, curr.pruned, -1),
            ('reductions', prev.reductions, curr.reductions, -0.3),
            ('coverage', prev.coverage, curr.coverage, 1.5)
        ]

        score: float = 0
        total: float = 0

        for _, old, new, weight in metrics:
            score += weight * delta(old, new)
            total += abs(weight)

        return max(-1, min(1, score / total))
