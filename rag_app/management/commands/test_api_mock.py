"""
Management command to test the RAG API endpoint with mock LLM
"""

from django.core.management.base import BaseCommand
from django.test import Client, override_settings
from django.contrib.auth.models import User
import json
from unittest.mock import patch


class Command(BaseCommand):
    help = 'Test the RAG API endpoint with mock LLM'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='What meetings or tasks involve Young?',
            help='Query to test with',
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.3,
            help='Similarity threshold for search',
        )
    
    async def mock_llm_response(self, prompt):
        """Mock LLM response for testing"""
        # Simulate API delay
        import asyncio
        await asyncio.sleep(0.1)
        
        response = "Based on the provided documents, I found information about meetings with Young and related tasks."
        
        metadata = {
            'prompt_tokens': 500,
            'completion_tokens': 150,
            'total_cost': 0.002,
            'llm_time': 0.8,
            'model': 'mock-api-model',
        }
        
        return response, metadata
    
    def handle(self, *args, **options):
        """Test RAG API endpoint with mock LLM"""
        query_text = options['query']
        threshold = options['threshold']
        
        self.stdout.write(self.style.HTTP_INFO("🌐 Testing RAG API with Mock LLM"))
        self.stdout.write("="*60)
        
        self.stdout.write(f"❓ Query: {query_text}")
        self.stdout.write(f"🎯 Threshold: {threshold}")
        self.stdout.write("-"*60)
        
        try:
            # Mock the LLM response to avoid OpenRouter API
            with patch('rag_app.rag_engine.RAGQueryEngine.generate_llm_response', self.mock_llm_response):
                # Create test client
                client = Client()
                
                # Prepare request data
                data = {
                    'query': query_text,
                    'similarity_threshold': threshold,
                    'max_results': 5
                }
                
                # Make API request
                self.stdout.write("📡 Making API request with mock LLM...")
                response = client.post(
                    '/api/query/',
                    data=json.dumps(data),
                    content_type='application/json'
                )
                
                self.stdout.write(f"📊 Status Code: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    
                    self.stdout.write("\n" + "="*60)
                    self.stdout.write(self.style.SUCCESS("✅ API RESPONSE"))
                    self.stdout.write("="*60)
                    
                    self.stdout.write(f"\n💬 Answer:")
                    self.stdout.write("-"*30)
                    self.stdout.write(result.get('response', 'No response'))
                    
                    source_chunks = result.get('source_chunks', [])
                    if source_chunks:
                        self.stdout.write(f"\n📚 Source Chunks ({len(source_chunks)}):")
                        self.stdout.write("-"*50)
                        
                        for i, chunk in enumerate(source_chunks, 1):
                            self.stdout.write(f"\n{i}. Document: {chunk.get('document_title', 'Unknown')}")
                            self.stdout.write(f"   Similarity: {chunk.get('similarity_score', 0):.3f}")
                            self.stdout.write(f"   Content: {chunk.get('content', '')[:200]}...")
                    
                    # Performance metrics
                    self.stdout.write(f"\n⚡ Performance:")
                    self.stdout.write("-"*30)
                    self.stdout.write(f"Search time: {result.get('search_time', 0):.3f}s")
                    self.stdout.write(f"LLM time: {result.get('llm_time', 0):.3f}s")
                    self.stdout.write(f"Total time: {result.get('total_time', 0):.3f}s")
                    self.stdout.write(f"Chunks found: {result.get('total_chunks_found', 0)}")
                    
                    if result.get('prompt_tokens', 0) > 0:
                        self.stdout.write(f"\n💰 Token Usage:")
                        self.stdout.write("-"*30)
                        self.stdout.write(f"Prompt tokens: {result.get('prompt_tokens', 0)}")
                        self.stdout.write(f"Completion tokens: {result.get('completion_tokens', 0)}")
                        self.stdout.write(f"Total cost: ${result.get('total_cost', 0):.6f}")
                        self.stdout.write(f"Model: {result.get('llm_model', 'Unknown')}")
                    
                    self.stdout.write("\n" + "="*60)
                    self.stdout.write(
                        self.style.SUCCESS("🎉 API test with mock LLM successful!")
                    )
                    
                else:
                    try:
                        error_data = response.json()
                    except:
                        error_data = {'error': response.content.decode('utf-8')}
                    
                    self.stdout.write(
                        self.style.ERROR(f"❌ API request failed: {error_data.get('error', 'Unknown error')}")
                    )
                    
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ API test failed: {str(e)}")
            )
            import traceback
            self.stdout.write(traceback.format_exc())
