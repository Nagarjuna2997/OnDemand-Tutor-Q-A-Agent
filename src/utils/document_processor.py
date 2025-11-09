"""
Document processing utilities for the OnDemand Tutor Q&A Agent.
Handles reading, chunking, and preprocessing of course materials.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple
import PyPDF2
import docx
from config.settings import (
    CHUNK_SIZE, 
    CHUNK_OVERLAP, 
    SUPPORTED_FILE_TYPES,
    COURSE_MATERIALS_DIR
)

class DocumentProcessor:
    """Processes course materials for vector embedding and storage."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def read_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error reading PDF {file_path}: {str(e)}")
        return text
    
    def read_docx(self, file_path: str) -> str:
        """Extract text from Word document."""
        text = ""
        try:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            print(f"Error reading DOCX {file_path}: {str(e)}")
        return text
    
    def read_text_file(self, file_path: str) -> str:
        """Read plain text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {str(e)}")
            return ""
    
    def read_document(self, file_path: str) -> str:
        """Read document based on file extension."""
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self.read_pdf(file_path)
        elif file_ext == '.docx':
            return self.read_docx(file_path)
        elif file_ext in ['.txt', '.md']:
            return self.read_text_file(file_path)
        else:
            print(f"Unsupported file type: {file_ext}")
            return ""
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\[\]{}"]', ' ', text)
        
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, metadata: Dict[str, str]) -> List[Dict[str, str]]:
        """Split text into chunks with overlap for better context preservation."""
        chunks = []
        words = text.split()
        
        if len(words) <= self.chunk_size:
            chunks.append({
                'content': text,
                'metadata': metadata,
                'chunk_index': 0
            })
            return chunks
        
        chunk_index = 0
        start_idx = 0
        
        while start_idx < len(words):
            end_idx = min(start_idx + self.chunk_size, len(words))
            chunk_words = words[start_idx:end_idx]
            chunk_text = ' '.join(chunk_words)
            
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = chunk_index
            chunk_metadata['start_word'] = start_idx
            chunk_metadata['end_word'] = end_idx
            
            chunks.append({
                'content': chunk_text,
                'metadata': chunk_metadata,
                'chunk_index': chunk_index
            })
            
            # Move start index with overlap
            start_idx = end_idx - self.chunk_overlap
            chunk_index += 1
        
        return chunks
    
    def process_single_file(self, file_path: str) -> List[Dict[str, str]]:
        """Process a single file and return chunks with metadata."""
        print(f"Processing file: {file_path}")
        
        # Extract text
        raw_text = self.read_document(file_path)
        if not raw_text.strip():
            print(f"No content extracted from {file_path}")
            return []
        
        # Clean text
        cleaned_text = self.clean_text(raw_text)
        
        # Create metadata
        file_path_obj = Path(file_path)
        metadata = {
            'source_file': file_path_obj.name,
            'file_path': str(file_path),
            'file_type': file_path_obj.suffix.lower(),
            'file_size': os.path.getsize(file_path),
            'content_length': len(cleaned_text)
        }
        
        # Chunk the text
        chunks = self.chunk_text(cleaned_text, metadata)
        
        print(f"Created {len(chunks)} chunks from {file_path_obj.name}")
        return chunks
    
    def process_directory(self, directory_path: str = None) -> List[Dict[str, str]]:
        """Process all supported files in the course materials directory."""
        if directory_path is None:
            directory_path = COURSE_MATERIALS_DIR
        
        directory = Path(directory_path)
        if not directory.exists():
            print(f"Directory not found: {directory_path}")
            return []
        
        all_chunks = []
        processed_files = 0
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FILE_TYPES:
                chunks = self.process_single_file(str(file_path))
                all_chunks.extend(chunks)
                processed_files += 1
        
        print(f"Processed {processed_files} files, created {len(all_chunks)} total chunks")
        return all_chunks
    
    def get_document_stats(self, chunks: List[Dict[str, str]]) -> Dict[str, int]:
        """Get statistics about processed documents."""
        if not chunks:
            return {}
        
        total_chunks = len(chunks)
        unique_files = len(set(chunk['metadata']['source_file'] for chunk in chunks))
        total_content_length = sum(len(chunk['content']) for chunk in chunks)
        
        file_types = {}
        for chunk in chunks:
            file_type = chunk['metadata']['file_type']
            file_types[file_type] = file_types.get(file_type, 0) + 1
        
        return {
            'total_chunks': total_chunks,
            'unique_files': unique_files,
            'total_content_length': total_content_length,
            'avg_chunk_length': total_content_length // total_chunks if total_chunks > 0 else 0,
            'file_types': file_types
        }