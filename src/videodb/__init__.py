# src/videodb/__init__.py
from .videodb_client import VideoDBClient
from .base import VideoDBBase
from .indexing import VideoIndexer
from .search import VideoSearcher
from .voiceover import VideoVoiceOver

__version__ = "0.1.0"
__all__ = [
    "VideoDBClient",
    "VideoDBBase", 
    "VideoIndexer",
    "VideoSearcher",
    "VideoVoiceOver"
]

# Convenience factory function
def create_client(videodb_api_key: str,
                 openai_api_key: str = None,
                 groq_api_key: str = None,
                 videodb_base_url: str = None) -> VideoDBClient:
    """Create a VideoDB client with all features
    
    Args:
        videodb_api_key: VideoDB API key
        openai_api_key: OpenAI API key for TTS
        groq_api_key: Groq API key for TTS  
        videodb_base_url: Optional VideoDB base URL
        
    Returns:
        Configured VideoDBClient instance
    """
    return VideoDBClient(
        videodb_api_key=videodb_api_key,
        videodb_base_url=videodb_base_url,
        openai_api_key=openai_api_key,
        groq_api_key=groq_api_key
    )
