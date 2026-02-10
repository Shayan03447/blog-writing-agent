from __future__ import annotations
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from state.State import Blog_State
from Schemas.router_schema import RouterDecision
from langchain_core.messages import SystemMessage, HumanMessage
load_dotenv()
llm=ChatOpenAI(model="gpt-4.1-mini")

ROUTER_SYSTEM="""You are a routing module for a technical blog planner.
Decide whether web research is needed before planning
Modes:
- closed_book (needs_research=false):
Evergreen topics where correctness does not depend on the recent facts (concept, fundamentals).
- hybrid (needs_research=true):
Mostly evergreen but needs up-to-date examples/tools/models to be usefull.
- Open_book (needs_research=true):
Mostlt volatile: Weekly roundups, "this_week", "latest", ranking, pricing, policy/regulation.

if needs_research=true:
- Output 3-10 high signal queries.
- Queries should be scoped and specific (avoid generic queries like just "AI" or "LLM").
- If user asked for "last week/this week/latest", reflect that constraint in the queries
"""
def Router_Node(state: Blog_State)-> dict:
    topic=state["topic"]
    decider=llm.with_structured_output(RouterDecision)
    decision=decider.invoke(
        [
            SystemMessage(content=ROUTER_SYSTEM),
            HumanMessage(content=f"Topic: {topic}")
        ]
    )
    return {
        "needs_research":decision.needs_research,
        "mode": decision.mode,
        "queries":decision.queries,

    }
def route_next(state: Blog_State) -> str:
    if state["needs_research"]==True:
        return "research"
    else:
        return "orchestrator"

