from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class RouterDecision(BaseModel):
    needs_research: bool
    mode: Literal["open_book","hybrid","closed_book"]
    queries: List[str] = Field(default_factory=list)