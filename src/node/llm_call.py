from schema.state import WorkerState
from langchain.messages import SystemMessage, HumanMessage
from utils.llm_planner import llm
from langchain.agents import create_agent
from src.tools.web_search import tavily_tool
from utils.prompts.llm_prompt import SECTION_WRITER_PROMPT
from utils.loggers import logger


agent = create_agent(
    model = llm,
    tools = [tavily_tool],
)
async def llm_call(state: WorkerState):
    """Worker writes a section of the report"""
    logger.info("Worker starting to write a section...")
    try:
        section = await agent.ainvoke(
           { "messages":
            [
                SystemMessage(content = SECTION_WRITER_PROMPT),
                HumanMessage(content = f"Here is the section name {state['section'].name} and description {state['section'].description}")
            ]
        })
        final_message = section["messages"][-1].content
        logger.info("Worker finished writing a section.")
        return {"completed_sections": [final_message]}
    
    
    
    except Exception as e:
        logger.error(f"Failed to write section {e}")
        raise RuntimeError(f"Failed to write section {e}")
    
