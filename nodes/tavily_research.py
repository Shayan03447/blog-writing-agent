from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults
from state.State import Blog_State
from langchain_openai import ChatOpenAI
from typing import List
from Schemas.evidence_schema import EvidencePack
load_dotenv()
llm=ChatOpenAI(model="gpt-4.1-mini")

def _tavily_search(query: str, max_results: int = 5) -> List[dict]:
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

RESEARCH_SYSTEM="""You are a research synthesizer for technical writing.
Given raw web search results, produce a deduplicated list of EvidenceItem objects.
Rules:
- Only include items with a non-empty url.
- Prefer relavent + authoritive sources (company blogs, docs, reputable outlets).
- If a published date is explicitly present in the result payload, keep it as YYY--MM-DD.
  If missing or unclear, set published_at=null. Do not guess
- Keep snippits short
- Deduplicte by url 
"""
def research_node(state: Blog_State)->dict:
    queries=(state.get("queries", []) or [])
    max_results=6
    raw_results: List[dict]=[]
    for q in queries:
        raw_results.extend(_tavily_search(q, max_results=max_results))
    if not raw_results:
        return {"evidence":[]}
    extractor=llm.with_structured_output(EvidencePack)
    pack=extractor.invokr(
        [
            SystemMessage(content=RESEARCH_SYSTEM),
            HumanMessage(content=f"Raw results: \n{raw_results}")
        ]
    )
    # Deduplicate by url
    dedup={}
    for e in pack.evidence:
        if e.url:
            dedup[e.url]=e
    return {"evidence":list(dedup.values())}
    
