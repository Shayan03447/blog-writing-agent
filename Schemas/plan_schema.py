from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from .task_schema import Task

class Plan(BaseModel):
    blog_title: str
    audience: str
    tone: str
    blog_kind: Literal["Explainer","Tutorial","news_roundup","Comparison","System_Design"]="Explainer" 
    constraints: List[str] = Field(default_factory=list)
    tasks: List[Task]
