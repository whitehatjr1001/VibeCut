"""
State management for Video Editing Agent workflow
"""
from typing import Dict, List, Optional, Any
from typing_extensions import TypedDict

class VideoEditingState(TypedDict):
    """State schema for the video editing workflow"""
    
    # User inputs
    user_query: str
    uploaded_clips: List[str]  # VideoDB clip IDs
    preset_type: str  # "highlights", "reel", "custom"
    custom_duration: Optional[int]
    custom_theme: Optional[str]
    
    # Workflow state
    execution_plan: Optional[Dict[str, Any]]
    search_queries: List[str]
    retrieved_clips: List[Dict[str, Any]]
    selected_clips: List[Dict[str, Any]]
    assembly_config: Optional[Dict[str, Any]]
    
    # Results
    final_video_url: Optional[str]
    preview_url: Optional[str]
    
    # System state
    current_step: str
    processing_status: str
    error_message: Optional[str]
    
    # Metadata
    created_at: Optional[str]
    duration_estimate: Optional[int]
