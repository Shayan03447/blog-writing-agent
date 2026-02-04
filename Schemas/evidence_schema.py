from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class EvidenceItems(BaseModel):
    title: str
    url: str
    source: Optional[str] = None
    published_at: Optional[str] = None
    snippet: Optional[str] = None