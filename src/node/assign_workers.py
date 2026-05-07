from schema.state import State
from langgraph.types import Send


def assign_workers(state: State):

    """Assign a worker to each section in the plan"""

    return [Send("llm_call",{"section":s}) for s in state["sections"]] 