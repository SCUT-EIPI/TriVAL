from agents.graph import create_trival_graph
from agents.schema import ContextSchema


def run_trival(problem_description: str, context: ContextSchema) -> dict:
    graph = create_trival_graph()
    initial_state = {
        "problem_description": problem_description,
        "code_execution_count": 0,
        "code_validation_count": 0,
    }
    return graph.invoke(
        initial_state,
        config={"recursion_limit": 500},
        context=context,
    )
