"""
State management for Video Editing Agent workflow
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from src.utils.agent_schemas import UserSettings,ClipInfo
from langgraph.graph import MessagesState



class VibeCutState(MessagesState, BaseModel):
    plan: Optional[Dict] = None
    user_settings: UserSettings = Field(default_factory=UserSettings)
    theme: Optional[str] = None
    video_sequence: List[ClipInfo] = Field(default_factory=list)
    multimodal: Optional[str] = None

    # Other fields and inherited properties...
