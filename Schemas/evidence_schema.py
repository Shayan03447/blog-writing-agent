from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class EvidenceItem(BaseModel):
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    snippet: Optional[str] = None

class EvidencePack(BaseModel):
    evidence: List[EvidenceItem] = Field(default_factory=list)
    
