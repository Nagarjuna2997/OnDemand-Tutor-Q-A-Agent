"""
Citation display components for the Streamlit interface.
Shows detailed source references and citation information.
"""

import streamlit as st
from typing import List, Dict
from pathlib import Path

def display_detailed_sources(sources: List[Dict], similarity_threshold: float = 0.3):
    """Display detailed source information with citations."""
    if not sources:
        return
    
    st.markdown("### 📚 Source References & Citations")
    st.markdown("*For academic integrity, here are the detailed source references:*")
    
    # Group sources by file
    file_groups = {}
    for source in sources:
        file_name = source.get('file', 'Unknown')
        if file_name not in file_groups:
            file_groups[file_name] = []
        file_groups[file_name].append(source)
    
    citation_number = 1
    for file_name, file_sources in file_groups.items():
        st.markdown(f"#### 📄 {file_name}")
        
        for source in file_sources:
            similarity = source.get('similarity', 0.0)
            page_num = source.get('page_number', 'Unknown')
            chunk_index = source.get('chunk_index', 'N/A')
            
            # Color code based on similarity
            if similarity > 0.7:
                relevance_color = "🟢"
                relevance_text = "High Relevance"
            elif similarity > similarity_threshold:
                relevance_color = "🟡" 
                relevance_text = "Medium Relevance"
            else:
                relevance_color = "🔴"
                relevance_text = "Low Relevance"
            
            with st.expander(f"{relevance_color} Citation [{citation_number}]: Page {page_num} ({relevance_text})"):
                
                # Citation information
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("**📖 Citation Details:**")
                    st.write(f"**File:** {file_name}")
                    st.write(f"**Page:** {page_num}")
                    st.write(f"**Chunk:** {chunk_index}")
                    st.write(f"**Relevance:** {similarity:.3f}")
                
                with col2:
                    st.markdown("**📋 Formatted Citations:**")
                    
                    # Generate different citation styles
                    base_name = Path(file_name).stem.replace('_', ' ').title()
                    
                    # APA Style
                    apa_citation = f"{base_name}. (2024). Page {page_num}."
                    st.text_area("APA Style:", apa_citation, height=60, key=f"apa_{citation_number}")
                    
                    # MLA Style  
                    mla_citation = f"{base_name}, p. {page_num}."
                    st.text_area("MLA Style:", mla_citation, height=60, key=f"mla_{citation_number}")
                
                # Show content preview if available
                content = source.get('content', '')
                if content:
                    st.markdown("**📄 Content Preview:**")
                    preview = content[:200] + "..." if len(content) > 200 else content
                    st.text_area("Source Text:", preview, height=100, key=f"content_{citation_number}")
            
            citation_number += 1

def create_bibliography(sources: List[Dict]) -> str:
    """Create a complete bibliography from all sources used."""
    bibliography = []
    seen_files = set()
    
    for source in sources:
        file_name = source.get('file', 'Unknown')
        if file_name not in seen_files:
            base_name = Path(file_name).stem.replace('_', ' ').title()
            
            # Get all pages referenced from this file
            pages = [s.get('page_number', 'Unknown') for s in sources if s.get('file') == file_name]
            unique_pages = sorted(set(pages))
            
            if len(unique_pages) == 1:
                page_text = f"Page {unique_pages[0]}"
            elif len(unique_pages) <= 3:
                page_text = f"Pages {', '.join(map(str, unique_pages))}"
            else:
                page_text = f"Pages {unique_pages[0]}-{unique_pages[-1]}"
            
            bibliography.append(f"{base_name}. (2024). Network Security Course Material. {page_text}.")
            seen_files.add(file_name)
    
    return '\n\n'.join(bibliography)

def display_citation_export(sources: List[Dict]):
    """Display citation export options."""
    if not sources:
        return
    
    st.markdown("### 📤 Export Citations")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("📋 Copy APA Citations"):
            bibliography = create_bibliography(sources)
            st.code(bibliography, language='text')
    
    with col2:
        if st.button("📝 Generate Bibliography"):
            bib = create_bibliography(sources)
            st.text_area("Complete Bibliography:", bib, height=150)
    
    with col3:
        if st.button("💾 Download Citations"):
            bib = create_bibliography(sources)
            st.download_button(
                label="Download as .txt",
                data=bib,
                file_name="citations.txt",
                mime="text/plain"
            )

def show_citation_summary(sources: List[Dict]):
    """Show a summary of citation information."""
    if not sources:
        return
    
    # Count unique files and pages
    files = set(s.get('file', 'Unknown') for s in sources)
    pages = set(s.get('page_number', 'Unknown') for s in sources if s.get('page_number') != 'Unknown')
    
    # Average relevance
    similarities = [s.get('similarity', 0.0) for s in sources]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    
    st.markdown("#### 📊 Citation Summary")
    
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        st.metric("📚 Files Referenced", len(files))
    
    with col2:
        st.metric("📄 Pages Cited", len(pages))
    
    with col3:
        st.metric("🔗 Total Citations", len(sources))
    
    with col4:
        st.metric("📈 Avg. Relevance", f"{avg_similarity:.2f}")
    
    # List files referenced
    if files:
        st.markdown("**Files Referenced:**")
        for file_name in sorted(files):
            file_pages = sorted(set(s.get('page_number', 'Unknown') for s in sources 
                                  if s.get('file') == file_name and s.get('page_number') != 'Unknown'))
            if file_pages:
                pages_text = f"Pages: {', '.join(map(str, file_pages[:5]))}"
                if len(file_pages) > 5:
                    pages_text += f" (and {len(file_pages)-5} more)"
                st.write(f"• **{file_name}** - {pages_text}")
            else:
                st.write(f"• **{file_name}**")