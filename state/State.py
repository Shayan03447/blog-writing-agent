from typing import Literal, TypedDict, Annotated, List, Optional
from pydantic import BaseModel, Field
from Schemas.evidence_schema import EvidenceItems
from Schemas.plan_schema import Plan
import operator

class Blog_State(TypedDict):
    topic: str
    # Evidence
    mode: str
    needs_research: bool
    queries: List[str]
    evidence: List[EvidenceItems]
    plan: Optional[Plan]
    sections: Annotated[List[tuple[int, str]],operator.add]
    # Reducer
    merged_md: str
    md_with_placeholders: str
    image_specs: List[dict]
    final: str