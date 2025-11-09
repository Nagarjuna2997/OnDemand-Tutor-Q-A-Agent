#!/usr/bin/env python3
"""
Test the complete pipeline with knowledge base setup and querying.
"""

import sys
from pathlib import Path
sys.path.append('src')

from qa_pipeline import QAPipeline

def test_complete_pipeline():
    """Test the complete pipeline including knowledge base setup."""
    print("=" * 60)
    print("TESTING COMPLETE PIPELINE")
    print("=" * 60)
    
    # Initialize pipeline
    print("\n1. Initializing pipeline...")
    pipeline = QAPipeline()
    
    # Setup knowledge base
    print("\n2. Setting up knowledge base...")
    success = pipeline.setup_knowledge_base()
    
    if not success:
        print("FAILED: Could not setup knowledge base")
        return False
    
    # Check stats
    print("\n3. Checking knowledge base stats...")
    stats = pipeline.get_knowledge_base_stats()
    print(f"Database: {stats.get('database', {})}")
    
    total_docs = stats.get('database', {}).get('total_documents', 0)
    if total_docs == 0:
        print("WARNING: No documents in database")
        return False
    
    print(f"SUCCESS: Found {total_docs} documents in database")
    
    # Test query
    print("\n4. Testing query...")
    question = "What is network security?"
    result = pipeline.query(question, top_k=3)
    
    print(f"\nQ: {question}")
    print(f"A: {result['answer'][:200]}...")
    print(f"Sources found: {len(result.get('sources', []))}")
    print(f"Context used: {result.get('context_used', 0)}")
    
    # Display sources
    sources = result.get('sources', [])
    if sources:
        print("\nSOURCE CITATIONS:")
        for i, source in enumerate(sources, 1):
            file_name = source.get('file', 'Unknown')
            page_num = source.get('page_number', 'Unknown')
            similarity = source.get('similarity', 0.0)
            print(f"[{i}] {file_name}, Page {page_num} (Relevance: {similarity:.3f})")
    else:
        print("\nNO SOURCES FOUND - CITATIONS WILL BE 0")
    
    # Cleanup
    pipeline.cleanup()
    
    return len(sources) > 0

if __name__ == "__main__":
    success = test_complete_pipeline()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")