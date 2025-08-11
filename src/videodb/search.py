# src/videodb/search.py
import logging
from typing import List, Optional, Dict, Any, Union
from enum import Enum
from pydantic import BaseModel, Field

import videodb
from videodb import SearchType, IndexType, SceneExtractionType
from .base import VideoDB
from src.utils.agent_schemas import IndexType as AgentIndexType

logger = logging.getLogger(__name__)

class SearchFilter(BaseModel):
    """Scene-level metadata filter for targeted search"""
    key: str = Field(..., max_length=20, description="Metadata key")
    value: Union[str, int] = Field(..., description="Metadata value")

class SceneSearchRequest(BaseModel):
    """Search request for scene-based queries"""
    query: str = Field(..., description="Natural language search query")
    video_id: Optional[str] = Field(default=None, description="Specific video to search")
    collection_name: Optional[str] = Field(default=None, description="Collection to search")
    filters: List[SearchFilter] = Field(default=[], description="Metadata filters")
    scene_index_id: Optional[str] = Field(default=None, description="Specific scene index")
    search_type: str = Field(default="semantic", description="Search type: semantic or keyword")
    result_threshold: int = Field(default=50, description="Result relevance threshold")

class VideoDBSearch(VideoDB):
    """VideoDB client for scene-based search operations"""

    def search_scenes(self, query: str, 
                     video_id: Optional[str] = None,
                     collection_name: Optional[str] = None,
                     filters: List[Dict[str, Union[str, int]]] = None,
                     scene_index_id: Optional[str] = None,
                     search_type: str = "semantic") -> Any:
        """
        Search for video scenes using natural language queries
        
        Args:
            query: Natural language search query
            video_id: Search specific video (searches collection if None)
            collection_name: Collection to search in
            filters: Scene-level metadata filters
            scene_index_id: Specific scene index to search
            search_type: "semantic" or "keyword"
            
        Returns:
            Search results object with playable segments
        """
        try:
            # Determine search type
            search_type_enum = SearchType.semantic if search_type == "semantic" else SearchType.keyword
            
            # Search in specific video
            if video_id:
                conn = self.connect()
                video = conn.get_video(video_id)
                
                search_params = {
                    "query": query,
                    "search_type": search_type_enum,
                    "index_type": IndexType.scene
                }
                
                # Add optional parameters
                if filters:
                    search_params["filter"] = filters
                if scene_index_id:
                    search_params["scene_index_id"] = scene_index_id
                    
                return video.search(**search_params)
            
            # Search in collection
            else:
                if collection_name:
                    self.collection_name = collection_name
                    self._collection = None  # Reset to get correct collection
                
                collection = self.get_collection()
                
                search_params = {
                    "query": query,
                    "search_type": search_type_enum,
                    "index_type": IndexType.scene
                }
                
                if filters:
                    search_params["filter"] = filters
                    
                return collection.search(**search_params)
                
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return None

    def search_with_metadata(self, query: str, metadata_filters: Dict[str, str],
                           video_id: Optional[str] = None) -> Any:
        """
        Search scenes with metadata filtering for targeted results
        
        Args:
            query: Natural language search query
            metadata_filters: Dict of metadata key-value pairs for filtering
            video_id: Specific video to search
            
        Returns:
            Filtered search results
        """
        # Convert metadata dict to filter format
        filters = [metadata_filters] if metadata_filters else None
        
        return self.search_scenes(
            query=query,
            video_id=video_id,
            filters=filters,
            search_type="semantic"
        )

    def find_action_scenes(self, action_type: str, video_id: str,
                          scene_index_id: Optional[str] = None) -> Any:
        """
        Find specific action scenes (e.g., "chase", "overtake", "crash")
        
        Args:
            action_type: Type of action to find
            video_id: Video to search in
            scene_index_id: Specific scene index
            
        Returns:
            Action-specific search results
        """
        query = f"intense {action_type} scene with dynamic movement"
        filters = [{"action_type": action_type}] if action_type else None
        
        return self.search_scenes(
            query=query,
            video_id=video_id,
            filters=filters,
            scene_index_id=scene_index_id
        )

    def multi_query_search(self, queries: List[str], 
                          video_id: Optional[str] = None) -> List[Any]:
        """
        Search for multiple queries and combine results
        
        Args:
            queries: List of search queries
            video_id: Video to search in
            
        Returns:
            List of search results for each query
        """
        results = []
        for query in queries:
            result = self.search_scenes(query=query, video_id=video_id)
            if result:
                results.append(result)
        return results

    def get_scene_clips(self, query: str, video_id: Optional[str] = None,
                       max_clips: int = 5) -> List[Dict[str, Any]]:
        """
        Get scene clips as structured data for video editing
        
        Args:
            query: Search query
            video_id: Video to search in
            max_clips: Maximum number of clips to return
            
        Returns:
            List of clip dictionaries with timing and metadata
        """
        try:
            results = self.search_scenes(query=query, video_id=video_id)
            if not results:
                return []
            
            shots = results.get_shots()[:max_clips]
            clips = []
            
            for shot in shots:
                clip = {
                    "start_time": shot.start,
                    "end_time": shot.end,
                    "duration": shot.end - shot.start,
                    "video_id": shot.video_id,
                    "description": getattr(shot, 'description', ''),
                    "relevance_score": getattr(shot, 'score', 0)
                }
                clips.append(clip)
            
            return clips
            
        except Exception as e:
            logger.error(f"Failed to get scene clips: {e}")
            return []

    def get_compilation_stream(self, queries: List[str], 
                             video_id: Optional[str] = None) -> Optional[str]:
        """
        Create a compilation stream from multiple search queries
        
        Args:
            queries: List of search queries for different scenes
            video_id: Video to search in
            
        Returns:
            Playable stream URL for compilation
        """
        try:
            all_results = []
            
            for query in queries:
                result = self.search_scenes(query=query, video_id=video_id)
                if result:
                    all_results.append(result)
            
            if not all_results:
                return None
            
            # Use the first result's play method (VideoDB handles compilation)
            return all_results[0].play()
            
        except Exception as e:
            logger.error(f"Failed to create compilation stream: {e}")
            return None

    # LangGraph Tool-Ready Methods
    def tool_search_scenes(self, query: str, video_id: str = None) -> str:
        """
        Tool-friendly scene search for agents
        
        Args:
            query: Natural language search query
            video_id: Video ID to search (optional)
            
        Returns:
            Human-readable search summary
        """
        try:
            results = self.search_scenes(query=query, video_id=video_id)
            if not results:
                return f"❌ No scenes found for query: '{query}'"
            
            shots = results.get_shots()
            playable_url = results.play()
            
            return (f"🎬 Found {len(shots)} scene(s) for '{query}'\n"
                   f"📺 Preview: {playable_url}")
                   
        except Exception as e:
            return f"❌ Search failed: {str(e)}"

    def tool_find_action_clips(self, action_type: str, video_id: str) -> str:
        """
        Tool-friendly action scene finder
        
        Args:
            action_type: Type of action (chase, crash, overtake, etc.)
            video_id: Video to search in
            
        Returns:
            Action clips summary
        """
        try:
            results = self.find_action_scenes(action_type, video_id)
            if not results:
                return f"❌ No {action_type} scenes found"
            
            shots = results.get_shots()
            return (f"🏃 Found {len(shots)} {action_type} scene(s)\n"
                   f"⏱️ Total duration: {sum(shot.end - shot.start for shot in shots):.1f}s")
                   
        except Exception as e:
            return f"❌ Failed to find {action_type} scenes: {str(e)}"

    def tool_create_compilation(self, search_queries: str, video_id: str = None) -> str:
        """
        Tool-friendly compilation creator
        
        Args:
            search_queries: Comma-separated search queries
            video_id: Video to search in
            
        Returns:
            Compilation summary with playable URL
        """
        try:
            queries = [q.strip() for q in search_queries.split(",")]
            stream_url = self.get_compilation_stream(queries, video_id)
            
            if not stream_url:
                return f"❌ Failed to create compilation from queries: {search_queries}"
            
            return (f"🎞️ Created compilation from {len(queries)} search queries\n"
                   f"📺 Stream: {stream_url}")
                   
        except Exception as e:
            return f"❌ Compilation failed: {str(e)}"
