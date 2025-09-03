"""
Embedding utilities for RAG system using sentence-transformers
"""
import time
import hashlib
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from django.conf import settings
import os


class EmbeddingGenerator:
    """
    Handles embedding generation using sentence-transformers
    """
    
    def __init__(self, model_name: str = 'all-mpnet-base-v2'):
        self.model_name = model_name
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model"""
        try:
            print(f"Loading embedding model: {self.model_name}")
            start_time = time.time()
            self.model = SentenceTransformer(self.model_name)
            load_time = time.time() - start_time
            print(f"Model loaded in {load_time:.2f} seconds")
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            raise
    
    def generate_embedding(self, text: str) -> tuple[np.ndarray, float]:
        """
        Generate embedding for a single text
        
        Returns:
            tuple: (embedding_vector, processing_time)
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        start_time = time.time()
        embedding = self.model.encode(text, convert_to_numpy=True)
        processing_time = time.time() - start_time
        
        return embedding, processing_time
    
    def generate_embeddings_batch(self, texts: List[str]) -> tuple[np.ndarray, float]:
        """
        Generate embeddings for multiple texts efficiently
        
        Returns:
            tuple: (embeddings_array, total_processing_time)
        """
        if not self.model:
            raise ValueError("Model not loaded")
        
        start_time = time.time()
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        processing_time = time.time() - start_time
        
        return embeddings, processing_time
    
    def get_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        """
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[dict]:
    """
    Split text into overlapping chunks for embedding
    
    Args:
        text: Input text to chunk
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks
    
    Returns:
        List of dictionaries with chunk information
    """
    if not text.strip():
        return []
    
    chunks = []
    words = text.split()
    
    current_chunk = ""
    chunk_index = 0
    start_char = 0
    
    for word in words:
        # Check if adding this word would exceed chunk size
        test_chunk = current_chunk + (" " if current_chunk else "") + word
        
        if len(test_chunk) <= chunk_size:
            current_chunk = test_chunk
        else:
            # Save current chunk if it has content
            if current_chunk.strip():
                end_char = start_char + len(current_chunk)
                chunks.append({
                    'content': current_chunk.strip(),
                    'chunk_index': chunk_index,
                    'start_char': start_char,
                    'end_char': end_char,
                    'word_count': len(current_chunk.split()),
                    'char_count': len(current_chunk),
                })
                chunk_index += 1
                
                # Start new chunk with overlap
                overlap_words = current_chunk.split()[-overlap//10:] if overlap > 0 else []
                current_chunk = " ".join(overlap_words)
                start_char = end_char - len(current_chunk)
            
            # Add the current word to new chunk
            current_chunk += (" " if current_chunk else "") + word
    
    # Don't forget the last chunk
    if current_chunk.strip():
        end_char = start_char + len(current_chunk)
        chunks.append({
            'content': current_chunk.strip(),
            'chunk_index': chunk_index,
            'start_char': start_char,
            'end_char': end_char,
            'word_count': len(current_chunk.split()),
            'char_count': len(current_chunk),
        })
    
    return chunks


def calculate_content_hash(content: str) -> str:
    """
    Calculate SHA256 hash of content for deduplication
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count (approximation: 1 token ≈ 4 characters)
    """
    return len(text) // 4


# Global embedding generator instance
_embedding_generator = None

def get_embedding_generator() -> EmbeddingGenerator:
    """
    Get or create global embedding generator instance
    """
    global _embedding_generator
    if _embedding_generator is None:
        model_name = os.getenv('EMBEDDINGS_MODEL', 'all-mpnet-base-v2')
        _embedding_generator = EmbeddingGenerator(model_name)
    return _embedding_generator
