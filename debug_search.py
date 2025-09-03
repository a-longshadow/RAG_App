#!/usr/bin/env python
"""
Debug RAG Search Issues
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_rag.settings')
sys.path.append('/Users/joe/Documents/RAG')
django.setup()

from rag_app.models import Document, DocumentChunk, Embedding
from rag_app.rag_engine import RAGQueryEngine
from django.contrib.auth.models import User
import numpy as np
from pgvector.django import CosineDistance


def debug_search_issue():
    """Debug why search returns no results"""
    print("🔍 DEBUGGING SEARCH ISSUE")
    print("=" * 40)
    
    # Get first user for testing
    user = User.objects.first()
    print(f"Test user: {user.username if user else 'None'}")
    
    # Check chunks with embeddings
    chunks_with_embeddings = DocumentChunk.objects.filter(embedding__isnull=False)
    print(f"Chunks with embeddings: {chunks_with_embeddings.count()}")
    
    if chunks_with_embeddings.count() == 0:
        print("❌ No chunks with embeddings found!")
        return
    
    # Test embedding generation
    engine = RAGQueryEngine()
    query = "test"
    
    try:
        print(f"\n📝 Testing query: '{query}'")
        query_embedding = engine.generate_query_embedding(query)
        print(f"Query embedding shape: {query_embedding.shape}")
        print(f"Query embedding type: {type(query_embedding)}")
        
        # Check embedding dimensions match
        first_chunk = chunks_with_embeddings.first()
        if hasattr(first_chunk, 'embedding') and first_chunk.embedding:
            stored_vector = first_chunk.embedding.vector
            print(f"Stored embedding shape: {np.array(stored_vector).shape}")
            print(f"Stored embedding type: {type(stored_vector)}")
            
            # Test manual similarity calculation
            cosine_dist = np.linalg.norm(query_embedding - np.array(stored_vector))
            print(f"Manual distance to first chunk: {cosine_dist}")
        
        # Test search without user filter
        print(f"\n🔍 Testing search without user filter...")
        chunks_query = DocumentChunk.objects.filter(embedding__isnull=False)
        
        # Test with very loose threshold (0.9)
        loose_threshold = 0.9
        distance_threshold = 1.0 - loose_threshold
        print(f"Using loose similarity threshold: {loose_threshold} (distance < {distance_threshold})")
        
        similar_chunks = chunks_query.annotate(
            similarity=CosineDistance('embedding__vector', query_embedding)
        ).filter(
            similarity__lt=distance_threshold
        ).order_by('similarity')[:10]
        
        print(f"Found {similar_chunks.count()} chunks with loose threshold")
        
        # Show actual similarity scores
        for chunk in similar_chunks:
            similarity_score = 1.0 - chunk.similarity
            print(f"  - Chunk {chunk.id}: similarity {similarity_score:.3f} (distance {chunk.similarity:.3f})")
        
        # Test with NO threshold
        print(f"\n🎯 Testing with NO threshold (show all)...")
        all_chunks = chunks_query.annotate(
            similarity=CosineDistance('embedding__vector', query_embedding)
        ).order_by('similarity')[:5]
        
        print(f"Top 5 chunks by similarity:")
        for chunk in all_chunks:
            similarity_score = 1.0 - chunk.similarity
            print(f"  - Chunk {chunk.id}: similarity {similarity_score:.3f} from '{chunk.document.title}'")
            print(f"    Content preview: {chunk.content[:100]}...")
        
    except Exception as e:
        print(f"❌ Error during search debug: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    debug_search_issue()
