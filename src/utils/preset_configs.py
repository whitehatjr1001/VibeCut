"""
Preset configurations for different video editing modes
"""
from typing import Dict, Any

# Preset configurations
PRESETS: Dict[str, Dict[str, Any]] = {
    "highlights": {
        "name": "Highlights",
        "description": "Best moments compilation with smooth transitions",
        "default_duration": 60,
        "max_clips": 8,
        "transition_style": "fade",
        "music_style": "uplifting",
        "pacing": "medium",
        "effects": {
            "intro_fade": True,
            "outro_fade": True,
            "auto_color_correction": True
        },
        "search_keywords": ["best", "important", "key moment", "highlight"]
    },
    
    "reel": {
        "name": "Social Media Reel",
        "description": "Fast-paced, engaging content for social platforms",
        "default_duration": 30,
        "max_clips": 6,
        "aspect_ratio": "9:16",
        "transition_style": "quick_cut",
        "pacing": "fast",
        "effects": {
            "auto_captions": True,
            "trending_music": True,
            "dynamic_zoom": True,
            "text_overlays": True
        },
        "search_keywords": ["dynamic", "engaging", "action", "movement"]
    },
    
    "custom": {
        "name": "Custom",
        "description": "Fully customizable video with user specifications",
        "default_duration": 45,
        "max_clips": 10,
        "transition_style": "smooth",
        "pacing": "user_defined",
        "effects": {
            "flexible": True
        },
        "search_keywords": []  # User-defined
    }
}

def get_preset_config(preset_type: str) -> Dict[str, Any]:
    """Get configuration for a specific preset"""
    return PRESETS.get(preset_type, PRESETS["custom"])

def get_all_presets() -> Dict[str, Dict[str, Any]]:
    """Get all available presets"""
    return PRESETS

def validate_preset(preset_type: str) -> bool:
    """Validate if preset type is supported"""
    return preset_type in PRESETS
