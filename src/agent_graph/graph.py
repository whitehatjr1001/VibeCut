"""
LangGraph Workflow Definition
"""
from langgraph.graph import StateGraph, END
from src.agent_graph.state import VideoEditingState
from src.agent_graph.nodes import planner_node, retriever_node, assembler_node
from src.config.logger import logger

def create_video_editing_graph():
    """Create and compile the video editing workflow graph"""
    
    # Initialize graph
    workflow = StateGraph(VideoEditingState)
    
    # Add nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("assembler", assembler_node)
    
    # Define routing logic
    def route_after_planning(state: VideoEditingState) -> str:
        if state["current_step"] == "planning_complete":
            return "retriever"
        else:
            return "error"
    
    def route_after_retrieval(state: VideoEditingState) -> str:
        if state["current_step"] == "retrieval_complete":
            return "assembler"
        else:
            return "error"
    
    def route_after_assembly(state: VideoEditingState) -> str:
        if state["current_step"] == "complete":
            return "end"
        else:
            return "error"
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "planner",
        route_after_planning,
        {"retriever": "retriever", "error": END}
    )
    
    workflow.add_conditional_edges(
        "retriever", 
        route_after_retrieval,
        {"assembler": "assembler", "error": END}
    )
    
    workflow.add_conditional_edges(
        "assembler",
        route_after_assembly, 
        {"end": END, "error": END}
    )
    
    # Set entry point
    workflow.set_entry_point("planner")
    
    # Compile graph
    app = workflow.compile()
    
    logger.info("Video editing graph compiled successfully")
    return app

# Create global graph instance
video_editing_graph = create_video_editing_graph()
