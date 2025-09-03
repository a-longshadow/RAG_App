#!/usr/bin/env python
"""
Test script for embedding generation and vector storage
"""
import os
import sys
import django

# Setup Django environment
sys.path.append('/Users/joe/Documents/RAG')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_rag.settings')
django.setup()

from django.contrib.auth.models import User
from rag_app.models import Document, DocumentChunk, Embedding
from rag_app.embedding_utils import get_embedding_generator, chunk_text, calculate_content_hash
import numpy as np


def test_embedding_pipeline():
    """Test the complete embedding pipeline"""
    print("🚀 Testing RAG Embedding Pipeline")
    print("=" * 50)
    
    # Test text
    test_text = """
    Django is a high-level Python web framework that encourages rapid development 
    and clean, pragmatic design. Built by experienced developers, it takes care of 
    much of the hassle of web development, so you can focus on writing your app 
    without needing to reinvent the wheel. It's free and open source.
    
    Django includes dozens of extras you can use to handle common web development 
    tasks. Django takes care of user authentication, content administration, site 
    maps, RSS feeds, and many more tasks — right out of the box.
    """
    
    # Step 1: Test chunking
    print("1. Testing text chunking...")
    chunks = chunk_text(test_text, chunk_size=200, overlap=20)
    print(f"   Created {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"   Chunk {i}: {chunk['char_count']} chars, {chunk['word_count']} words")
    
    # Step 2: Test embedding generation
    print("\n2. Testing embedding generation...")
    embedding_gen = get_embedding_generator()
    
    if len(chunks) > 0:
        test_chunk = chunks[0]['content']
        embedding, processing_time = embedding_gen.generate_embedding(test_chunk)
        print(f"   Embedding shape: {embedding.shape}")
        print(f"   Processing time: {processing_time:.4f} seconds")
        print(f"   First 5 values: {embedding[:5]}")
    
    # Step 3: Test database storage
    print("\n3. Testing database storage...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com'}
    )
    if created:
        print("   Created test user")
    
    # Create a test document
    content_hash = calculate_content_hash(test_text)
    document, created = Document.objects.get_or_create(
        content_hash=content_hash,
        defaults={
            'title': 'Test Document',
            'file_name': 'test.txt',
            'file_path': '/tmp/test.txt',
            'file_size': len(test_text),
            'file_type': 'txt',
            'mime_type': 'text/plain',
            'content': test_text,
            'uploaded_by': user,
            'status': 'processing'
        }
    )
    if created:
        print("   Created test document")
    
    # Create chunks and embeddings
    print("   Creating chunks and embeddings...")
    for chunk_data in chunks:
        # Create DocumentChunk
        doc_chunk, created = DocumentChunk.objects.get_or_create(
            document=document,
            chunk_index=chunk_data['chunk_index'],
            defaults={
                'content': chunk_data['content'],
                'start_char': chunk_data['start_char'],
                'end_char': chunk_data['end_char'],
                'word_count': chunk_data['word_count'],
                'char_count': chunk_data['char_count'],
                'token_count': chunk_data['char_count'] // 4,  # rough estimate
            }
        )
        
        if created:
            # Generate and store embedding
            embedding_vector, proc_time = embedding_gen.generate_embedding(chunk_data['content'])
            
            Embedding.objects.create(
                chunk=doc_chunk,
                vector=embedding_vector.tolist(),  # Convert numpy array to list for pgvector
                model_name=embedding_gen.model_name,
                processing_time=proc_time
            )
            print(f"   Created embedding for chunk {chunk_data['chunk_index']}")
    
    # Update document status
    document.chunk_count = len(chunks)
    document.status = 'processed'
    document.save()
    
    # Step 4: Test similarity search
    print("\n4. Testing similarity search...")
    query = "What is Django?"
    query_embedding, _ = embedding_gen.generate_embedding(query)
    
    # Get all embeddings for similarity search
    embeddings = Embedding.objects.all()
    similarities = []
    
    for emb in embeddings:
        # Convert stored vector back to numpy array
        stored_vector = np.array(emb.vector)
        similarity = embedding_gen.get_similarity(query_embedding, stored_vector)
        similarities.append((emb.chunk, similarity))
    
    # Sort by similarity (highest first)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    print(f"   Query: '{query}'")
    print("   Top 3 most similar chunks:")
    for i, (chunk, similarity) in enumerate(similarities[:3]):
        print(f"   {i+1}. Similarity: {similarity:.4f}")
        print(f"      Content: {chunk.content[:100]}...")
    
    print("\n✅ All tests completed successfully!")
    
    # Cleanup for repeated runs
    print("\n🧹 Cleaning up test data...")
    Document.objects.filter(title='Test Document').delete()
    if created:
        user.delete()
    
    return True


if __name__ == "__main__":
    try:
        test_embedding_pipeline()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
