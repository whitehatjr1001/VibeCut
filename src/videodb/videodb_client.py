# src/videodb/videodb_client.py
import logging
from typing import List, Optional, Dict, Any, Union
from concurrent.futures import ThreadPoolExecutor

from .base import VideoDB
from .indexing import VideoDBIndexer  
from .search import VideoDBSearch
from src.utils.agent_schemas import IndexType

logger = logging.getLogger(__name__)

class VideoDBClient:
    """
    Unified VideoDB client for video editing agent
    Combines upload, indexing, and search capabilities
    """
    
    def __init__(self, collection_name: str = "vibecut_videos"):
        """
        Initialize VideoDB client
        
        Args:
            collection_name: Name of the collection to work with
        """
        self.collection_name = collection_name
        
        # Initialize specialized clients
        self.base = VideoDB(collection_name=collection_name)
        self.indexer = VideoDBIndexer(collection_name=collection_name)
        self.searcher = VideoDBSearch(collection_name=collection_name)
        
    # Core Operations
    def upload_video(self, video_url: str) -> str:
        """Upload single video and return ID"""
        return self.base.upload(video_url)
    
    def index_video(self, video_id: str, index_type: IndexType = IndexType.SPOKEN_WORDS,
                   scene_prompt: Optional[str] = None) -> bool:
        """Index single video for search"""
        return self.indexer.index_video(video_id, index_type, scene_prompt)
    
    def search_video(self, query: str, video_id: Optional[str] = None) -> Any:
        """Search for video segments"""
        return self.searcher.search_scenes(query, video_id)
    
    # Workflow Methods
    def process_video(self, video_url: str, 
                     index_type: IndexType = IndexType.BOTH,
                     scene_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete workflow: upload, index, and prepare for search
        
        Args:
            video_url: URL or path to video
            index_type: Type of indexing to perform
            scene_prompt: Custom scene description prompt
            
        Returns:
            Dict with video_id and processing status
        """
        try:
            # Upload video
            video_id = self.upload_video(video_url)
            logger.info(f"Uploaded video: {video_id}")
            
            # Index for both spoken words and scenes if requested
            indexing_success = True
            
            if index_type in [IndexType.SPOKEN_WORDS, IndexType.BOTH]:
                spoken_success = self.index_video(video_id, IndexType.SPOKEN_WORDS)
                indexing_success = indexing_success and spoken_success
                
            if index_type in [IndexType.SCENES, IndexType.BOTH]:  
                scene_success = self.index_video(video_id, IndexType.SCENES, scene_prompt)
                indexing_success = indexing_success and scene_success
            
            return {
                "video_id": video_id,
                "upload_success": True,
                "indexing_success": indexing_success,
                "ready_for_search": indexing_success
            }
            
        except Exception as e:
            logger.error(f"Failed to process video {video_url}: {e}")
            return {
                "video_id": None,
                "upload_success": False,
                "indexing_success": False,
                "ready_for_search": False,
                "error": str(e)
            }

    def process_videos_batch(self, video_urls: List[str],
                           index_type: IndexType = IndexType.BOTH,
                           scene_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Process multiple videos in batch
        
        Args:
            video_urls: List of video URLs
            index_type: Type of indexing
            scene_prompt: Custom scene prompt
            
        Returns:
            Batch processing results
        """
        logger.info(f"Processing batch of {len(video_urls)} videos")
        
        # Upload all videos first
        video_ids = []
        failed_uploads = []
        
        for url in video_urls:
            try:
                video_id = self.upload_video(url)
                video_ids.append(video_id)
            except Exception as e:
                logger.error(f"Failed to upload {url}: {e}")
                failed_uploads.append(url)
        
        # Batch index uploaded videos
        indexing_results = {}
        if video_ids:
            indexing_results = self.indexer.index_videos_batch(
                video_ids, index_type, scene_prompt
            )
        
        successful_videos = [vid for vid, success in indexing_results.items() if success]
        
        return {
            "total_videos": len(video_urls),
            "uploaded_videos": len(video_ids),
            "indexed_videos": len(successful_videos),
            "failed_uploads": failed_uploads,
            "ready_video_ids": successful_videos,
            "success_rate": f"{len(successful_videos)}/{len(video_urls)}"
        }

    # Search and Edit Operations
    def find_clips(self, search_queries: List[str], 
                  video_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find clips matching multiple search queries
        
        Args:
            search_queries: List of natural language queries
            video_id: Specific video to search
            
        Returns:
            List of clips with timing and metadata
        """
        all_clips = []
        
        for query in search_queries:
            clips = self.searcher.get_scene_clips(query, video_id, max_clips=3)
            for clip in clips:
                clip['search_query'] = query
            all_clips.extend(clips)
        
        # Sort by relevance score
        all_clips.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return all_clips

    def create_edit_compilation(self, edit_queries: List[str],
                              video_id: Optional[str] = None) -> Optional[str]:
        """
        Create a playable compilation from edit queries
        
        Args:
            edit_queries: List of scene descriptions for the edit
            video_id: Video to create compilation from
            
        Returns:
            Playable stream URL
        """
        return self.searcher.get_compilation_stream(edit_queries, video_id)

    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about current collection"""
        return self.indexer.get_collection_status()

    # Agent Tool Methods
    def agent_upload_and_index(self, video_url: str, content_type: str = "both") -> str:
        """
        Agent-friendly video processing
        
        Args:
            video_url: Video URL to process
            content_type: "spoken", "visual", or "both"
            
        Returns:
            Human-readable status message
        """
        # Map content type to IndexType
        type_mapping = {
            "spoken": IndexType.SPOKEN_WORDS,
            "visual": IndexType.SCENES,
            "both": IndexType.BOTH
        }
        
        index_type = type_mapping.get(content_type, IndexType.BOTH)
        scene_prompt = "Describe key visual scenes, actions, and emotions" if content_type != "spoken" else None
        
        result = self.process_video(video_url, index_type, scene_prompt)
        
        if result['ready_for_search']:
            return f"✅ Successfully processed video: {result['video_id']}\n📹 Ready for scene search and editing"
        else:
            return f"❌ Failed to process video: {result.get('error', 'Unknown error')}"

    def agent_find_edit_clips(self, edit_description: str, video_id: str = None) -> str:
        """
        Agent-friendly clip finder for video editing
        
        Args:
            edit_description: Description of the edit or scenes needed
            video_id: Video to search in
            
        Returns:
            Edit-ready clip summary
        """
        try:
            # Break edit description into search queries
            queries = [q.strip() for q in edit_description.split(",")]
            clips = self.find_clips(queries, video_id)
            
            if not clips:
                return f"❌ No clips found for: '{edit_description}'"
            
            total_duration = sum(clip['duration'] for clip in clips)
            
            clip_summary = "\n".join([
                f"  🎬 {clip['start_time']:.1f}s-{clip['end_time']:.1f}s ({clip['duration']:.1f}s) - {clip['search_query']}"
                for clip in clips[:5]  # Show top 5
            ])
            
            return (f"🎞️ Found {len(clips)} clips ({total_duration:.1f}s total):\n"
                   f"{clip_summary}")
                   
        except Exception as e:
            return f"❌ Search failed: {str(e)}"

    def agent_create_compilation(self, edit_plan: str, video_id: str = None) -> str:
        """
        Agent-friendly compilation creator
        
        Args:
            edit_plan: Comma-separated list of scenes for the edit
            video_id: Video to create compilation from
            
        Returns:
            Compilation status with playable URL
        """
        try:
            queries = [q.strip() for q in edit_plan.split(",")]
            stream_url = self.create_edit_compilation(queries, video_id)
            
            if stream_url:
                return (f"🎬 Created video compilation from {len(queries)} scenes\n"
                       f"📺 Preview: {stream_url}")
            else:
                return f"❌ Failed to create compilation from: '{edit_plan}'"
                
        except Exception as e:
            return f"❌ Compilation error: {str(e)}"

    def agent_collection_status(self) -> str:
        """Agent-friendly collection status"""
        try:
            info = self.get_collection_info()
            if "error" in info:
                return f"❌ Collection error: {info['error']}"
            
            return (f"📁 Collection '{info['collection_name']}':\n"
                   f"  📹 {info['total_videos']} videos ready for editing\n"
                   f"  🔍 All videos indexed and searchable")
                   
        except Exception as e:
            return f"❌ Status check failed: {str(e)}"
