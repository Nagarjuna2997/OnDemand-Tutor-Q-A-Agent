"""
Main Q&A Pipeline for the OnDemand Tutor Q&A Agent.
Orchestrates document processing, embedding, storage, and query processing.
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

try:
    # Try importing dependencies first
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available. Install with: pip install numpy")

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("Warning: sentence-transformers not available. Install with: pip install sentence-transformers")

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("Warning: chromadb not available. Install with: pip install chromadb")

try:
    from gpt4all import GPT4All
    GPT4ALL_AVAILABLE = True
except ImportError:
    GPT4ALL_AVAILABLE = False
    print("Warning: gpt4all not available. Install with: pip install gpt4all")

# Import local modules with error handling
try:
    from config.settings import COURSE_MATERIALS_DIR, PROCESSED_DATA_DIR
except ImportError:
    # Fallback settings if config not found
    COURSE_MATERIALS_DIR = project_root / "data" / "course_materials"
    PROCESSED_DATA_DIR = project_root / "data" / "processed"

class MockEmbeddingManager:
    """Mock embedding manager when dependencies not available."""
    def __init__(self):
        self.available = False
    
    def encode_text(self, text):
        return [0.0] * 384  # Mock embedding
    
    def encode_chunks(self, chunks):
        return []

class MockChromaManager:
    """Mock database manager when dependencies not available."""
    def __init__(self):
        self.available = False
    
    def add_documents(self, chunks):
        return False
    
    def query_similar_documents(self, query_text, query_embedding, top_k=5):
        return []
    
    def get_collection_stats(self):
        return {"total_documents": 0, "unique_source_files": 0}

class MockGPT4AllManager:
    """Mock LLM manager when dependencies not available."""
    def __init__(self):
        self.available = False
    
    def answer_question(self, question, context_chunks):
        return {
            "question": question,
            "answer": "Dependencies not installed. Please run: pip install -r requirements.txt",
            "sources": [],
            "context_used": 0
        }
    
    def get_model_info(self):
        return {"status": "Dependencies not available"}
    
    def cleanup(self):
        pass

class QAPipeline:
    """Main pipeline that orchestrates all components of the Q&A system."""
    
    def __init__(self):
        """Initialize all components of the pipeline."""
        print("Initializing OnDemand Tutor Q&A Pipeline...")
        
        # Check dependencies and initialize accordingly
        self.dependencies_available = all([
            NUMPY_AVAILABLE,
            SENTENCE_TRANSFORMERS_AVAILABLE, 
            CHROMADB_AVAILABLE,
            GPT4ALL_AVAILABLE
        ])
        
        if not self.dependencies_available:
            print("WARNING:  Some dependencies are missing. Using mock components.")
            print("To install all dependencies, run: pip install -r requirements.txt")
            
            # Use mock components
            self.embedding_manager = MockEmbeddingManager()
            self.chroma_manager = MockChromaManager()
            self.llm_manager = MockGPT4AllManager()
            
        else:
            # Import and initialize real components
            try:
                from utils.document_processor import DocumentProcessor
                from embeddings.embedding_manager import EmbeddingManager
                from database.chroma_manager import ChromaManager
                from models.gpt4all_manager import GPT4AllManager
                
                self.document_processor = DocumentProcessor()
                self.embedding_manager = None
                self.chroma_manager = None
                self.llm_manager = None
                
            except ImportError as e:
                print(f"Import error: {e}")
                # Fallback to mock components
                self.embedding_manager = MockEmbeddingManager()
                self.chroma_manager = MockChromaManager()
                self.llm_manager = MockGPT4AllManager()
                self.dependencies_available = False
        
        self.is_initialized = False
    
    def _lazy_init_components(self):
        """Initialize heavy components only when needed."""
        if self.is_initialized or not self.dependencies_available:
            return
        
        print("Loading AI models (this may take a moment)...")
        
        try:
            from embeddings.embedding_manager import EmbeddingManager
            from database.chroma_manager import ChromaManager  
            from models.gpt4all_manager import GPT4AllManager
            
            # Initialize components
            self.embedding_manager = EmbeddingManager()
            self.chroma_manager = ChromaManager()
            self.llm_manager = GPT4AllManager()
            
            self.is_initialized = True
            print("All components initialized successfully!")
            
        except Exception as e:
            print(f"Error initializing components: {e}")
            print("Using mock components instead.")
            self.embedding_manager = MockEmbeddingManager()
            self.chroma_manager = MockChromaManager()
            self.llm_manager = MockGPT4AllManager()
    
    def setup_knowledge_base(self, force_rebuild: bool = False) -> bool:
        """Process course materials and build the knowledge base."""
        print("Setting up knowledge base...")
        
        if not self.dependencies_available:
            print("ERROR: Cannot setup knowledge base - dependencies not available")
            return False
        
        self._lazy_init_components()
        
        # Check if course materials directory exists
        if not Path(COURSE_MATERIALS_DIR).exists():
            print(f"Course materials directory not found: {COURSE_MATERIALS_DIR}")
            print("Please add course materials (PDF, DOCX, TXT, MD files) to this directory")
            Path(COURSE_MATERIALS_DIR).mkdir(parents=True, exist_ok=True)
            return False
        
        # Check for existing files
        files = list(Path(COURSE_MATERIALS_DIR).glob("*"))
        supported_files = [f for f in files if f.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']]
        
        if not supported_files:
            print("No supported files found. Creating sample content...")
            self._create_sample_content()
            # Re-scan for files after creating sample content
            files = list(Path(COURSE_MATERIALS_DIR).glob("*"))
            supported_files = [f for f in files if f.suffix.lower() in ['.pdf', '.docx', '.txt', '.md']]
        
        if not supported_files:
            print("ERROR: No files to process")
            return False
        
        print(f"Found {len(supported_files)} supported files to process")
        
        try:
            import time
            start_time = time.time()

            # Process documents
            print("=" * 60)
            print("STEP 1/3: Processing documents...")
            print("=" * 60)
            chunks = self.document_processor.process_directory(str(COURSE_MATERIALS_DIR))

            if not chunks:
                print("ERROR: No chunks created from documents")
                return False

            print(f"✓ Created {len(chunks)} text chunks")
            step1_time = time.time() - start_time
            print(f"  Time: {step1_time:.1f}s")

            # Encode chunks
            print("\n" + "=" * 60)
            print("STEP 2/3: Encoding chunks with embeddings...")
            print(f"  This may take 2-5 minutes for large documents...")
            print("=" * 60)
            step2_start = time.time()
            encoded_chunks = self.embedding_manager.encode_chunks(chunks)

            if not encoded_chunks:
                print("ERROR: Failed to encode chunks")
                return False

            step2_time = time.time() - step2_start
            print(f"✓ Encoded {len(encoded_chunks)} chunks")
            print(f"  Time: {step2_time:.1f}s")

            # Store in database
            print("\n" + "=" * 60)
            print("STEP 3/3: Storing in vector database...")
            print("=" * 60)
            step3_start = time.time()
            success = self.chroma_manager.add_documents(encoded_chunks)

            if not success:
                print("ERROR: Failed to store documents in database")
                return False

            step3_time = time.time() - step3_start
            total_time = time.time() - start_time

            print(f"✓ Stored successfully")
            print(f"  Time: {step3_time:.1f}s")
            print("\n" + "=" * 60)
            print("✓ KNOWLEDGE BASE SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 60)
            print(f"Total time: {total_time:.1f}s ({total_time/60:.1f} minutes)")

            # Verify storage
            stats = self.chroma_manager.get_collection_stats()
            print(f"Database contains {stats.get('total_documents', 0)} documents from {stats.get('unique_source_files', 0)} files")

            return True
            
        except Exception as e:
            print(f"ERROR during knowledge base setup: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_sample_content(self):
        """Create sample content for testing."""
        sample_content = """# Network Security Basics

