"""
Main Q&A Pipeline for the OnDemand Tutor Q&A Agent.
Orchestrates document processing, embedding, storage, and query processing.
"""

import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path

from utils.document_processor import DocumentProcessor
from embeddings.embedding_manager import EmbeddingManager
from database.chroma_manager import ChromaManager
from models.gpt4all_manager import GPT4AllManager
from config.settings import COURSE_MATERIALS_DIR, PROCESSED_DATA_DIR

class QAPipeline:
    """Main pipeline that orchestrates all components of the Q&A system."""
    
    def __init__(self):
        """Initialize all components of the pipeline."""
        print("Initializing OnDemand Tutor Q&A Pipeline...")
        
        self.document_processor = DocumentProcessor()
        self.embedding_manager = None
        self.chroma_manager = None
        self.llm_manager = None
        self.is_initialized = False
        
        # Initialize components lazily to avoid long startup times
    
    def _lazy_init_components(self):
        """Initialize heavy components only when needed."""
        if self.is_initialized:
            return
        
        print("Loading AI models (this may take a moment)...")
        
        # Initialize embedding manager
        self.embedding_manager = EmbeddingManager()
        
        # Initialize database manager
        self.chroma_manager = ChromaManager()
        
        # Initialize LLM manager
        self.llm_manager = GPT4AllManager()
        
        self.is_initialized = True
        print("All components initialized successfully!")
    
    def setup_knowledge_base(self, force_rebuild: bool = False) -> bool:
        """Process course materials and build the knowledge base."""
        print("Setting up knowledge base...")
        
        self._lazy_init_components()
        
        # Check if knowledge base already exists
        stats = self.chroma_manager.get_collection_stats()
        if not force_rebuild and stats.get('total_documents', 0) > 0:
            print(f"Knowledge base already exists with {stats['total_documents']} documents")
            return True
        
        # Check if course materials directory exists
        if not Path(COURSE_MATERIALS_DIR).exists():
            print(f"Course materials directory not found: {COURSE_MATERIALS_DIR}")
            print("Please add course materials (PDF, DOCX, TXT, MD files) to this directory")
            Path(COURSE_MATERIALS_DIR).mkdir(parents=True, exist_ok=True)
            return False
        
        # Process documents
        print("Processing course materials...")
        chunks = self.document_processor.process_directory(COURSE_MATERIALS_DIR)
        
        if not chunks:
            print("No documents found or processed")
            return False
        
        # Generate embeddings
        print("Generating embeddings...")
        encoded_chunks = self.embedding_manager.encode_chunks(chunks)
        
        if not encoded_chunks:
            print("Failed to generate embeddings")
            return False
        
        # Clear existing data if force rebuild
        if force_rebuild:
            print("Clearing existing knowledge base...")
            self.chroma_manager.clear_collection()
        
        # Store in database
        print("Storing embeddings in vector database...")
        success = self.chroma_manager.add_documents(encoded_chunks)
        
        if success:
            # Print statistics
            doc_stats = self.document_processor.get_document_stats(chunks)
            print(f"\nKnowledge base setup complete!")
            print(f"- Processed {doc_stats['unique_files']} files")
            print(f"- Created {doc_stats['total_chunks']} text chunks")
            print(f"- Generated {len(encoded_chunks)} embeddings")
            
            return True
        else:
            print("Failed to store embeddings in database")
            return False
    
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
        
        self._lazy_init_components()
        
        try:
            # Generate embedding for the question
            question_embedding = self.embedding_manager.encode_text(question)
            
            # Search for relevant documents
            similar_docs = self.chroma_manager.query_similar_documents(
                query_text=question,
                query_embedding=question_embedding.tolist(),
                top_k=top_k
            )
            
            if not similar_docs:
                return {
                    'question': question,
                    'answer': "I couldn't find relevant information in the course materials to answer your question. Please check if the course materials have been loaded properly.",
                    'sources': [],
                    'context_used': 0,
                    'error': "No relevant documents found"
                }
            
            # Generate answer using LLM
            answer_result = self.llm_manager.answer_question(question, similar_docs)
            
            # Add similarity scores to sources
            for i, source in enumerate(answer_result['sources']):
                if i < len(similar_docs):
                    source['similarity'] = similar_docs[i]['similarity']
                    source['distance'] = similar_docs[i]['distance']
            
            answer_result['retrieved_docs'] = similar_docs
            
            return answer_result
            
        except Exception as e:
            print(f"Error processing query: {str(e)}")
            return {
                'question': question,
                'answer': f"I encountered an error while processing your question: {str(e)}",
                'sources': [],
                'context_used': 0,
                'error': str(e)
            }
    
    def explain_concept(self, concept: str, top_k: int = 3) -> str:
        """Provide an explanation for a specific concept."""
        self._lazy_init_components()
        
        try:
            # Search for relevant context about the concept
            concept_embedding = self.embedding_manager.encode_text(concept)
            similar_docs = self.chroma_manager.query_similar_documents(
                query_text=concept,
                query_embedding=concept_embedding.tolist(),
                top_k=top_k
            )
            
            if not similar_docs:
                return f"I couldn't find information about '{concept}' in the course materials."
            
            # Generate explanation
            explanation = self.llm_manager.explain_concept(concept, similar_docs)
            
            return explanation
            
        except Exception as e:
            print(f"Error explaining concept: {str(e)}")
            return f"I encountered an error while explaining '{concept}': {str(e)}"
    
    def get_knowledge_base_stats(self) -> Dict[str, any]:
        """Get statistics about the current knowledge base."""
        if not self.is_initialized:
            self._lazy_init_components()
        
        try:
            # Get database stats
            db_stats = self.chroma_manager.get_collection_stats()
            
            # Get embedding model info
            embedding_info = self.embedding_manager.get_model_info()
            
            # Get LLM info
            llm_info = self.llm_manager.get_model_info()
            
            return {
                'database': db_stats,
                'embedding_model': embedding_info,
                'language_model': llm_info,
                'system_status': 'Ready' if self.is_initialized else 'Not initialized'
            }
            
        except Exception as e:
            print(f"Error getting stats: {str(e)}")
            return {'error': str(e)}
    
    def search_documents(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search for documents without generating an answer."""
        if not self.is_initialized:
            self._lazy_init_components()
        
        try:
            query_embedding = self.embedding_manager.encode_text(query)
            similar_docs = self.chroma_manager.query_similar_documents(
                query_text=query,
                query_embedding=query_embedding.tolist(),
                top_k=top_k
            )
            
            return similar_docs
            
        except Exception as e:
            print(f"Error searching documents: {str(e)}")
            return []
    
    def add_document(self, file_path: str) -> bool:
        """Add a single document to the knowledge base."""
        if not self.is_initialized:
            self._lazy_init_components()
        
        try:
            # Process the document
            chunks = self.document_processor.process_single_file(file_path)
            
            if not chunks:
                return False
            
            # Generate embeddings
            encoded_chunks = self.embedding_manager.encode_chunks(chunks)
            
            # Add to database
            success = self.chroma_manager.add_documents(encoded_chunks)
            
            if success:
                print(f"Successfully added document: {Path(file_path).name}")
            
            return success
            
        except Exception as e:
            print(f"Error adding document: {str(e)}")
            return False
    
    def clear_knowledge_base(self) -> bool:
        """Clear the entire knowledge base."""
        if not self.is_initialized:
            self._lazy_init_components()
        
        return self.chroma_manager.clear_collection()
    
    def cleanup(self):
        """Clean up resources."""
        if self.llm_manager:
            self.llm_manager.cleanup()
        
        print("Pipeline cleanup completed")