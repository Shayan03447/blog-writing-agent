from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from __future__ import annotations


class Task(BaseModel):
    id: int
    title: str
    goal: str = Field(
        ...,
        description="One sentence discribing what the reader should do/understand after this section."
    )
    bullets: List[str] = Field(
        ...,
        min_length=3,
        max_length=6,
        description="3-6 concrete, non-overlaping subpoints to cover in this section."
    )
    target_words: int = Field(
        ...,
        description="Target words count for this section (120-550)."
    )
    tags: List[str] = Field(default_factory=list)
    requires_research: bool = False
    requires_citations: bool = False
    requires_code: bool = False
