"""
Streamlit user interface for the OnDemand Tutor Q&A Agent.
Provides an intuitive web-based interface for interacting with the Q&A system.
"""

import streamlit as st
import os
import sys
from pathlib import Path
from typing import Dict, List
import time

# Add parent directory to path to import modules
current_dir = Path(__file__).parent
src_dir = current_dir.parent
project_root = src_dir.parent
sys.path.append(str(src_dir))

from qa_pipeline import QAPipeline
from config.settings import APP_TITLE, APP_DESCRIPTION, COURSE_MATERIALS_DIR

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'knowledge_base_ready' not in st.session_state:
    st.session_state.knowledge_base_ready = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def initialize_pipeline():
    """Initialize the Q&A pipeline."""
    if st.session_state.pipeline is None:
        with st.spinner("Initializing Q&A system..."):
            st.session_state.pipeline = QAPipeline()

def setup_knowledge_base():
    """Setup the knowledge base from course materials."""
    if st.session_state.pipeline is None:
        initialize_pipeline()
    
    with st.spinner("Setting up knowledge base from course materials..."):
        success = st.session_state.pipeline.setup_knowledge_base()
        st.session_state.knowledge_base_ready = success
        return success

def display_sources(sources: List[Dict], similarity_threshold: float = 0.3):
    """Display source information with academic integrity."""
    if not sources:
        return
    
    st.markdown("### 📚 Sources")
    st.markdown("*For academic integrity, here are the sources used to generate this answer:*")
    
    for i, source in enumerate(sources, 1):
        similarity = source.get('similarity', 0.0)
        file_name = source.get('file', 'Unknown')
        
        # Color code based on similarity
        if similarity > 0.7:
            relevance = "🟢 High"
        elif similarity > similarity_threshold:
            relevance = "🟡 Medium"
        else:
            relevance = "🔴 Low"
        
        with st.expander(f"📄 Source {i}: {file_name} (Relevance: {relevance})"):
            st.write(f"**File:** {file_name}")
            st.write(f"**Similarity Score:** {similarity:.3f}")
            st.write(f"**Chunk Index:** {source.get('chunk_index', 'N/A')}")

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("🎓 " + APP_TITLE)
    st.markdown(f"*{APP_DESCRIPTION}*")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("📋 System Status")
    
    # Initialize pipeline button
    if st.sidebar.button("🔄 Initialize System"):
        initialize_pipeline()
        st.sidebar.success("System initialized!")
    
    # Knowledge base setup
    st.sidebar.markdown("### 📖 Knowledge Base")
    
    if st.sidebar.button("⚙️ Setup Knowledge Base"):
        if setup_knowledge_base():
            st.sidebar.success("Knowledge base ready!")
        else:
            st.sidebar.error("Failed to setup knowledge base. Check course materials.")
    
    # Display knowledge base status
    if st.session_state.pipeline:
        try:
            stats = st.session_state.pipeline.get_knowledge_base_stats()
            db_stats = stats.get('database', {})
            
            if db_stats.get('total_documents', 0) > 0:
                st.sidebar.success(f"📊 {db_stats['total_documents']} documents loaded")
                st.sidebar.info(f"📁 {db_stats['unique_source_files']} source files")
                st.session_state.knowledge_base_ready = True
            else:
                st.sidebar.warning("No documents in knowledge base")
                
        except Exception as e:
            st.sidebar.error(f"Error getting stats: {str(e)}")
    
    # Course materials info
    st.sidebar.markdown("### 📁 Course Materials")
    course_dir = Path(COURSE_MATERIALS_DIR)
    
    if course_dir.exists():
        files = list(course_dir.glob("**/*"))
        supported_files = [f for f in files if f.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']]
        st.sidebar.info(f"📄 {len(supported_files)} supported files found")
    else:
        st.sidebar.warning("Course materials directory not found")
        if st.sidebar.button("📁 Create Directory"):
            course_dir.mkdir(parents=True, exist_ok=True)
            st.sidebar.success("Directory created!")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💭 Ask a Question")
        
        # Question input
        question = st.text_area(
            "Enter your Network Security question:",
            placeholder="e.g., What is a firewall and how does it work?",
            height=100
        )
        
        # Query options
        col_a, col_b = st.columns([1, 1])
        with col_a:
            top_k = st.slider("Number of sources to use:", 1, 10, 5)
        with col_b:
            show_sources = st.checkbox("Show sources", value=True)
        
        # Ask button
        if st.button("🔍 Ask Question", type="primary"):
            if not question.strip():
                st.error("Please enter a question.")
            elif not st.session_state.knowledge_base_ready:
                st.error("Please setup the knowledge base first using the sidebar.")
            else:
                # Process the question
                with st.spinner("Thinking..."):
                    try:
                        result = st.session_state.pipeline.query(question, top_k=top_k)
                        
                        # Display answer
                        st.markdown("### 💡 Answer")
                        
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.markdown(result['answer'])
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                'question': question,
                                'answer': result['answer'],
                                'sources': result['sources'],
                                'timestamp': time.time()
                            })
                            
                            # Display sources
                            if show_sources and result['sources']:
                                display_sources(result['sources'])
                    
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
        
        # Chat history
        if st.session_state.chat_history:
            st.markdown("### 📝 Recent Questions")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history[-5:]), 1):
                with st.expander(f"Q{i}: {chat['question'][:60]}..."):
                    st.markdown("**Question:**")
                    st.write(chat['question'])
                    st.markdown("**Answer:**")
                    st.write(chat['answer'])
                    
                    if chat.get('sources'):
                        st.markdown("**Sources:**")
                        for j, source in enumerate(chat['sources'][:3], 1):
                            st.write(f"{j}. {source.get('file', 'Unknown')} (Score: {source.get('similarity', 0):.3f})")
    
    with col2:
        st.markdown("### ⚙️ System Information")
        
        # System stats
        if st.session_state.pipeline:
            if st.button("📊 Refresh Stats"):
                with st.spinner("Getting system stats..."):
                    try:
                        stats = st.session_state.pipeline.get_knowledge_base_stats()
                        
                        # Database stats
                        db_stats = stats.get('database', {})
                        if db_stats:
                            st.markdown("**📊 Database:**")
                            st.write(f"Documents: {db_stats.get('total_documents', 0)}")
                            st.write(f"Source files: {db_stats.get('unique_source_files', 0)}")
                        
                        # Model info
                        embedding_info = stats.get('embedding_model', {})
                        if embedding_info.get('status') == 'Loaded successfully':
                            st.markdown("**🧠 Embedding Model:**")
                            st.write(f"Model: {embedding_info.get('model_name', 'Unknown')}")
                            st.write(f"Dimensions: {embedding_info.get('embedding_dimension', 'Unknown')}")
                        
                        llm_info = stats.get('language_model', {})
                        if llm_info.get('status') == 'Loaded successfully':
                            st.markdown("**💬 Language Model:**")
                            st.write(f"Model: {llm_info.get('model_name', 'Unknown')}")
                    
                    except Exception as e:
                        st.error(f"Error getting stats: {str(e)}")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
        
        if st.button("🔄 Rebuild Knowledge Base"):
            if st.session_state.pipeline:
                with st.spinner("Rebuilding knowledge base..."):
                    success = st.session_state.pipeline.setup_knowledge_base(force_rebuild=True)
                    if success:
                        st.success("Knowledge base rebuilt!")
                    else:
                        st.error("Failed to rebuild knowledge base")
        
        # Help section
        st.markdown("### ❓ Help")
        with st.expander("How to use"):
            st.markdown("""
            1. **Setup:** Click "Setup Knowledge Base" in the sidebar
            2. **Add Materials:** Place PDF, DOCX, TXT, or MD files in the `data/course_materials/` folder
            3. **Ask Questions:** Type your Network Security questions in the main area
            4. **Review Sources:** Check the sources for academic integrity
            """)
        
        with st.expander("Troubleshooting"):
            st.markdown("""
            - **No documents found:** Add course materials to the `data/course_materials/` directory
            - **Slow responses:** Large knowledge bases take time to process
            - **Poor answers:** Try rephrasing your question or check if relevant materials are loaded
            """)

if __name__ == "__main__":
    main()