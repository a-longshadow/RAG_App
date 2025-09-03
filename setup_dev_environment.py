#!/usr/bin/env python
"""
Development Environment Setup Script
====================================

This script sets up a complete development environment for the RAG system:
1. Runs database migrations
2. Creates default superuser from environment variables
3. Initializes system settings
4. Performs system health check

Usage:
    python setup_dev_environment.py

Environment Variables Required:
    DJANGO_SUPERUSER_USERNAME (default: admin)
    DJANGO_SUPERUSER_PASSWORD (default: testpass123)
    DJANGO_SUPERUSER_EMAIL (default: admin@localhost.local)
"""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def main():
    """Run the development environment setup"""
    
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_rag.settings')
    
    # Setup Django
    django.setup()
    
    print("🚀 RAG SYSTEM - DEVELOPMENT ENVIRONMENT SETUP")
    print("=" * 55)
    
    # Step 1: Run migrations
    print("\n📊 STEP 1: Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False
    
    # Step 2: Create superuser
    print("\n👤 STEP 2: Creating default superuser...")
    try:
        execute_from_command_line(['manage.py', 'ensure_superuser', '--skip-if-exists'])
        print("✅ Superuser setup completed")
    except Exception as e:
        print(f"❌ Superuser creation failed: {e}")
        return False
    
    # Step 3: Initialize system settings
    print("\n⚙️  STEP 3: Initializing system settings...")
    try:
        execute_from_command_line(['manage.py', 'init_settings'])
        print("✅ System settings initialized")
    except Exception as e:
        print(f"❌ Settings initialization failed: {e}")
        return False
    
    # Step 4: Health check
    print("\n🏥 STEP 4: Running system health check...")
    try:
        # Import here to avoid circular imports
        from rag_app.models import Document, DocumentChunk, Embedding
        
        doc_count = Document.objects.count()
        chunk_count = DocumentChunk.objects.count()
        embedding_count = Embedding.objects.count()
        
        print(f"   📄 Documents: {doc_count}")
        print(f"   📝 Chunks: {chunk_count}")
        print(f"   🔗 Embeddings: {embedding_count}")
        print("✅ System health check completed")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Final summary
    print("\n🎉 SETUP COMPLETE!")
    print("=" * 55)
    print("🌐 Your RAG system is ready!")
    print("   • Start server: python manage.py runserver")
    print("   • Access URL: http://127.0.0.1:8000/")
    print("   • Admin URL: http://127.0.0.1:8000/admin/")
    print("   • Default login: admin / testpass123")
    print("")
    
    # Check if OpenRouter API key is set
    api_key = os.getenv('OPENROUTER_API_KEY')
    if api_key:
        print("✅ OpenRouter API key configured")
    else:
        print("⚠️  OpenRouter API key not set (add OPENROUTER_API_KEY to .env)")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
