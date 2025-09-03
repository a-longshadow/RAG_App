"""
Management command to test the RAG query engine
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rag_app.rag_engine import RAGQueryEngine, quick_query


class Command(BaseCommand):
    help = 'Test the RAG query engine with sample queries'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--query',
            type=str,
            default='What information do you have about tasks or projects?',
            help='Query to test with',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to use for the query (optional)',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed response metadata',
        )
    
    def handle(self, *args, **options):
        """Test the RAG query engine"""
        query_text = options['query']
        user_id = options.get('user_id')
        detailed = options['detailed']
        
        self.stdout.write(self.style.HTTP_INFO("🚀 Testing RAG Query Engine"))
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
        self.stdout.write("-"*60)
        
        try:
            # Initialize RAG engine
            self.stdout.write("🔧 Initializing RAG engine...")
            engine = RAGQueryEngine()
            
            # Perform query
            self.stdout.write("🔍 Processing query...")
            response = engine.query(query_text, user=user)
            
            # Display results
            self.stdout.write("\n" + "="*60)
            self.stdout.write(self.style.SUCCESS("✅ RAG RESPONSE"))
            self.stdout.write("="*60)
            
            self.stdout.write(f"\n📝 Answer:")
            self.stdout.write("-"*30)
            self.stdout.write(response.response)
            
            if response.source_chunks:
                self.stdout.write(f"\n📚 Source Chunks ({len(response.source_chunks)}):")
                self.stdout.write("-"*30)
                
                for i, chunk_result in enumerate(response.source_chunks, 1):
                    chunk = chunk_result.chunk
                    similarity = chunk_result.similarity_score
                    
                    self.stdout.write(f"\n{i}. Document: {chunk.document.title}")
                    self.stdout.write(f"   Similarity: {similarity:.3f}")
                    self.stdout.write(f"   Content: {chunk.content[:200]}...")
                    if detailed:
                        self.stdout.write(f"   Position: {chunk.position_start}-{chunk.position_end}")
                        self.stdout.write(f"   Words: {chunk.word_count}")
            else:
                self.stdout.write("\n📚 No relevant source chunks found")
            
            # Performance metrics
            self.stdout.write(f"\n⚡ Performance Metrics:")
            self.stdout.write("-"*30)
            self.stdout.write(f"Search time: {response.search_time:.3f}s")
            self.stdout.write(f"LLM time: {response.llm_time:.3f}s")
            self.stdout.write(f"Total time: {response.total_time:.3f}s")
            self.stdout.write(f"Chunks found: {response.total_chunks_found}")
            
            if detailed:
                self.stdout.write(f"\n💰 Token Usage:")
                self.stdout.write("-"*30)
                self.stdout.write(f"Prompt tokens: {response.prompt_tokens}")
                self.stdout.write(f"Completion tokens: {response.completion_tokens}")
                self.stdout.write(f"Total cost: ${response.total_cost:.6f}")
                self.stdout.write(f"LLM model: {response.llm_model}")
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write(
                self.style.SUCCESS("🎉 RAG query test completed successfully!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ RAG query test failed: {str(e)}")
            )
            if detailed:
                import traceback
                self.stdout.write(traceback.format_exc())
        
        # Test quick_query function
        self.stdout.write("\n" + "="*60)
        self.stdout.write("🚀 Testing quick_query function...")
        
        try:
            quick_response = quick_query("What documents are available?", user=user)
            self.stdout.write(
                self.style.SUCCESS("✅ quick_query function works!")
            )
            self.stdout.write(f"Response: {quick_response.response[:100]}...")
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ quick_query failed: {str(e)}")
            )
