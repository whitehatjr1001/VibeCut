# src/videodb/base.py
import videodb
from typing import List, Optional, Any
from pydantic import BaseModel
from src.config import settings
from src.utils.agent_schemas import VideoUpload, IndexRequest, SearchRequest, IndexType

class VideoDB(BaseModel):
    """Minimal VideoDB client for video editing agent"""
    
    collection_name: str = "vibecut_videos"
    _conn: Optional[Any] = None
    _collection: Optional[Any] = None
    
    class Config:
        arbitrary_types_allowed = True
        underscore_attrs_are_private = True

    def connect(self):
        """Get or create VideoDB connection"""
        if not self._conn:
            self._conn = videodb.connect(api_key=settings.VIDEO_DB_API_KEY)
        return self._conn

    def get_collection(self):
        """Get or create collection"""
        if not self._collection:
            conn = self.connect()
            self._collection = conn.get_collection(name=self.collection_name)
        return self._collection

    def upload(self, video_url: str) -> str:
        """
        Upload video and return video ID
        
        Args:
            video_url: URL or path to video
            
        Returns:
            video_id: ID of uploaded video
        """
        collection = self.get_collection()
        video = collection.upload(url=video_url)
        return video.id

    def index(self, video_id: str, index_type: IndexType = IndexType.SPOKEN_WORDS, 
              scene_prompt: Optional[str] = None) -> bool:
        """
        Index video for search
        
        Args:
            video_id: ID of video to index
            index_type: Type of indexing to perform
            scene_prompt: Custom prompt for scene indexing
            
        Returns:
            bool: Success status
        """
        try:
            conn = self.connect()
            video = conn.get_video(video_id)
            
            if index_type == IndexType.SPOKEN_WORDS:
                video.index_spoken_words()
            elif index_type == IndexType.SCENES:
                prompt = scene_prompt or "Describe the visual scenes and actions"
                video.index_scenes(prompt=prompt)
                
            return True
        except Exception:
            return False

    def search(self, query: str, video_id: Optional[str] = None) -> Any:
        """
        Search for video segments
        
        Args:
            query: Natural language search query
            video_id: Specific video to search (searches collection if None)
            
        Returns:
            Search results object
        """
        if video_id:
            conn = self.connect()
            video = conn.get_video(video_id)
            return video.search(query=query)
        else:
            collection = self.get_collection()
            return collection.search(query=query)

    def upload_and_index(self, video_url: str, 
                        index_type: IndexType = IndexType.SPOKEN_WORDS,
                        scene_prompt: Optional[str] = None) -> str:
        """
        Complete workflow: upload and index video
        
        Args:
            video_url: URL or path to video
            index_type: Type of indexing
            scene_prompt: Custom scene prompt
            
        Returns:
            video_id: ID of processed video
        """
        video_id = self.upload(video_url)
        self.index(video_id, index_type, scene_prompt)
        return video_id
