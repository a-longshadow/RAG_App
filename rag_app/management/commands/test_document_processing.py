"""
Django management command to test document processing pipeline
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import os

from rag_app.document_processor import get_document_processor
from rag_app.models import Document


class Command(BaseCommand):
    help = 'Test document processing pipeline with a sample document'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file-path',
            type=str,
            help='Path to test document file',
            default='/Users/joe/Documents/RAG/test_document.txt'
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='User ID to associate with document',
            default=1
        )
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        user_id = options['user_id']
        
        self.stdout.write(f"🚀 Testing Document Processing Pipeline")
        self.stdout.write(f"File: {file_path}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stdout.write(
                self.style.ERROR(f"File not found: {file_path}")
            )
            return
        
        # Get user
        try:
            user = User.objects.get(id=user_id)
            self.stdout.write(f"User: {user.username}")
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"User with ID {user_id} not found")
            )
            return
        
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        filename = os.path.basename(file_path)
        
        # Create uploaded file object
        uploaded_file = SimpleUploadedFile(
            name=filename,
            content=file_content,
            content_type='text/plain'
        )
        
        try:
            # Process document
            self.stdout.write("📄 Processing document...")
            processor = get_document_processor()
            
            document = processor.process_document(
                uploaded_file, 
                user, 
                title=f"Test Document - {filename}"
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Document created: {document.title}")
            )
            self.stdout.write(f"   ID: {document.id}")
            self.stdout.write(f"   Content length: {len(document.content)} characters")
            self.stdout.write(f"   Status: {document.status}")
            
            # Process chunks and embeddings
            self.stdout.write("🔄 Creating chunks and embeddings...")
            processor.create_chunks_and_embeddings(document)
            
            # Refresh from database
            document.refresh_from_db()
            
            self.stdout.write(
                self.style.SUCCESS(f"✅ Processing completed!")
            )
            self.stdout.write(f"   Status: {document.status}")
            self.stdout.write(f"   Chunks created: {document.chunk_count}")
            self.stdout.write(f"   Embeddings: {document.chunks.filter(embedding__isnull=False).count()}")
            
            # Show chunks summary
            self.stdout.write("\n📊 Chunks Summary:")
            for chunk in document.chunks.all()[:5]:  # Show first 5 chunks
                has_embedding = "✅" if hasattr(chunk, 'embedding') and chunk.embedding else "❌"
                self.stdout.write(
                    f"   Chunk {chunk.chunk_index}: {chunk.char_count} chars, "
                    f"{chunk.word_count} words {has_embedding}"
                )
            
            if document.chunk_count > 5:
                self.stdout.write(f"   ... and {document.chunk_count - 5} more chunks")
            
            self.stdout.write(
                self.style.SUCCESS(f"\n🎉 Document processing test completed successfully!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Error processing document: {str(e)}")
            )
            import traceback
            traceback.print_exc()
