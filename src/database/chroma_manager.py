"""
Chroma vector database management for the OnDemand Tutor Q&A Agent.
Handles storage and retrieval of document embeddings for semantic search.
"""

import os
import json
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from config.settings import CHROMA_DB_PATH, COLLECTION_NAME

class ChromaManager:
    """Manages Chroma vector database operations."""
    
    def __init__(self, db_path: str = CHROMA_DB_PATH, collection_name: str = COLLECTION_NAME):
        """Initialize Chroma database connection."""
        self.db_path = db_path
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Initialize the Chroma database and collection."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Initialize Chroma client
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Network Security course materials"}
            )
            
            print(f"Successfully initialized Chroma database at: {self.db_path}")
            print(f"Collection: {self.collection_name}")
            
        except Exception as e:
            print(f"Error initializing Chroma database: {str(e)}")
            raise e
    
    def add_documents(self, encoded_chunks: List[Dict]) -> bool:
        """Add encoded document chunks to the vector database."""
        if not encoded_chunks:
            print("No chunks to add")
            return False
        
        try:
            # Prepare data for Chroma
            ids = []
            embeddings = []
            documents = []
            metadatas = []
            
            for chunk in encoded_chunks:
                ids.append(chunk['id'])
                embeddings.append(chunk['embedding'].tolist())
                documents.append(chunk['content'])
                
                # Serialize metadata for Chroma (must be JSON serializable)
                metadata = chunk['metadata'].copy()
                # Convert any non-serializable values to strings
                for key, value in metadata.items():
                    if not isinstance(value, (str, int, float, bool)):
                        metadata[key] = str(value)
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
            
            print(f"Successfully added {len(encoded_chunks)} chunks to database")
            return True
            
        except Exception as e:
            print(f"Error adding documents to database: {str(e)}")
            return False
    
    def query_similar_documents(self, query_text: str, query_embedding: List[float], 
                              top_k: int = 5) -> List[Dict]:
        """Query for similar documents using embedding vector."""
        try:
            # Query the collection
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    result = {
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i],
                        'similarity': 1 - results['distances'][0][i]  # Convert distance to similarity
                    }
                    formatted_results.append(result)
            
            return formatted_results
            
        except Exception as e:
            print(f"Error querying database: {str(e)}")
            return []
    
    def get_document_by_id(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a specific document by ID."""
        try:
            results = self.collection.get(
                ids=[doc_id],
                include=['documents', 'metadatas']
            )
            
            if results['ids'] and len(results['ids']) > 0:
                return {
                    'id': results['ids'][0],
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0]
                }
            return None
            
        except Exception as e:
            print(f"Error retrieving document {doc_id}: {str(e)}")
            return None
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """Delete documents from the collection."""
        try:
            self.collection.delete(ids=doc_ids)
            print(f"Successfully deleted {len(doc_ids)} documents")
            return True
        except Exception as e:
            print(f"Error deleting documents: {str(e)}")
            return False
    
    def clear_collection(self) -> bool:
        """Clear all documents from the collection."""
        try:
            # Delete the collection and recreate it
            self.client.delete_collection(name=self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Network Security course materials"}
            )
            print("Successfully cleared collection")
            return True
        except Exception as e:
            print(f"Error clearing collection: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            # Get collection info
            collection_info = self.collection.get()
            
            total_documents = len(collection_info['ids']) if collection_info['ids'] else 0
            
            # Get unique source files
            unique_files = set()
            if collection_info['metadatas']:
                for metadata in collection_info['metadatas']:
                    if 'source_file' in metadata:
                        unique_files.add(metadata['source_file'])
            
            stats = {
                'collection_name': self.collection_name,
                'total_documents': total_documents,
                'unique_source_files': len(unique_files),
                'source_files': list(unique_files),
                'database_path': self.db_path
            }
            
            return stats
            
        except Exception as e:
            print(f"Error getting collection stats: {str(e)}")
            return {}
    
    def update_document(self, doc_id: str, content: str = None, 
                       metadata: Dict = None, embedding: List[float] = None) -> bool:
        """Update an existing document in the collection."""
        try:
            update_data = {'ids': [doc_id]}
            
            if content is not None:
                update_data['documents'] = [content]
            if metadata is not None:
                # Ensure metadata is JSON serializable
                clean_metadata = {}
                for key, value in metadata.items():
                    if not isinstance(value, (str, int, float, bool)):
                        clean_metadata[key] = str(value)
                    else:
                        clean_metadata[key] = value
                update_data['metadatas'] = [clean_metadata]
            if embedding is not None:
                update_data['embeddings'] = [embedding]
            
            self.collection.update(**update_data)
            print(f"Successfully updated document: {doc_id}")
            return True
            
        except Exception as e:
            print(f"Error updating document {doc_id}: {str(e)}")
            return False
    
    def search_by_metadata(self, metadata_filter: Dict, max_results: int = 50) -> List[Dict]:
        """Search documents by metadata criteria."""
        try:
            # Get all documents first (Chroma's where clause has limitations)
            results = self.collection.get(
                include=['documents', 'metadatas'],
                limit=max_results
            )
            
            if not results['ids']:
                return []
            
            # Filter by metadata
            filtered_results = []
            for i in range(len(results['ids'])):
                metadata = results['metadatas'][i]
                match = True
                
                for key, value in metadata_filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                
                if match:
                    filtered_results.append({
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': metadata
                    })
            
            return filtered_results
            
        except Exception as e:
            print(f"Error searching by metadata: {str(e)}")
            return []