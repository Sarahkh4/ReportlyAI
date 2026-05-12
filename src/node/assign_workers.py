from schema.state import State
from langgraph.types import Send
from utils.loggers import logger


def assign_workers(state: State):

    """Assign a worker to each section in the plan"""
    logger.info("Assigning workers to report sections...")

    return [Send("llm_call",{"section":s}) for s in state["sections"]] 