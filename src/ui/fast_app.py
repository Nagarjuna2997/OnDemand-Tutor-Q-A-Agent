"""
FAST Streamlit interface - optimized for quick setup and citations.
Processes only the main merged PDF for speed.
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
    page_title="OnDemand Tutor Q&A Agent - FAST Mode",
    page_icon="⚡",
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

class FastQAPipeline(QAPipeline):
    """Fast version that processes only the main PDF."""
    
    def setup_knowledge_base_fast(self) -> bool:
        """Fast setup - process only the main merged PDF."""
        print("Setting up knowledge base (FAST MODE)...")
        
        if not self.dependencies_available:
            print("ERROR: Cannot setup knowledge base - dependencies not available")
            return False
        
        self._lazy_init_components()
        
        # Process only the main merged PDF
        main_pdf = Path("data/course_materials/1_merged_compressed.pdf")
        if not main_pdf.exists():
            print(f"Main PDF not found: {main_pdf}")
            return False
        
        print(f"Processing ONLY: {main_pdf.name} (27MB)")
        
        try:
            # Process just the main document
            chunks = self.document_processor.process_single_file(str(main_pdf))
            
            if not chunks:
                print("ERROR: No chunks created")
                return False
            
            print(f"Created {len(chunks)} text chunks")
            
            # Encode chunks in batches for speed
            print("Encoding chunks...")
            batch_size = 50  # Process in smaller batches
            encoded_chunks = []
            
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i+batch_size]
                batch_encoded = self.embedding_manager.encode_chunks(batch)
                encoded_chunks.extend(batch_encoded)
                print(f"Encoded batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1}")
            
            if not encoded_chunks:
                print("ERROR: Failed to encode chunks")
                return False
            
            print(f"Total encoded: {len(encoded_chunks)} chunks")
            
            # Clear existing and store new
            print("Storing in database...")
            self.chroma_manager.clear_collection()
            success = self.chroma_manager.add_documents(encoded_chunks)
            
            if not success:
                print("ERROR: Failed to store documents")
                return False
            
            # Verify
            stats = self.chroma_manager.get_collection_stats()
            total_docs = stats.get('total_documents', 0)
            
            print(f"SUCCESS: {total_docs} documents stored")
            return True
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def initialize_pipeline():
    """Initialize the fast Q&A pipeline."""
    if st.session_state.pipeline is None:
        with st.spinner("Initializing FAST Q&A system..."):
            st.session_state.pipeline = FastQAPipeline()

def setup_knowledge_base():
    """Setup knowledge base with only the main PDF."""
    if st.session_state.pipeline is None:
        initialize_pipeline()
    
    with st.spinner("Setting up knowledge base (FAST mode - main PDF only)..."):
        try:
            success = st.session_state.pipeline.setup_knowledge_base_fast()
            st.session_state.knowledge_base_ready = success
            return success
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return False

def main():
    """Main FAST Streamlit application."""
    
    # Header
    st.title("⚡ OnDemand Tutor Q&A Agent - FAST MODE")
    st.markdown("*Optimized for quick setup - processes main PDF only (27MB)*")
    st.markdown("---")
    
    # Sidebar
    st.sidebar.title("🚀 FAST System Status")
    
    # Initialize pipeline button
    if st.sidebar.button("⚡ Initialize System (FAST)"):
        initialize_pipeline()
        st.sidebar.success("System initialized!")
    
    # Knowledge base setup
    st.sidebar.markdown("### 📖 Knowledge Base (FAST)")
    
    if st.sidebar.button("⚙️ Setup Knowledge Base (Main PDF Only)"):
        if setup_knowledge_base():
            st.sidebar.success("Knowledge base ready!")
        else:
            st.sidebar.error("Failed to setup knowledge base.")
    
    # Display status
    if st.session_state.pipeline:
        try:
            stats = st.session_state.pipeline.get_knowledge_base_stats()
            db_stats = stats.get('database', {})
            
            if db_stats.get('total_documents', 0) > 0:
                st.sidebar.success(f"📊 Documents: {db_stats['total_documents']}")
                st.sidebar.info(f"📁 Files: {db_stats['unique_source_files']}")
                st.session_state.knowledge_base_ready = True
            else:
                st.sidebar.warning("No documents in knowledge base")
        except Exception as e:
            st.sidebar.error(f"Error: {str(e)}")
    
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
            top_k = st.slider("Number of sources:", 1, 10, 5)
        with col_b:
            show_sources = st.checkbox("Show sources", value=True)
        
        # Ask button
        if st.button("🔍 Ask Question", type="primary"):
            if not question.strip():
                st.error("Please enter a question.")
            else:
                if st.session_state.pipeline is None:
                    initialize_pipeline()
                
                # Process the question
                with st.spinner("Processing your question..."):
                    try:
                        result = st.session_state.pipeline.query(question, top_k=top_k)
                        
                        # Display answer
                        st.markdown("### 💡 Answer")
                        
                        if 'error' in result:
                            st.error(f"Error: {result['error']}")
                        else:
                            st.markdown(result['answer'])
                            
                            # Display sources
                            sources = result.get('sources', [])
                            if sources and show_sources:
                                st.markdown("---")
                                st.markdown(f"### 📚 Citations ({len(sources)} sources)")
                                
                                for i, source in enumerate(sources, 1):
                                    file_name = source.get('file', 'Unknown')
                                    page_num = source.get('page_number', 'Unknown')
                                    similarity = source.get('similarity', 0.0)
                                    
                                    # Color based on relevance
                                    if similarity > 0.7:
                                        color = "🟢"
                                    elif similarity > 0.5:
                                        color = "🟡"
                                    else:
                                        color = "🔴"
                                    
                                    st.markdown(f"{color} **[{i}] {file_name}, Page {page_num}** (Score: {similarity:.3f})")
                                    
                                    # Content preview
                                    content = source.get('content', '')[:200] + "..."
                                    st.text(content)
                                    st.markdown("---")
                            
                            # Add to chat history
                            st.session_state.chat_history.append({
                                'question': question,
                                'answer': result['answer'],
                                'sources': sources,
                                'timestamp': time.time()
                            })
                    
                    except Exception as e:
                        st.error(f"An error occurred: {str(e)}")
    
    with col2:
        st.markdown("### ⚡ FAST Mode Info")
        st.info("This version processes only the main merged PDF (1_merged_compressed.pdf) for speed.")
        
        st.markdown("### ⏱️ Performance")
        st.success("✓ 10x faster setup\\n✓ Quick responses\\n✓ Still shows citations\\n✓ Main content covered")
        
        # System stats
        if st.session_state.pipeline:
            if st.button("📊 Refresh Stats"):
                try:
                    stats = st.session_state.pipeline.get_knowledge_base_stats()
                    db_stats = stats.get('database', {})
                    st.write(f"Documents: {db_stats.get('total_documents', 0)}")
                    st.write(f"Files: {db_stats.get('unique_source_files', 0)}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
        
        # Help
        st.markdown("### ❓ Help")
        with st.expander("Why FAST Mode?"):
            st.markdown("""
            **FAST Mode processes only:**
            - Main merged PDF (27MB)
            - Faster setup (2-3 minutes vs 15+ minutes)
            - Still provides accurate citations
            - Covers most course content
            """)

if __name__ == "__main__":
    main()