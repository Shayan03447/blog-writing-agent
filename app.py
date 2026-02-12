"""
Streamlit UI for Blog Writing Agent
A beautiful, interactive interface for generating blog posts with AI
"""
import streamlit as st
import sys
import os
from datetime import date, datetime
from pathlib import Path
import traceback
import time
from dotenv import load_dotenv

# Load environment variables from .env file
# Explicitly load from project root to ensure it's found
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Helper function to get env var and strip quotes if present
def get_env_var(key: str) -> str:
    """Get environment variable and strip quotes if present"""
    value = os.getenv(key)
    if value:
        # Strip single or double quotes from start and end
        value = value.strip().strip("'").strip('"')
    return value

# Page config
st.set_page_config(
    page_title="AI Blog Writer",
    page_icon="✍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern, attractive design
st.markdown("""
<style>
    /* Main styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Status cards */
    .status-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .status-card.success {
        border-left-color: #10b981;
    }
    
    .status-card.error {
        border-left-color: #ef4444;
    }
    
    .status-card.warning {
        border-left-color: #f59e0b;
    }
    
    .status-card.info {
        border-left-color: #3b82f6;
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div {
        background-color: #667eea;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    /* Blog preview styling */
    .blog-preview {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        margin-top: 1rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        padding-top: 3rem;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'blog_generated' not in st.session_state:
    st.session_state.blog_generated = False
if 'blog_content' not in st.session_state:
    st.session_state.blog_content = None
if 'blog_title' not in st.session_state:
    st.session_state.blog_title = None
if 'generation_status' not in st.session_state:
    st.session_state.generation_status = None
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'progress' not in st.session_state:
    st.session_state.progress = 0
if 'current_step' not in st.session_state:
    st.session_state.current_step = ""

def display_status_card(status_type, title, message):
    """Display a styled status card"""
    icon_map = {
        "success": "✅",
        "error": "❌",
        "warning": "⚠️",
        "info": "ℹ️"
    }
    st.markdown(f"""
    <div class="status-card {status_type}">
        <h3>{icon_map.get(status_type, '')} {title}</h3>
        <p>{message}</p>
    </div>
    """, unsafe_allow_html=True)

def update_progress(step, progress_value):
    """Update progress bar and current step"""
    st.session_state.current_step = step
    st.session_state.progress = progress_value

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>✍️ AI Blog Writing Agent</h1>
        <p>Generate professional blog posts with AI-powered research, writing, and image generation</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Keys check
        st.subheader("API Keys")
        openai_key = get_env_var("OPENAI_API_KEY")
        tavily_key = get_env_var("TAVILY_API_KEY")
        
        if not openai_key:
            st.error("⚠️ OPENAI_API_KEY not set")
        else:
            st.success("✅ OpenAI API Key configured")
            
        if not tavily_key:
            st.warning("⚠️ TAVILY_API_KEY not set (research will be limited)")
        else:
            st.success("✅ Tavily API Key configured")
        
        st.divider()
        
        # Date configuration
        st.subheader("📅 Date Settings")
        as_of_date = st.date_input(
            "As-of Date",
            value=date.today(),
            help="The reference date for 'latest' or 'this week' queries"
        )
        
        st.divider()
        
        # Advanced settings
        with st.expander("🔧 Advanced Settings"):
            st.info("Default settings are optimized for best results")
            show_debug = st.checkbox("Show Debug Info", value=False)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📝 Blog Topic")
        topic = st.text_input(
            "Enter your blog topic",
            placeholder="e.g., 'Introduction to Python Decorators' or 'Latest AI Developments This Week'",
            label_visibility="collapsed"
        )
        
        if topic:
            st.info(f"📌 Topic: **{topic}**")
    
    with col2:
        st.header("🚀 Generate")
        generate_button = st.button(
            "Generate Blog Post",
            type="primary",
            use_container_width=True
        )
    
    # Generation process
    if generate_button:
        if not topic or not topic.strip():
            st.error("❌ Please enter a blog topic")
            return
        
        # Re-check API key (in case it wasn't loaded in sidebar)
        openai_key = get_env_var("OPENAI_API_KEY")
        if not openai_key:
            st.error("❌ OPENAI_API_KEY is required. Please set it in your .env file.")
            st.info("💡 Make sure your .env file is in the project root and contains: OPENAI_API_KEY=your_key_here")
            return
        
        # Initialize progress
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        try:
            # Import graph (with error handling)
            try:
                from Graph.graph import app
                from state.State import Blog_State
            except ImportError as e:
                st.error(f"❌ Import Error: {str(e)}")
                st.info("💡 Make sure all dependencies are installed: `pip install -r requirements.txt`")
                return
            
            # Initialize state
            initial_state: Blog_State = {
                "topic": topic.strip(),
                "mode": "",
                "needs_research": False,
                "queries": [],
                "evidence": [],
                "plan": None,
                "as_of": as_of_date.isoformat(),
                "recency_days": 3650,
                "sections": [],
                "merged_md": "",
                "md_with_placeholders": "",
                "image_specs": [],
                "final": ""
            }
            
            # Stream the graph execution
            update_progress("Initializing...", 0.05)
            status_placeholder.info("🔄 Initializing blog generation pipeline...")
            progress_bar.progress(5)
            
            # Execute graph with streaming
            final_state = None
            step_count = 0
            total_steps = 6  # router, research (optional), orchestrator, worker, reducer
            
            try:
                # Stream through the graph
                config = {"recursion_limit": 50}
                
                # Router step
                update_progress("Routing...", 0.15)
                status_placeholder.info("🔀 Analyzing topic and determining research needs...")
                progress_bar.progress(15)
                
                # Collect all states from stream
                all_states = []
                for event in app.stream(initial_state, config=config, stream_mode="values"):
                    step_count += 1
                    current_state = event
                    all_states.append(current_state)
                    
                    # Update progress based on state
                    if "needs_research" in current_state and current_state.get("needs_research"):
                        if "evidence" in current_state and current_state.get("evidence"):
                            update_progress("Researching...", 0.35)
                            status_placeholder.info(f"🔍 Researching topic: Found {len(current_state.get('evidence', []))} sources...")
                            progress_bar.progress(35)
                        else:
                            update_progress("Researching...", 0.30)
                            status_placeholder.info("🔍 Conducting web research...")
                            progress_bar.progress(30)
                    
                    if "plan" in current_state and current_state.get("plan"):
                        update_progress("Planning...", 0.50)
                        plan = current_state["plan"]
                        num_tasks = len(plan.tasks) if hasattr(plan, 'tasks') else 0
                        status_placeholder.info(f"📋 Creating blog plan: {num_tasks} sections...")
                        progress_bar.progress(50)
                    
                    if "sections" in current_state and current_state.get("sections"):
                        sections = current_state.get("sections", [])
                        plan = current_state.get("plan")
                        num_tasks = len(plan.tasks) if plan and hasattr(plan, 'tasks') else len(sections)
                        update_progress("Writing...", 0.70)
                        status_placeholder.info(f"✍️ Writing blog sections: {len(sections)}/{num_tasks} completed...")
                        progress_bar.progress(70)
                    
                    if "final" in current_state and current_state.get("final"):
                        update_progress("Finalizing...", 0.95)
                        status_placeholder.success("✨ Blog generation complete!")
                        progress_bar.progress(95)
                        final_state = current_state
                        break
                
                # If no final state found, use the last state
                if not final_state and all_states:
                    final_state = all_states[-1]
                
                # Finalize
                if not final_state or not final_state.get("final"):
                    # Try to get final state from last event
                    final_state = current_state if 'current_state' in locals() else initial_state
                
                progress_bar.progress(100)
                time.sleep(0.5)
                
                # Extract results
                if final_state and final_state.get("final"):
                    st.session_state.blog_content = final_state["final"]
                    st.session_state.blog_title = final_state.get("plan").blog_title if final_state.get("plan") else topic
                    st.session_state.blog_generated = True
                    st.session_state.generation_status = "success"
                    st.rerun()
                else:
                    # Fallback: use merged_md if final is not available
                    if final_state and final_state.get("merged_md"):
                        st.session_state.blog_content = final_state["merged_md"]
                        st.session_state.blog_title = final_state.get("plan").blog_title if final_state.get("plan") else topic
                        st.session_state.blog_generated = True
                        st.session_state.generation_status = "success"
                        st.rerun()
                    else:
                        raise Exception("Blog generation completed but no content was produced")
                        
            except Exception as e:
                error_msg = str(e)
                st.session_state.error_message = error_msg
                st.session_state.generation_status = "error"
                raise
        
        except Exception as e:
            error_msg = f"Error during blog generation: {str(e)}"
            if show_debug:
                error_msg += f"\n\nTraceback:\n{traceback.format_exc()}"
            
            st.session_state.error_message = error_msg
            st.session_state.generation_status = "error"
            display_status_card("error", "Generation Failed", error_msg)
            
            if show_debug:
                with st.expander("🔍 Debug Information"):
                    st.code(traceback.format_exc())
    
    # Display results
    if st.session_state.blog_generated and st.session_state.blog_content:
        st.divider()
        st.header("📄 Generated Blog Post")
        
        # Blog metadata
        if st.session_state.blog_title:
            st.markdown(f"### {st.session_state.blog_title}")
        
        # Download button
        col_dl1, col_dl2 = st.columns([1, 4])
        with col_dl1:
            blog_filename = f"{st.session_state.blog_title.replace(' ', '_').lower()}.md"
            st.download_button(
                label="📥 Download Markdown",
                data=st.session_state.blog_content,
                file_name=blog_filename,
                mime="text/markdown"
            )
        
        # Blog content
        st.markdown("---")
        st.markdown(st.session_state.blog_content)
        
        # Check for images
        images_dir = Path("images")
        if images_dir.exists():
            image_files = list(images_dir.glob("*.png")) + list(images_dir.glob("*.jpg"))
            if image_files:
                st.divider()
                st.subheader("🖼️ Generated Images")
                for img_file in image_files:
                    st.image(str(img_file), caption=img_file.name, use_container_width=True)
    
    # Error display
    if st.session_state.generation_status == "error" and st.session_state.error_message:
        display_status_card("error", "Error", st.session_state.error_message)
    
    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>Powered by LangGraph, OpenAI, and Stable Diffusion</p>
        <p style="font-size: 0.9rem;">Generate professional blog posts with AI assistance</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
