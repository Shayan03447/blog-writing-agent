from state.State import Blog_State
from Schemas.plan_schema import Plan
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from typing import List
from langgraph.types import Send
load_dotenv()
llm=ChatOpenAI(model="gpt-4.1-mini")
ORCH_SYSTEM="""You are a senior technical writer and developer advocate.
Your job is to produce a highly actionable outline for a technical blog post.

Hard Requirements:
- Create 5-9 sections (tasks) suitable for the topic and audience.
- Each task must include :
  1) goal (one sentence)
  2) 3-6 bullets that are concrete, specific, and non-overlapping
  3) target words counts (120-550)

Quality bar
- Assume the reader is a developer: use correct terminology.
- Bullets must be actionable : build/compare/measure/verify/debug.
- Ensure the overall plan include at least 2 of these somewhere.
  * minimal code sketch / MWE (set requires_code=True for that section)
  * edge cases / failure modes
  * performance/cost considerations
  * security/privacy considerations (if relevant)
  * debugging/observability tips

Grounding rules:
- Mode closed_book: keep it evergreen; do not depend on evidence.
- Mode hybrid:
  - Use evidence for up-to-date examples (models/tools/releases) in bullets.
  - Mark sections using fresh info as requires_research=True and requires_citations=True.
- Mode open_book:
  - Set blog_kind = "news_roundup".
  - Every section is about summarizing events + implications.
  - DO NOT include tutorial/how-to sections unless user explicitly asked for that.
  - If evidence is empty or insufficient, create a plan that transparently says "insufficient sources"
    and includes only what can be supported.

Output must strictly match the Plan schema
"""
def orchestrator_node(state: Blog_State)->dict:
    planner=llm.with_structured_output(Plan)
    evidence=state.get("evidence",[])
    mode=state.get("mode", "closed_book")

    forced_kind="news_roundup" if mode=="open_book" else None
    plan=planner.invoke(
        [
            SystemMessage(content=ORCH_SYSTEM),
            HumanMessage(content=(
                f"Topic: {state['topic']}\n"
                f"mode: {state.get('mode', 'closed_book')}\n"
                f"As-of: {state.get('as_of', '')} (recency days: {state.get('recency_days', 3650)})\n"
                f"{'Force blog_kind=news_roundup' if forced_kind else ''}\n\n"
                f"Evidence: \n{[e.model_dump() for e in evidence][:16]}"
                
            ))
        ]
    )
    if forced_kind:
        plan.blog_kind="news_roundup"
    return {"plan":plan}

def fanout(state: Blog_State):
    sends=[]
    for task in state["plan"].tasks:
        sends.append(
            Send(
                "worker",
                {
                    "task":task.model_dump(),
                    "topic":state["topic"],
                    "mode":state["mode"],
                    "as_of":state["as_of"],
                    "recency_days":state["recency_days"],
                    "plan":state["plan"].model_dump(),
                    "evidence":[e.model_dump() for e in state.get("evidence",[])],
                },

            )
        )
    return sends    
