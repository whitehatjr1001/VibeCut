"""
Video processing helper functions
"""
from typing import List, Dict, Any, Optional
import os
from pathlib import Path

def calculate_total_duration(clips: List[Dict[str, Any]]) -> float:
    """Calculate total duration of clips"""
    return sum(clip.get("duration", 0) for clip in clips)

def validate_video_file(file_path: str) -> bool:
    """Validate if file is a supported video format"""
    supported_formats = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    return Path(file_path).suffix.lower() in supported_formats

def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def generate_thumbnail_timestamps(duration: float, count: int = 3) -> List[float]:
    """Generate timestamps for thumbnail extraction"""
    if count <= 1:
        return [duration / 2]
    
    timestamps = []
    interval = duration / (count + 1)
    
    for i in range(1, count + 1):
        timestamps.append(i * interval)
    
    return timestamps

def optimize_clip_selection(clips: List[Dict], target_duration: float) -> List[Dict]:
    """Select clips that best fit target duration"""
    if not clips:
        return []
    
    # Sort by relevance score
    sorted_clips = sorted(clips, key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    selected_clips = []
    current_duration = 0
    
    for clip in sorted_clips:
        clip_duration = clip.get("duration", 0)
        
        if current_duration + clip_duration <= target_duration:
            selected_clips.append(clip)
            current_duration += clip_duration
        
        # Stop if we have enough content
        if current_duration >= target_duration * 0.8:  # 80% of target
            break
    
    return selected_clips

def create_temp_file(suffix: str = ".mp4") -> str:
    """Create a temporary file path"""
    import tempfile
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    temp_file.close()
    return temp_file.name

def cleanup_temp_files(file_paths: List[str]) -> None:
    """Clean up temporary files"""
    for file_path in file_paths:
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(f"Warning: Could not delete {file_path}: {e}")

def estimate_processing_time(clips_count: int, total_duration: float) -> int:
    """Estimate video processing time in seconds"""
    # Rough estimation: 2 seconds per clip + 1 second per 10 seconds of video
    base_time = clips_count * 2
    duration_time = total_duration / 10
    return int(base_time + duration_time + 10)  # +10 for overhead
