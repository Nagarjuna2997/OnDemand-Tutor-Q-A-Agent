"""
Enhanced document processor with detailed citation tracking.
Adds page numbers, sections, and precise source referencing.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import PyPDF2
import docx
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP, SUPPORTED_FILE_TYPES

class EnhancedDocumentProcessor:
    """Enhanced document processor with detailed citation tracking."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def extract_pdf_with_pages(self, file_path: str) -> List[Dict[str, any]]:
        """Extract text from PDF with page-by-page tracking for citations."""
        pages_data = []
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"Processing PDF: {total_pages} pages")
                
                for page_num, page in enumerate(pdf_reader.pages, 1):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():  # Only process pages with content
                            pages_data.append({
                                'page_number': page_num,
                                'text': page_text,
                                'char_count': len(page_text),
                                'word_count': len(page_text.split())
                            })
                    except Exception as e:
                        print(f"Error processing page {page_num}: {e}")
                        continue
                
                print(f"Successfully processed {len(pages_data)} pages with content")
                
        except Exception as e:
            print(f"Error reading PDF: {e}")
        
        return pages_data
    
    def create_chunks_with_citations(self, pages_data: List[Dict], file_metadata: Dict) -> List[Dict]:
        """Create text chunks while preserving page number citations."""
        chunks = []
        chunk_id = 0
        
        for page_data in pages_data:
            page_num = page_data['page_number']
            page_text = page_data['text']
            
            # Clean the page text
            cleaned_text = self.clean_text(page_text)
            
            # If page text fits in one chunk, create single chunk
            words = cleaned_text.split()
            if len(words) <= self.chunk_size:
                chunk_metadata = file_metadata.copy()
                chunk_metadata.update({
                    'page_number': page_num,
                    'page_start': page_num,
                    'page_end': page_num,
                    'chunk_index': chunk_id,
                    'word_count': len(words),
                    'char_count': len(cleaned_text)
                })
                
                chunks.append({
                    'content': cleaned_text,
                    'metadata': chunk_metadata,
                    'chunk_index': chunk_id,
                    'citation': f"Page {page_num}"
                })
                
                chunk_id += 1
            
            else:
                # Split page into multiple chunks with overlap
                start_idx = 0
                while start_idx < len(words):
                    end_idx = min(start_idx + self.chunk_size, len(words))
                    chunk_words = words[start_idx:end_idx]
                    chunk_text = ' '.join(chunk_words)
                    
                    chunk_metadata = file_metadata.copy()
                    chunk_metadata.update({
                        'page_number': page_num,
                        'page_start': page_num,
                        'page_end': page_num,
                        'chunk_index': chunk_id,
                        'word_count': len(chunk_words),
                        'char_count': len(chunk_text),
                        'chunk_start_word': start_idx,
                        'chunk_end_word': end_idx
                    })
                    
                    chunks.append({
                        'content': chunk_text,
                        'metadata': chunk_metadata,
                        'chunk_index': chunk_id,
                        'citation': f"Page {page_num} (Part {chunk_id - len([c for c in chunks if c['metadata']['page_number'] < page_num]) + 1})"
                    })
                    
                    chunk_id += 1
                    start_idx = end_idx - self.chunk_overlap
        
        return chunks
    
    def clean_text(self, text: str) -> str:
        """Enhanced text cleaning for better citations."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix common PDF extraction issues
        text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add spaces between camelCase
        text = re.sub(r'([.!?])([A-Z])', r'\1 \2', text)  # Add spaces after punctuation
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\[\]{}"\'/]', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def detect_sections(self, text: str) -> List[str]:
        """Detect section headers for better citations."""
        sections = []
        
        # Common patterns for section headers
        patterns = [
            r'^(Chapter \d+[:\.]?\s*[A-Z].*)',
            r'^(\d+\.\d*\s+[A-Z].*)',
            r'^([A-Z][A-Z\s]{10,})',  # ALL CAPS headers
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*:)',  # Title Case with colon
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if len(line) > 5 and len(line) < 100:  # Reasonable header length
                for pattern in patterns:
                    if re.match(pattern, line):
                        sections.append(line)
                        break
        
        return sections
    
    def process_pdf_with_enhanced_citations(self, file_path: str) -> List[Dict]:
        """Process PDF with comprehensive citation information."""
        print(f"Processing PDF with enhanced citations: {Path(file_path).name}")
        
        # Extract pages with tracking
        pages_data = self.extract_pdf_with_pages(file_path)
        if not pages_data:
            return []
        
        # Create file metadata
        file_path_obj = Path(file_path)
        file_metadata = {
            'source_file': file_path_obj.name,
            'file_path': str(file_path),
            'file_type': file_path_obj.suffix.lower(),
            'file_size': os.path.getsize(file_path),
            'total_pages': len(pages_data),
            'total_word_count': sum(p['word_count'] for p in pages_data),
            'total_char_count': sum(p['char_count'] for p in pages_data)
        }
        
        # Create chunks with enhanced citations
        chunks = self.create_chunks_with_citations(pages_data, file_metadata)
        
        # Add section information where possible
        for chunk in chunks:
            page_text = next((p['text'] for p in pages_data if p['page_number'] == chunk['metadata']['page_number']), '')
            sections = self.detect_sections(page_text)
            if sections:
                chunk['metadata']['sections'] = sections
                chunk['citation'] += f" (Section: {sections[0][:50]}...)"
        
        print(f"Created {len(chunks)} chunks with enhanced citations")
        return chunks
    
    def generate_citation_text(self, chunk_metadata: Dict, style: str = 'apa') -> str:
        """Generate properly formatted citation text."""
        file_name = chunk_metadata.get('source_file', 'Unknown')
        page_num = chunk_metadata.get('page_number', 'Unknown')
        sections = chunk_metadata.get('sections', [])
        
        if style.lower() == 'apa':
            # APA style citation
            base_name = Path(file_name).stem.replace('_', ' ').title()
            citation = f"{base_name}. Page {page_num}."
            if sections:
                citation += f" Section: {sections[0]}."
        
        elif style.lower() == 'mla':
            # MLA style citation
            base_name = Path(file_name).stem.replace('_', ' ').title()
            citation = f"{base_name}, p. {page_num}."
        
        else:  # Simple style
            citation = f"{file_name}, Page {page_num}"
            if sections:
                citation += f", {sections[0]}"
        
        return citation
    
    def export_citations(self, chunks_used: List[Dict], format: str = 'text') -> str:
        """Export citations for all sources used in an answer."""
        citations = []
        seen_sources = set()
        
        for chunk in chunks_used:
            source_key = (chunk['metadata']['source_file'], chunk['metadata']['page_number'])
            if source_key not in seen_sources:
                citation = self.generate_citation_text(chunk['metadata'])
                citations.append(citation)
                seen_sources.add(source_key)
        
        if format.lower() == 'json':
            import json
            return json.dumps(citations, indent=2)
        elif format.lower() == 'markdown':
            return '\n'.join(f"- {citation}" for citation in citations)
        else:  # text format
            return '\n'.join(citations)