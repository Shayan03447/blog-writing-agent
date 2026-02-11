import os
from datetime import date, timedelta
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from state.State import Blog_State
from langchain_openai import ChatOpenAI
from typing import List, Optional
from Schemas.evidence_schema import EvidencePack
load_dotenv()
llm=ChatOpenAI(model="gpt-4.1-mini")

def _tavily_search(query: str, max_results: int = 5) -> List[dict]:
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("TAVILY_API_KEY is not set")
    try:
        tool = TavilySearchResults(max_results=max_results)
        results=tool.invoke({"query":query})
        normalized: List[dict] = []
        for r in results or []:
            normalized.append(
                {
                    "title":r.get("title") or "",
                    "url" : r.get("url") or "",
                    "snippet": r.get("snippet") or r.get("content") or "",
                    "published_at": r.get("published_date") or r.get("published_at"),
                    "source": r.get("source"),
                }
            )
        return normalized
    except Exception as e:
        print(f"Error searching Tavily: {e}")
        return []

def _iso_to_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    try:
        return date.fromisoformat(s[:10])
    except Exception:
        return None
        
    

RESEARCH_SYSTEM="""You are a research synthesizer for technical writing.
Given raw web search results, produce a deduplicated list of EvidenceItem objects.
Rules:
- Only include items with a non-empty url.
- Prefer relevent + authoritative sources (company blogs, docs, reputable outlets).
- If a published date is explicitly present in the result payload, keep it as YYYY-MM-DD.
  If missing or unclear, set published_at=null. Do not guess
- Keep snippets short
- Deduplicate by url 
"""
def research_node(state: Blog_State)->dict:
    queries=(state.get("queries") or [])[:10]
    max_results=6
    raw_results: List[dict]=[]
    for q in queries:
        raw_results.extend(_tavily_search(q, max_results=max_results))
    if not raw_results:
        return {"evidence":[]}
    extractor=llm.with_structured_output(EvidencePack)
    pack=extractor.invoke(
        [
            SystemMessage(content=RESEARCH_SYSTEM),
            HumanMessage(content=(
                f"As-of date: {state['as_of']}\n"
                f"Recency days: {state['recency_days']}\n\n"
                f"Raw results: \n{raw_results}"))
        ]
    )
    # Deduplicate by url
    dedup={}
    for e in pack.evidence:
        if e.url:
            dedup[e.url]=e
    evidence = list(dedup.values())

    if state.get("mode") == "open_book":
        as_of=date.fromisoformat(state["as_of"])
        cutoff= as_of -timedelta(days=int(state["recency_days"]))
        evidence=[e for e in evidence if (d := _iso_to_date(e.published_at)) and d >=cutoff]
    return {"evidence":evidence}
    
