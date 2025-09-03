#!/usr/bin/env python
"""
Quick RAG System Test Script
Tests core functionality without lengthy diagnostics
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
from rag_app.openrouter_client import get_openrouter_client


def test_data_integrity():
    """Quick data check"""
    docs = Document.objects.count()
    chunks = DocumentChunk.objects.count()
    embeddings = Embedding.objects.count()
    
    print(f"📊 DATA STATUS:")
    print(f"   Documents: {docs}")
    print(f"   Chunks: {chunks}")
    print(f"   Embeddings: {embeddings}")
    
    if chunks > 0 and embeddings == 0:
        print("❌ PROBLEM: Chunks exist but no embeddings!")
        return False
    
    if docs > 0 and chunks == 0:
        print("❌ PROBLEM: Documents exist but no chunks!")
        return False
        
    print("✅ Data integrity OK")
    return True


def test_search_functionality():
    """Test core search"""
    try:
        engine = RAGQueryEngine()
        print(f"🔍 SEARCH TEST:")
        print(f"   Similarity threshold: {engine.config.similarity_threshold}")
        print(f"   Max chunks: {engine.config.max_chunks}")
        
        # Test with a simple query
        response = engine.query("test", user=None)
        print(f"   Query processed: {response.total_chunks_found} chunks found")
        
        if response.total_chunks_found == 0:
            print("❌ PROBLEM: No chunks found for test query")
            return False
            
        print("✅ Search functionality OK")
        return True
        
    except Exception as e:
        print(f"❌ SEARCH ERROR: {e}")
        return False


def test_llm_connection():
    """Test LLM connection"""
    try:
        client = get_openrouter_client()
        print(f"🤖 LLM TEST:")
        print(f"   Model: {client.default_model}")
        
        # Test simple connection
        result = client.test_connection()
        print(f"   Connection: {'✅ OK' if result else '❌ FAILED'}")
        
        return result
        
    except Exception as e:
        print(f"❌ LLM ERROR: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 QUICK RAG SYSTEM TEST")
    print("=" * 40)
    
    tests = [
        test_data_integrity,
        test_search_functionality, 
        test_llm_connection
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ TEST CRASHED: {e}")
            results.append(False)
        print()
    
    print("📋 SUMMARY:")
    print(f"   Data: {'✅' if results[0] else '❌'}")
    print(f"   Search: {'✅' if results[1] else '❌'}")
    print(f"   LLM: {'✅' if results[2] else '❌'}")
    
    if all(results):
        print("\n🎉 ALL TESTS PASSED - System should work!")
    else:
        print("\n⚠️  Some tests failed - Check issues above")


if __name__ == "__main__":
    main()
