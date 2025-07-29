"""
Streamlit Interface for Video Editing Agent
"""
import streamlit as st
import tempfile
import os
from pathlib import Path
from src.agent_graph.graph import video_editing_graph
from src.agent_graph.state import VideoEditingState
from src.integrations.videodb_client import VideoDBClient
from src.config.logger import logger

# Page config
st.set_page_config(
    page_title="Video Editing Agent",
    page_icon="🎬",
    layout="wide"
)

def initialize_session_state():
    """Initialize Streamlit session state"""
    if "uploaded_clips" not in st.session_state:
        st.session_state.uploaded_clips = []
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "result" not in st.session_state:
        st.session_state.result = None

def upload_section():
    """File upload interface"""
    st.subheader("📤 Upload Your Videos")
    
    uploaded_files = st.file_uploader(
        "Choose video files",
        accept_multiple_files=True,
        type=['mp4', 'avi', 'mov', 'mkv']
    )
    
    if uploaded_files:
        videodb_client = VideoDBClient()
        
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in [clip["name"] for clip in st.session_state.uploaded_clips]:
                # Save temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_path = tmp_file.name
                
                # Upload to VideoDB
                with st.spinner(f"Uploading {uploaded_file.name}..."):
                    clip_id = videodb_client.upload_video(tmp_path)
                    
                st.session_state.uploaded_clips.append({
                    "name": uploaded_file.name,
                    "id": clip_id,
                    "size": uploaded_file.size
                })
                
                # Cleanup
                os.unlink(tmp_path)
        
        # Display uploaded clips
        if st.session_state.uploaded_clips:
            st.success(f"✅ {len(st.session_state.uploaded_clips)} clips uploaded")
            for clip in st.session_state.uploaded_clips:
                st.write(f"• {clip['name']} ({clip['size']} bytes)")

def settings_panel():
    """Video editing settings"""
    st.subheader("⚙️ Settings")
    
    # Preset selection
    preset = st.selectbox(
        "Choose editing preset:",
        ["highlights", "reel", "custom"],
        help="Highlights: Best moments compilation, Reel: Social media format, Custom: Your specifications"
    )
    
    # Custom settings
    custom_duration = None
    custom_theme = None
    
    if preset == "custom":
        custom_duration = st.slider("Video duration (seconds)", 10, 120, 30)
        custom_theme = st.selectbox("Theme", ["professional", "casual", "energetic", "calm"])
    
    return preset, custom_duration, custom_theme

def prompt_interface():
    """User prompt input"""
    st.subheader("💬 Describe Your Video")
    
    prompt = st.text_area(
        "What kind of video do you want to create?",
        placeholder="Create a highlight reel of my presentation with smooth transitions...",
        height=100
    )
    
    # Example prompts
    with st.expander("💡 Example prompts"):
        examples = [
            "Create a professional presentation summary with key talking points",
            "Make an engaging social media reel with dynamic cuts",
            "Compile the best moments with upbeat music and transitions",
            "Create a tutorial video showing step-by-step process"
        ]
        for example in examples:
            if st.button(example, key=f"example_{hash(example)}"):
                st.rerun()
    
    return prompt

def processing_dashboard():
    """Show processing status"""
    if st.session_state.processing:
        st.subheader("🔄 Processing Your Video")
        
        # Progress indicators
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulate progress (replace with actual status from graph)
        import time
        steps = ["Planning video structure...", "Finding relevant clips...", "Assembling final video..."]
        
        for i, step in enumerate(steps):
            status_text.text(step)
            progress_bar.progress((i + 1) / len(steps))
            time.sleep(1)  # Replace with actual processing
        
        status_text.text("✅ Video creation complete!")

def results_section():
    """Display results"""
    if st.session_state.result:
        st.subheader("🎬 Your Video")
        
        result = st.session_state.result
        
        if result.get("final_video_url"):
            st.video(result["final_video_url"])
            
            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    "📥 Download Video",
                    data="placeholder",  # Replace with actual video data
                    file_name="edited_video.mp4",
                    mime="video/mp4"
                )
            with col2:
                if st.button("🔄 Create Another"):
                    st.session_state.result = None
                    st.session_state.processing = False
                    st.rerun()

def main():
    """Main Streamlit application"""
    initialize_session_state()
    
    st.title("🎬 Video Editing Agent")
    st.markdown("Transform your video clips into polished content with AI")
    
    # Main interface
    if not st.session_state.processing and not st.session_state.result:
        # Input phase
        upload_section()
        
        if st.session_state.uploaded_clips:
            preset, custom_duration, custom_theme = settings_panel()
            prompt = prompt_interface()
            
            if st.button("🚀 Create Video", type="primary"):
                if prompt:
                    st.session_state.processing = True
                    
                    # Prepare initial state
                    initial_state = VideoEditingState(
                        user_query=prompt,
                        uploaded_clips=[clip["id"] for clip in st.session_state.uploaded_clips],
                        preset_type=preset,
                        custom_duration=custom_duration,
                        custom_theme=custom_theme,
                        execution_plan=None,
                        search_queries=[],
                        retrieved_clips=[],
                        selected_clips=[],
                        assembly_config=None,
                        final_video_url=None,
                        preview_url=None,
                        current_step="start",
                        processing_status="Initializing...",
                        error_message=None,
                        created_at=None,
                        duration_estimate=None
                    )
                    
                    # Run the graph
                    try:
                        result = video_editing_graph.invoke(initial_state)
                        st.session_state.result = result
                        st.session_state.processing = False
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                        st.session_state.processing = False
                else:
                    st.warning("Please describe what kind of video you want to create!")
        else:
            st.info("👆 Upload some video clips to get started!")
    
    elif st.session_state.processing:
        processing_dashboard()
    
    else:
        results_section()

if __name__ == "__main__":
    main()
