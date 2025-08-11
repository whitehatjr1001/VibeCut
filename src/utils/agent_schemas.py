# src/utils/agent_schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum

class IndexType(str, Enum):
    SPOKEN_WORDS = "spoken_words"
    SCENES = "scenes"

class VideoUpload(BaseModel):
    url: str = Field(..., description="Video URL or file path")
    collection_name: Optional[str] = Field(default="default", description="Collection to upload to")

class IndexRequest(BaseModel):
    video_id: str = Field(..., description="Video ID to index")
    index_type: IndexType = Field(default=IndexType.SPOKEN_WORDS, description="Type of indexing")
    scene_prompt: Optional[str] = Field(default=None, description="Custom scene description prompt")

class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    collection_id: Optional[str] = Field(default=None, description="Collection to search in")
    video_id: Optional[str] = Field(default=None, description="Specific video to search")
