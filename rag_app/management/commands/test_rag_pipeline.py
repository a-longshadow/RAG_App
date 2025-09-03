"""
Management command to test the complete RAG pipeline with a mock LLM response
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rag_app.rag_engine import RAGQueryEngine
from decimal import Decimal
import time


class MockRAGEngine(RAGQueryEngine):
    """RAG Engine with mock LLM for testing"""
    
    async def generate_llm_response(self, prompt: str):
        """Mock LLM response for testing"""
        await self._simulate_delay()
        
        # Analyze the prompt to generate a relevant mock response
        context_lines = prompt.split('\n')
        context_content = []
        
        for line in context_lines:
            if line.strip() and not line.startswith('Context:') and not line.startswith('Question:') and not line.startswith('Answer:'):
                if any(keyword in line.lower() for keyword in ['unnamed', 'task', 'meeting', 'project', 'done']):
                    context_content.append(line.strip())
        
        if context_content:
            response = f"Based on the provided documents, I found the following relevant information:\n\n"
            
            # Extract key information from context
            if any('young' in content.lower() for content in context_content):
                response += "• There is a scheduled meeting with Young at noon EAT to discuss workflow.\n"
            
            if any('monday.com' in content.lower() for content in context_content):
                response += "• Research is being conducted on connecting Monday.com boards with AI for processing meeting transcriptions.\n"
            
            if any('task' in content.lower() for content in context_content):
                response += "• Multiple tasks are documented with various completion statuses.\n"
            
            response += f"\nThis information comes from {len(context_content)} relevant document sections."
        else:
            response = "I couldn't find specific information to answer your question based on the available documents. Please try rephrasing your query or check if the relevant documents have been uploaded."
        
        # Mock usage metadata
        prompt_tokens = len(prompt.split()) * 1.3  # Rough token estimation
        completion_tokens = len(response.split()) * 1.3
        
        metadata = {
            'prompt_tokens': int(prompt_tokens),
            'completion_tokens': int(completion_tokens),
            'total_cost': Decimal('0.002'),  # Mock cost
            'llm_time': 1.5,  # Mock response time
            'model': 'mock-llm-v1',
        }
        
        return response, metadata
    
    async def _simulate_delay(self):
        """Simulate LLM response delay"""
        import asyncio
        await asyncio.sleep(0.5)  # 500ms delay


class Command(BaseCommand):
    help = 'Test the complete RAG pipeline with mock LLM'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='What meetings or tasks involve Young?',
            help='Query to test with',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to use for the query (optional)',
        )
        parser.add_argument(
            '--threshold',
            type=float,
            default=0.5,
            help='Similarity threshold for search',
        )
    
    def handle(self, *args, **options):
        """Test complete RAG pipeline"""
        query_text = options['query']
        user_id = options.get('user_id')
        threshold = options['threshold']
        
        self.stdout.write(self.style.HTTP_INFO("🚀 Testing Complete RAG Pipeline"))
        self.stdout.write("="*60)
        
        # Get user if specified
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                self.stdout.write(f"👤 User: {user.username}")
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"❌ User with ID {user_id} not found")
                )
                return
        else:
            # Use first available user
            user = User.objects.first()
            if user:
                self.stdout.write(f"👤 Using user: {user.username}")
        
        self.stdout.write(f"❓ Query: {query_text}")
        self.stdout.write(f"🎯 Similarity threshold: {threshold}")
        self.stdout.write("-"*60)
        
        try:
            # Initialize mock RAG engine
            self.stdout.write("🔧 Initializing RAG engine with mock LLM...")
            engine = MockRAGEngine()
            engine.config.similarity_threshold = threshold
            
            # Perform complete RAG query
            self.stdout.write("🔍 Processing complete RAG query...")
            response = engine.query(query_text, user=user)
            
            # Display results
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.SUCCESS("✅ RAG RESPONSE"))
            self.stdout.write("="*60)
            
            self.stdout.write(f"\n💬 Answer:")
            self.stdout.write("-"*30)
            self.stdout.write(response.response)
            
            if response.source_chunks:
                self.stdout.write(f"\n📚 Source Chunks ({len(response.source_chunks)}):")
                self.stdout.write("-"*50)
                
                for i, chunk_result in enumerate(response.source_chunks, 1):
                    chunk = chunk_result.chunk
                    similarity = chunk_result.similarity_score
                    
                    self.stdout.write(f"\n{i}. Document: {chunk.document.title}")
                    self.stdout.write(f"   File: {chunk.document.file_name}")
                    self.stdout.write(f"   Similarity: {similarity:.3f}")
                    self.stdout.write(f"   Content: {chunk.content[:200]}...")
            else:
                self.stdout.write("\n📚 No relevant source chunks found")
            
            # Performance metrics
            self.stdout.write(f"\n⚡ Performance Metrics:")
            self.stdout.write("-"*30)
            self.stdout.write(f"Search time: {response.search_time:.3f}s")
            self.stdout.write(f"LLM time: {response.llm_time:.3f}s")
            self.stdout.write(f"Total time: {response.total_time:.3f}s")
            self.stdout.write(f"Chunks found: {response.total_chunks_found}")
            
            self.stdout.write(f"\n💰 Token Usage:")
            self.stdout.write("-"*30)
            self.stdout.write(f"Prompt tokens: {response.prompt_tokens}")
            self.stdout.write(f"Completion tokens: {response.completion_tokens}")
            self.stdout.write(f"Total cost: ${response.total_cost:.6f}")
            self.stdout.write(f"LLM model: {response.llm_model}")
            
            # Check if query was logged
            from rag_app.models import QueryLog
            recent_logs = QueryLog.objects.filter(query_text=query_text).order_by('-created_at')[:1]
            if recent_logs:
                log = recent_logs[0]
                self.stdout.write(f"\n📝 Query logged with ID: {log.id}")
                self.stdout.write(f"   Source chunks logged: {log.source_chunks.count()}")
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write(
                self.style.SUCCESS("🎉 Complete RAG pipeline test successful!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ RAG pipeline test failed: {str(e)}")
            )
            import traceback
            self.stdout.write(traceback.format_exc())
