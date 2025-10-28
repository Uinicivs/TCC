from typing import Any

from src.app.evaluators.parser import get_parser
from src.app.core.exceptions import InvalidFlowException
from src.app.evaluators.transformers import ConcreteTransformer
from src.app.models.node_model import AnyNode, ConditionalNode, EndNode


class ConcreteExecutor:
    def __init__(self, nodes: list[AnyNode]) -> None:
        self.nodes = nodes

    def _evaluate(self, rule: str, payload: dict) -> bool:
        tree = get_parser().parse(rule)
        transformer = ConcreteTransformer(payload)

        return transformer.transform(tree)

    def execute(self, payload: dict[str, Any], start_node_id: str) -> Any:
        current_node = next(
            (node for node in self.nodes if node.parentNodeId == start_node_id),
            None
        )
        assert current_node is not None

        while True:
            self.nodes.remove(current_node)
            if len(self.nodes) == 0:
                raise InvalidFlowException(
                    'Flow is broken, could not find a response')

            match current_node.nodeType:
                case 'CONDITIONAL':
                    assert isinstance(
                        current_node,
                        ConditionalNode
                    )
                    assert current_node.parentNodeId is not None

                    result = self._evaluate(
                        current_node.metadata.expression.replace(
                            "'", '"').strip(),
                        payload
                    )

                    next_node = next(
                        (node for node in self.nodes if node.parentNodeId == current_node.nodeId
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
