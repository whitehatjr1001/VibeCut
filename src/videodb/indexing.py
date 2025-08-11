# src/videodb/indexing.py
import logging
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

from .base import VideoDB
from src.utils.agent_schemas import IndexType

logger = logging.getLogger(__name__)

class VideoDBIndexer(VideoDB):
    """VideoDB client for indexing videos with batch processing capabilities"""

    def index_video(self, video_id: str, index_type: IndexType = IndexType.SPOKEN_WORDS,
                   scene_prompt: Optional[str] = None) -> bool:
        """
        Index a single video for search
        
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
                logger.info(f"Indexed spoken words for video {video_id}")
            elif index_type == IndexType.SCENES:
                prompt = scene_prompt or "Describe the key visual scenes and actions"
                video.index_scenes(prompt=prompt)
                logger.info(f"Indexed scenes for video {video_id}")
            else:
                logger.error(f"Unsupported index type: {index_type}")
                return False
                
            return True
        except Exception as e:
            logger.error(f"Failed to index video {video_id}: {e}")
            return False

    def index_videos_batch(self, video_ids: List[str], 
                          index_type: IndexType = IndexType.SPOKEN_WORDS,
                          scene_prompt: Optional[str] = None,
                          max_workers: int = 3) -> Dict[str, bool]:
        """
        Index multiple videos concurrently
        
        Args:
            video_ids: List of video IDs to index
            index_type: Type of indexing to perform
            scene_prompt: Custom prompt for scene indexing
            max_workers: Maximum concurrent indexing operations
            
        Returns:
            Dict mapping video_id to success status
        """
        if not video_ids:
            logger.warning("No video IDs provided for indexing")
            return {}
            
        results = {}
        logger.info(f"Starting batch indexing of {len(video_ids)} videos")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all indexing tasks
            future_to_video = {
                executor.submit(self.index_video, video_id, index_type, scene_prompt): video_id
                for video_id in video_ids
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_video):
                video_id = future_to_video[future]
                try:
                    success = future.result()
                    results[video_id] = success
                except Exception as e:
                    logger.error(f"Indexing failed for video {video_id}: {e}")
                    results[video_id] = False
        
        successful = sum(results.values())
        logger.info(f"Batch indexing completed: {successful}/{len(video_ids)} successful")
        
        return results

    def create_indexed_collection(self, video_urls: List[str], 
                                 collection_name: str,
                                 index_type: IndexType = IndexType.SPOKEN_WORDS,
                                 scene_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new collection with uploaded and indexed videos
        
        Args:
            video_urls: List of video URLs to upload
            collection_name: Name for the new collection
            index_type: Type of indexing to perform
            scene_prompt: Custom prompt for scene indexing
            
        Returns:
            Dict with collection info and indexing results
        """
        logger.info(f"Creating indexed collection '{collection_name}' with {len(video_urls)} videos")
        
        # Set new collection name
        self.collection_name = collection_name
        self._collection = None  # Reset to create new collection
        
        # Upload all videos
        video_ids = []
        failed_uploads = []
        
        for url in video_urls:
            try:
                video_id = self.upload(url)
                video_ids.append(video_id)
                logger.info(f"Uploaded video: {video_id}")
            except Exception as e:
                logger.error(f"Failed to upload {url}: {e}")
                failed_uploads.append(url)
        
        # Index all uploaded videos
        indexing_results = {}
        if video_ids:
            indexing_results = self.index_videos_batch(
                video_ids, index_type, scene_prompt
            )
        
        return {
            "collection_name": collection_name,
            "total_videos": len(video_urls),
            "uploaded_videos": len(video_ids),
            "failed_uploads": failed_uploads,
            "indexing_results": indexing_results,
            "video_ids": video_ids
        }

    def get_collection_status(self) -> Dict[str, Any]:
        """
        Get status of current collection
        
        Returns:
            Dict with collection metadata
        """
        try:
            collection = self.get_collection()
            videos = collection.get_videos()
            
            return {
                "collection_name": self.collection_name,
                "total_videos": len(videos),
                "video_ids": [video.id for video in videos]
            }
        except Exception as e:
            logger.error(f"Failed to get collection status: {e}")
            return {"error": str(e)}

    # LangGraph Tool-Ready Methods
    def tool_index_single(self, video_id: str, content_type: str = "spoken") -> str:
        """
        Tool-friendly single video indexing
        
        Args:
            video_id: Video to index
            content_type: "spoken" or "visual"
            
        Returns:
            Status message
        """
        index_type = IndexType.SPOKEN_WORDS if content_type == "spoken" else IndexType.SCENES
        success = self.index_video(video_id, index_type)
        
        return f"✅ Indexed {video_id}" if success else f"❌ Failed to index {video_id}"

    def tool_index_batch(self, video_ids: str, content_type: str = "spoken") -> str:
        """
        Tool-friendly batch indexing (comma-separated video IDs)
        
        Args:
            video_ids: Comma-separated video IDs
            content_type: "spoken" or "visual"
            
        Returns:
            Status summary
        """
        ids_list = [vid.strip() for vid in video_ids.split(",")]
        index_type = IndexType.SPOKEN_WORDS if content_type == "spoken" else IndexType.SCENES
        
        results = self.index_videos_batch(ids_list, index_type)
        successful = sum(results.values())
        
        return f"✅ Indexed {successful}/{len(ids_list)} videos successfully"

    def tool_create_collection(self, video_urls: str, collection_name: str) -> str:
        """
        Tool-friendly collection creation (comma-separated URLs)
        
        Args:
            video_urls: Comma-separated video URLs
            collection_name: Name for collection
            
        Returns:
            Status summary
        """
        urls_list = [url.strip() for url in video_urls.split(",")]
        
        result = self.create_indexed_collection(
            video_urls=urls_list,
            collection_name=collection_name
        )
        
        return (f"🎬 Created collection '{collection_name}': "
                f"{result['uploaded_videos']}/{result['total_videos']} videos uploaded and indexed")