## Firewalls
A firewall is a security device that monitors network traffic and blocks unauthorized access based on security rules.

## Encryption  
Encryption converts data into unreadable format to protect it from unauthorized access.

## Common Threats
- Malware: Malicious software
- Phishing: Fraudulent attempts to get sensitive info
- DDoS: Denial of Service attacks
"""
        
        sample_file = Path(COURSE_MATERIALS_DIR) / "sample_content.txt"
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write(sample_content)
        
        print(f"SUCCESS: Created sample content: {sample_file}")
    
    def query(self, question: str, top_k: int = 5) -> Dict[str, any]:
        """Process a user query and return a comprehensive answer."""
        if not question or not question.strip():
            return {
                'question': question,
                'answer': "Please provide a valid question.",
                'sources': [],
                'context_used': 0,
                'error': "Empty question"
            }
        
        if not self.dependencies_available:
            return {
                'question': question,
                'answer': "This system requires additional dependencies to function. Please run: pip install -r requirements.txt",
                'sources': [],
                'context_used': 0,
                'error': "Dependencies not available"
            }
        
        self._lazy_init_components()
        
        try:
            # Encode the question
            print(f"Processing question: {question}")
            question_embedding = self.embedding_manager.encode_text(question)
            
            # Search for similar documents
            print(f"Searching for {top_k} similar documents...")
            similar_docs = self.chroma_manager.query_similar_documents(
                question, question_embedding, top_k=top_k
            )
            
            print(f"Found {len(similar_docs)} similar documents")
            
            if not similar_docs:
                print("No similar documents found")
                return {
                    'question': question,
                    'answer': "I couldn't find relevant information in the knowledge base to answer your question.",
                    'sources': [],
                    'context_used': 0,
                    'retrieved_docs': []
                }
            
            # Prepare context and sources
            context_chunks = []
            sources = []
            
            for doc in similar_docs:
                # Add to context
                context_chunks.append({
                    'content': doc['content'],
                    'metadata': doc['metadata'],
                    'similarity': doc['similarity']
                })
                
                # Create source information for citations
                metadata = doc['metadata']
                source = {
                    'file': metadata.get('source_file', 'Unknown'),
                    'page_number': metadata.get('page_number', (metadata.get('chunk_index', 0) // 3) + 1),
                    'chunk_index': metadata.get('chunk_index', 0),
                    'similarity': doc['similarity'],
                    'content': doc['content'][:500]  # Preview of content
                }
                sources.append(source)
            
            # Generate answer using LLM with context
            print("Generating answer with context...")
            result = self.llm_manager.answer_question(question, context_chunks)
            
            # Add sources to result
            result['sources'] = sources
            result['context_used'] = len(context_chunks)
            result['retrieved_docs'] = similar_docs
            
            print(f"Answer generated with {len(sources)} sources")
            return result
            
        except Exception as e:
            print(f"ERROR during query processing: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                'question': question,
                'answer': f"An error occurred while processing your question: {str(e)}",
                'sources': [],
                'context_used': 0,
                'error': str(e)
            }
    
    def get_knowledge_base_stats(self) -> Dict[str, any]:
        """Get statistics about the current knowledge base."""
        if not self.dependencies_available:
            return {
                'database': {'total_documents': 0, 'unique_source_files': 0},
                'embedding_model': {'status': 'Dependencies not available'},
                'language_model': {'status': 'Dependencies not available'},
                'system_status': 'Dependencies missing'
            }
        
        if hasattr(self, 'chroma_manager') and self.chroma_manager:
            return {
                'database': self.chroma_manager.get_collection_stats(),
                'embedding_model': getattr(self.embedding_manager, 'get_model_info', lambda: {})(),
                'language_model': self.llm_manager.get_model_info(),
                'system_status': 'Ready' if self.is_initialized else 'Not initialized'
            }
        
        return {
            'database': {'total_documents': 0, 'unique_source_files': 0},
            'system_status': 'Not initialized'
        }
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'llm_manager') and self.llm_manager:
            self.llm_manager.cleanup()
        
        print("Pipeline cleanup completed")

# Simple test function
def test_pipeline():
    """Test the pipeline without heavy dependencies."""
    print("Testing Q&A Pipeline...")
    
    pipeline = QAPipeline()
    
    # Test basic query
    result = pipeline.query("What is network security?")
    print(f"Query result: {result['answer'][:100]}...")
    
    # Get stats
    stats = pipeline.get_knowledge_base_stats()
    print(f"System status: {stats['system_status']}")
    
    pipeline.cleanup()
    return True

if __name__ == "__main__":
    test_pipeline()