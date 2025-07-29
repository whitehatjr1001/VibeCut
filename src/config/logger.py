"""
Logging configuration for Video Editing Agent
"""
import logging
import sys
from pathlib import Path

def setup_logger(name: str = "video_editing_agent", level: str = "INFO") -> logging.Logger:
    """Setup structured logging"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    return logger

# Global logger instance
logger = setup_logger()
