"""
Embedding management using Sentence Transformers for the OnDemand Tutor Q&A Agent.
Handles text-to-vector conversion for semantic search capabilities.
"""

import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from config.settings import EMBEDDING_MODEL

class EmbeddingManager:
    """Manages text embeddings using Sentence Transformers."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """Initialize the embedding model."""
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the Sentence Transformers model."""
        try:
            print(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            print(f"Successfully loaded {self.model_name}")
        except Exception as e:
            print(f"Error loading embedding model: {str(e)}")
            raise e
    
    def encode_text(self, text: str) -> np.ndarray:
        """Convert a single text string to embedding vector."""
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            print(f"Error encoding text: {str(e)}")
            raise e
    
    def encode_texts(self, texts: List[str], batch_size: int = 128, show_progress: bool = True) -> np.ndarray:
        """Convert multiple texts to embedding vectors in batches."""
        if not self.model:
            raise RuntimeError("Embedding model not loaded")

        if not texts:
            return np.array([])

        try:
            print(f"Encoding {len(texts)} texts with batch size {batch_size}...")
            # Generate embeddings in batches for efficiency
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            print(f"Error encoding texts: {str(e)}")
            raise e
    
    def encode_chunks(self, chunks: List[Dict[str, str]], batch_size: int = 128) -> List[Dict]:
        """Encode document chunks and return with embeddings and metadata."""
        if not chunks:
            return []

        print(f"Encoding {len(chunks)} chunks with optimized batch size ({batch_size})...")

        # Extract text content from chunks
        texts = [chunk['content'] for chunk in chunks]

        # Generate embeddings
        embeddings = self.encode_texts(texts, batch_size=batch_size)

        # Combine chunks with their embeddings
        encoded_chunks = []
        for i, chunk in enumerate(chunks):
            encoded_chunk = {
                'id': f"{chunk['metadata']['source_file']}_chunk_{chunk['chunk_index']}",
                'content': chunk['content'],
                'embedding': embeddings[i],
                'metadata': chunk['metadata']
            }
            encoded_chunks.append(encoded_chunk)

        print(f"Successfully encoded {len(encoded_chunks)} chunks")
        return encoded_chunks
    
    def compute_similarity(self, query_embedding: np.ndarray, document_embeddings: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and document embeddings."""
        try:
            # Normalize embeddings
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            doc_norms = document_embeddings / np.linalg.norm(document_embeddings, axis=1, keepdims=True)
            
            # Compute cosine similarity
            similarities = np.dot(doc_norms, query_norm)
            return similarities
        except Exception as e:
            print(f"Error computing similarity: {str(e)}")
            raise e
    
    def find_similar_chunks(self, query: str, encoded_chunks: List[Dict], top_k: int = 5) -> List[Tuple[Dict, float]]:
        """Find the most similar chunks to a query."""
        if not encoded_chunks:
            return []
        
        # Encode the query
        query_embedding = self.encode_text(query)
        
        # Extract document embeddings
        document_embeddings = np.array([chunk['embedding'] for chunk in encoded_chunks])
        
        # Compute similarities
        similarities = self.compute_similarity(query_embedding, document_embeddings)
        
        # Get top-k most similar chunks
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            chunk = encoded_chunks[idx]
            similarity_score = float(similarities[idx])
            results.append((chunk, similarity_score))
        
        return results
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings produced by the model."""
        if not self.model:
            raise RuntimeError("Embedding model not loaded")
        
        # Test with a sample text
        sample_embedding = self.encode_text("sample text")
        return sample_embedding.shape[0]
    
    def get_model_info(self) -> Dict[str, str]:
        """Get information about the loaded model."""
        if not self.model:
            return {"status": "Model not loaded"}
        
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.get_embedding_dimension(),
            "max_sequence_length": getattr(self.model, 'max_seq_length', 'Unknown'),
            "status": "Loaded successfully"
        }