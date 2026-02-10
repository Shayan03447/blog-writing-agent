from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class RouterDecision(BaseModel):
    needs_research: bool
    mode: Literal["open_book","hybrid","closed_book"]
    reason: str
    queries: List[str] = Field(default_factory=list)
    max_results_per_query: int = Field(5, description="Max results per query")