from pydantic import BaseModel, Field
from typing import List, Optional, Literal

class ImageSpec(BaseModel):
    placeholders: str = Field(...,description="e.g. [[IMAGE_1]]")
    filename: str = Field(..., description="Save under images/,e.g. qkv_flow.png")
    alt: str
    caption: str
    prompt: str = Field(..., description="Prompt send to the image model")
    size: Literal["1024*1024", "1024*1536", "1536*1024"]="1024*1024"
    quality: Literal["low", "medium","high"]="medium"

class GlobalImagePlan(BaseModel):
    md_with_placeholders: str
    images: List[ImageSpec]= Field(default_factory=list)


