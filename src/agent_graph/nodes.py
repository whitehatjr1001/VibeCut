"""
LangGraph Node Implementations
"""
from typing import Dict, Any
from src.agent_graph.state import VideoEditingState
from src.agents.planner import VideoPlanner
from src.agents.retriever import VideoRetriever  
from src.agents.assembler import VideoAssembler
from src.integrations.videodb_client import VideoDBClient
from src.integrations.llm_client import LLMClient
from src.config.logger import logger

# Initialize clients
videodb_client = VideoDBClient()
llm_client = LLMClient()

# Initialize agents
planner = VideoPlanner(llm_client)
retriever = VideoRetriever(videodb_client, llm_client)
assembler = VideoAssembler(videodb_client)

def planner_node(state: VideoEditingState) -> VideoEditingState:
    """Planning phase - create execution strategy"""
    logger.info("Executing planner node")
    
    try:
        execution_plan = planner.create_plan(
            user_query=state["user_query"],
            clips=state["uploaded_clips"],
            preset=state["preset_type"],
            custom_settings={
                "duration": state.get("custom_duration"),
                "theme": state.get("custom_theme")
            }
        )
        
        return {
            **state,
            "execution_plan": execution_plan,
            "search_queries": execution_plan.get("search_queries", []),
            "current_step": "planning_complete",
            "processing_status": "Plan created successfully"
        }
        
    except Exception as e:
        logger.error(f"Planning failed: {e}")
        return {
            **state,
            "current_step": "error",
            "error_message": f"Planning failed: {str(e)}"
        }

def retriever_node(state: VideoEditingState) -> VideoEditingState:
    """Retrieval phase - find and select clips"""
    logger.info("Executing retriever node")
    
    try:
        retrieved_clips = retriever.retrieve_clips(
            search_queries=state["search_queries"],
            available_clips=state["uploaded_clips"]
        )
        
        return {
            **state,
            "retrieved_clips": retrieved_clips,
            "selected_clips": retrieved_clips[:5],  # Select top 5 for MVP
            "current_step": "retrieval_complete", 
            "processing_status": f"Retrieved {len(retrieved_clips)} clips"
        }
        
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        return {
            **state,
            "current_step": "error",
            "error_message": f"Retrieval failed: {str(e)}"
        }

def assembler_node(state: VideoEditingState) -> VideoEditingState:
    """Assembly phase - create final video"""
    logger.info("Executing assembler node")
    
    try:
        # Create assembly configuration
        assembly_config = {
            "preset": state["preset_type"],
            "duration": state.get("custom_duration", 30),
            "theme": state.get("custom_theme", "default")
        }
        
        # Assemble video
        video_url = assembler.assemble_video(
            clips=state["selected_clips"],
            assembly_config=assembly_config
        )
        
        # Create preview
        preview_url = assembler.create_preview(state["selected_clips"])
        
        return {
            **state,
            "final_video_url": video_url,
            "preview_url": preview_url,
            "assembly_config": assembly_config,
            "current_step": "complete",
            "processing_status": "Video created successfully"
        }
        
    except Exception as e:
        logger.error(f"Assembly failed: {e}")
        return {
            **state,
            "current_step": "error", 
            "error_message": f"Assembly failed: {str(e)}"
        }
