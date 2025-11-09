"""
Simple Streamlit interface for OnDemand Tutor Q&A Agent without Unicode issues.
"""

import streamlit as st
import os
import sys
from pathlib import Path
import time

# Add parent directory to path to import modules
current_dir = Path(__file__).parent
src_dir = current_dir.parent
project_root = src_dir.parent
sys.path.append(str(src_dir))

from qa_pipeline import QAPipeline

# Page configuration
st.set_page_config(
    page_title="OnDemand Tutor Q&A Agent",
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
        try:
            success = st.session_state.pipeline.setup_knowledge_base()
            st.session_state.knowledge_base_ready = success
            return success
        except Exception as e:
            st.error(f"Error setting up knowledge base: {str(e)}")
            return False

def main():
    """Main Streamlit application."""
    
    # Header
    st.title("OnDemand Tutor Q&A Agent")
    st.markdown("*Network Security Course Assistant*")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("System Status")
    
    # Initialize pipeline button
    if st.sidebar.button("Initialize System"):
        initialize_pipeline()
        st.sidebar.success("System initialized!")
    
    # Knowledge base setup
    st.sidebar.markdown("### Knowledge Base")
    
    if st.sidebar.button("Setup Knowledge Base"):
        if setup_knowledge_base():
            st.sidebar.success("Knowledge base ready!")
        else:
            st.sidebar.error("Failed to setup knowledge base.")
    
    # Display knowledge base status
    if st.session_state.pipeline:
        try:
            stats = st.session_state.pipeline.get_knowledge_base_stats()
            db_stats = stats.get('database', {})
            
            if db_stats.get('total_documents', 0) > 0:
                st.sidebar.success(f"Documents: {db_stats['total_documents']}")
                st.sidebar.info(f"Files: {db_stats['unique_source_files']}")
                st.session_state.knowledge_base_ready = True
            else:
                st.sidebar.warning("No documents in knowledge base")
                
        except Exception as e:
            st.sidebar.error(f"Error getting stats: {str(e)}")
    
    # Course materials info
    st.sidebar.markdown("### Course Materials")
    course_dir = Path("data/course_materials")
    
    if course_dir.exists():
        files = list(course_dir.glob("**/*"))
        supported_files = [f for f in files if f.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']]
        st.sidebar.info(f"Files found: {len(supported_files)}")
        
        # Show files
        for f in supported_files[:5]:  # Show first 5 files
            st.sidebar.text(f.name)
    else:
        st.sidebar.warning("Course materials directory not found")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Ask a Question")
        
        # Question input
        question = st.text_area(
            "Enter your Network Security question:",
            placeholder="e.g., What is a firewall and how does it work?",
            height=100
        )
        
        # Query options
        col_a, col_b = st.columns([1, 1])
        with col_a:
            top_k = st.slider("Number of sources:", 1, 10, 5)
        with col_b:
            show_sources = st.checkbox("Show sources", value=True)
        
        # Ask button
        if st.button("Ask Question", type="primary"):
            if not question.strip():
                st.error("Please enter a question.")
            else:
                if st.session_state.pipeline is None:
                    initialize_pipeline()
                
                # Process the question
                with st.spinner("Thinking..."):
                    try:
                        result = st.session_state.pipeline.query(question, top_k=top_k)
                        
                        # Display answer
                        st.markdown("### Answer")
                        
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.markdown(result['answer'])
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                'question': question,
                                'answer': result['answer'],
                                'sources': result.get('sources', []),
                                'timestamp': time.time()
                            })
                            
                            # Display sources
                            if show_sources and result.get('sources'):
                                st.markdown("### Sources")
                                st.markdown("*For academic integrity, here are the sources:*")
                                
                                for i, source in enumerate(result['sources'], 1):
                                    file_name = source.get('file', 'Unknown')
                                    similarity = source.get('similarity', 0.0)
                                    
                                    with st.expander(f"Source {i}: {file_name}"):
                                        st.write(f"**File:** {file_name}")
                                        st.write(f"**Similarity:** {similarity:.3f}")
                                        st.write(f"**Chunk:** {source.get('chunk_index', 'N/A')}")
                    
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
        
        # Chat history
        if st.session_state.chat_history:
            st.markdown("### Recent Questions")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history[-3:]), 1):
                with st.expander(f"Q{i}: {chat['question'][:50]}..."):
                    st.markdown("**Question:**")
                    st.write(chat['question'])
                    st.markdown("**Answer:**")
                    st.write(chat['answer'][:200] + "..." if len(chat['answer']) > 200 else chat['answer'])
    
    with col2:
        st.markdown("### System Information")
        
        # System stats
        if st.session_state.pipeline:
            if st.button("Refresh Stats"):
                with st.spinner("Getting stats..."):
                    try:
                        stats = st.session_state.pipeline.get_knowledge_base_stats()
                        
                        # Database stats
                        db_stats = stats.get('database', {})
                        if db_stats:
                            st.markdown("**Database:**")
                            st.write(f"Documents: {db_stats.get('total_documents', 0)}")
                            st.write(f"Files: {db_stats.get('unique_source_files', 0)}")
                        
                        # System status
                        system_status = stats.get('system_status', 'Unknown')
                        st.markdown(f"**Status:** {system_status}")
                    
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        # Quick actions
        st.markdown("### Quick Actions")
        
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
        
        # Help section
        st.markdown("### Help")
        with st.expander("How to use"):
            st.markdown("""
            1. **Initialize:** Click "Initialize System"
            2. **Setup:** Click "Setup Knowledge Base" 
            3. **Ask:** Type your questions
            4. **Review:** Check sources for references
            """)
        
        with st.expander("Course Materials"):
            st.markdown("""
            - Add PDF, DOCX, TXT, MD files to data/course_materials/
            - Currently supports Network Security content
            - Sources are cited for academic integrity
            """)

if __name__ == "__main__":
    main()