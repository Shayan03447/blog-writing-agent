from nodes.orches_node import orchestrator_node, fanout
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from state.State import Blog_State
from Schemas.task_schema import Task
from Schemas.plan_schema import Plan
from Schemas.evidence_schema import EvidenceItem
load_dotenv()
llm=ChatOpenAI(model="gpt-4.1-mini")

WORKER_SYSTEM="""You are a senior technical writer and developer advocate.
Write ONE section of a technical blog post in Markdown.

Hard constraints:
- Follow the provided Goal and cover ALL Bullets in order (do not skip or merge bullets).
- Stay close to Target words (±15%).
- Output ONLY the section content in Markdown (no blog title H1, no extra commentary).
- Start with a '## <Section Title>' heading.

Scope guard:
- If blog_kind == "news_roundup": do NOT turn this into a tutorial/how-to guide.
  Do NOT teach web scraping, RSS, automation, or "how to fetch news" unless bullets explicitly ask for it.
  Focus on summarizing events and implications.

Grounding policy:
- If mode == open_book:
  - Do NOT introduce any specific event/company/model/funding/policy claim unless it is supported by provided Evidence URLs.
  - For each event claim, attach a source as a Markdown link: ([Source](URL)).
  - Only use URLs provided in Evidence. If not supported, write: "Not found in provided sources."
- If requires_citations == true:
  - For outside-world claims, cite Evidence URLs the same way.
- Evergreen reasoning is OK without citations unless requires_citations is true.

Code:
- If requires_code == true, include at least one minimal, correct code snippet relevant to the bullets.

Style:
- Short paragraphs, bullets where helpful, code fences for code.
- Avoid fluff/marketing. Be precise and implementation-oriented.
"""
def worker_node(payload: dict)-> dict:
    task= Task(**payload["task"])
    plan=Plan(**payload["plan"])
    evidence=[EvidenceItem(**e) for e in payload.get("evidence",[])]
    topic=payload["topic"]
    mode=payload.get("mode","closed_book")

    bullets_text= "\n-" + "\n-".join(task.bullets)
    evidence_text=""
    if evidence:
        evidence_text="\n".join(
            f"- {e.title} | {e.url} | {e.published_at or 'date:unknown'}".strip()
            for e in evidence[:20]
        )
    section_md=llm.invoke([
        SystemMessage(content=WORKER_SYSTEM),
        HumanMessage(
            content=(
                f"Blog_title: {plan.blog_title}\n"
                f"Audience: {plan.audience}\n"
                f"Tone: {plan.tone}\n"
                f"Blog kind : {plan.blog_kind}\n"
                f"Constraints: {plan.constraints}\n"
                f"Topic: {payload['topic']}\n"
                f"Mode: {payload.get('mode')}\n"
                f"As-of: {payload.get('as_of')} (recency days={payload.get('recency_days')})\n\n"
                f"Section title: {task.title}\n"
                f"Goal: {task.goal}\n"
                f"Target words: {task.target_words}\n"
                f"Tags: {task.tags}\n"
                f"requires_research: {task.requires_research}\n"
                f"requires_citations: {task.requires_citations}\n"
                f"requires_code: {task.requires_code}\n"
                f"Bullets: {bullets_text}\n\n"
                f"Evidence (Only use these URLS when citing):\n{evidence_text}\n"

                
            )
        ),
    ]).content.strip()

    return {"sections":[(task.id, section_md)]}
