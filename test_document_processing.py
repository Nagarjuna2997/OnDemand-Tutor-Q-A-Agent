#!/usr/bin/env python3
"""
Test just the document processing pipeline without heavy LLM loading.
"""

import sys
from pathlib import Path
sys.path.append('src')

from utils.document_processor import DocumentProcessor
from embeddings.embedding_manager import EmbeddingManager
from database.chroma_manager import ChromaManager

def test_document_pipeline():
    """Test document processing without the LLM."""
    print("=" * 60)
    print("TESTING DOCUMENT PROCESSING PIPELINE")
    print("=" * 60)
    
    # Test PDF processing
    print("\n1. Testing PDF processing...")
    processor = DocumentProcessor()
    
    # Process just the main PDF file
    pdf_path = "data/course_materials/1_merged_compressed.pdf"
    if not Path(pdf_path).exists():
        print(f"PDF not found: {pdf_path}")
        return False
    
    print(f"Processing: {pdf_path}")
    chunks = processor.process_single_file(pdf_path)
    
    if not chunks:
        print("ERROR: No chunks created")
        return False
    
    print(f"SUCCESS: Created {len(chunks)} chunks")
    print(f"Sample chunk: {chunks[0]['content'][:100]}...")
    
    # Test embeddings
    print("\n2. Testing embeddings...")
    embedding_mgr = EmbeddingManager()
    
    # Encode first few chunks
    test_chunks = chunks[:3]
    encoded_chunks = embedding_mgr.encode_chunks(test_chunks)
    
    if not encoded_chunks:
        print("ERROR: Failed to encode chunks")
        return False
    
    print(f"SUCCESS: Encoded {len(encoded_chunks)} chunks")
    print(f"Embedding dimension: {len(encoded_chunks[0]['embedding'])}")
    
    # Test database storage
    print("\n3. Testing database storage...")
    chroma_mgr = ChromaManager()
    
    # Clear existing data first
    chroma_mgr.clear_collection()
    
    # Store encoded chunks
    success = chroma_mgr.add_documents(encoded_chunks)
    
    if not success:
        print("ERROR: Failed to store in database")
        return False
    
    # Check storage
    stats = chroma_mgr.get_collection_stats()
    total_docs = stats.get('total_documents', 0)
    
    print(f"SUCCESS: Stored {total_docs} documents")
    print(f"Files: {stats.get('unique_source_files', 0)}")
    print(f"Source files: {stats.get('source_files', [])}")
    
    # Test query
    print("\n4. Testing similarity search...")
    query_text = "What is network security?"
    query_embedding = embedding_mgr.encode_text(query_text)
    
    results = chroma_mgr.query_similar_documents(query_text, query_embedding, top_k=3)
    
    print(f"Query: {query_text}")
    print(f"Results found: {len(results)}")
    
    if results:
        print("\nTop results:")
        for i, result in enumerate(results, 1):
            similarity = result.get('similarity', 0)
            file_name = result.get('metadata', {}).get('source_file', 'Unknown')
            content_preview = result.get('content', '')[:100] + "..."
            print(f"[{i}] {file_name} (Score: {similarity:.3f})")
            print(f"    Content: {content_preview}")
    else:
        print("No results found!")
        return False
    
    print(f"\nTEST PASSED: Document processing pipeline working!")
    print(f"Citations will now show: {len(results)} sources")
    return True

if __name__ == "__main__":
    success = test_document_pipeline()
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")