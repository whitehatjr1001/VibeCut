from pydantic import BaseModel
from typing import Optional,Literal
from enum import Enum 


class PresetType(str, Enum):
    HIGHLIGHTS = "highlights"
    REEL = "reel" 
    CUSTOM = "custom"
    
    
class UserSettings(BaseModel):
    preset: PresetType
    duration: Optional[int] = None
    theme: Optional[str] = None
    additional_options: Optional[dict] = None

    voice_over_script: Optional[str] = None
    ai_script_generation: Optional[bool] = False
    voice_style: Optional[Literal["male", "female", "neutral", "robotic", "natural"]] = "neutral"
    voice_language: Optional[str] = "en-US"

class ClipInfo(BaseModel):
    clip_id: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    order: int