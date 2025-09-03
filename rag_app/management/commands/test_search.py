"""
Management command to test just the semantic search functionality
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rag_app.rag_engine import RAGQueryEngine
from rag_app.models import DocumentChunk


class Command(BaseCommand):
    help = 'Test the semantic search functionality without LLM'
    
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
    
    def handle(self, *args, **options):
        """Test semantic search"""
        query_text = options['query']
        user_id = options.get('user_id')
        
        self.stdout.write(self.style.HTTP_INFO("🔍 Testing Semantic Search"))
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
        
        # Check available documents and chunks
        total_chunks = DocumentChunk.objects.count()
        user_chunks = DocumentChunk.objects.filter(document__uploaded_by=user).count() if user else 0
        
        self.stdout.write(f"📊 Total chunks in database: {total_chunks}")
        if user:
            self.stdout.write(f"📊 User's chunks: {user_chunks}")
        
        self.stdout.write(f"❓ Query: {query_text}")
        self.stdout.write("-"*60)
        
        try:
            # Initialize RAG engine
            self.stdout.write("🔧 Initializing RAG engine...")
            engine = RAGQueryEngine()
            
            # Generate query embedding
            self.stdout.write("🧠 Generating query embedding...")
            query_embedding = engine.generate_query_embedding(query_text)
            self.stdout.write(f"✅ Embedding generated: {len(query_embedding)} dimensions")
            
            # Search for similar chunks
            self.stdout.write("🔍 Searching for similar chunks...")
            search_results = engine.search_similar_chunks(query_embedding, user=user)
            
            # Display results
            self.stdout.write(f"\n📚 Found {len(search_results)} relevant chunks:")
            self.stdout.write("-"*60)
            
            if search_results:
                for i, result in enumerate(search_results, 1):
                    chunk = result.chunk
                    similarity = result.similarity_score
                    
                    self.stdout.write(f"\n{i}. Document: {chunk.document.title}")
                    self.stdout.write(f"   File: {chunk.document.file_name}")
                    self.stdout.write(f"   Similarity: {similarity:.3f}")
                    self.stdout.write(f"   Position: {chunk.position_start}-{chunk.position_end}")
                    self.stdout.write(f"   Words: {chunk.word_count}")
                    self.stdout.write(f"   Content preview: {chunk.content[:150]}...")
                    
                # Test context assembly
                self.stdout.write(f"\n📝 Assembled Context:")
                self.stdout.write("-"*60)
                context = engine.assemble_context(search_results)
                self.stdout.write(f"Context length: {len(context)} characters")
                self.stdout.write(f"Preview: {context[:300]}...")
            else:
                self.stdout.write("❌ No chunks found above similarity threshold")
                
                # Try with lower threshold for debugging
                engine.config.similarity_threshold = 0.1
                debug_results = engine.search_similar_chunks(query_embedding, user=user)
                self.stdout.write(f"\n🔍 Debug: Found {len(debug_results)} chunks with threshold 0.1")
                
                if debug_results:
                    best_result = debug_results[0]
                    self.stdout.write(f"Best match: {best_result.similarity_score:.3f} similarity")
                    self.stdout.write(f"Content: {best_result.chunk.content[:200]}...")
            
            self.stdout.write("\n" + "="*60)
            self.stdout.write(
                self.style.SUCCESS("🎉 Semantic search test completed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Semantic search test failed: {str(e)}")
            )
            import traceback
            self.stdout.write(traceback.format_exc())
