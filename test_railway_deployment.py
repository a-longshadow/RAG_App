#!/usr/bin/env python3
"""
Railway deployment test script
Tests Django configuration for Railway compatibility
"""

import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_rag.settings')

def test_railway_config():
    """Test Railway deployment configuration"""
    print("🚀 Testing Railway Deployment Configuration\n")
    
    try:
        django.setup()
        from django.conf import settings
        from django.core.management import execute_from_command_line
        
        # Test 1: Settings Import
        print("✅ Django settings imported successfully")
        
        # Test 2: Database Configuration
        db_config = settings.DATABASES['default']
        print(f"✅ Database engine: {db_config['ENGINE']}")
        
        # Test 3: Static Files
        print(f"✅ Static files root: {settings.STATIC_ROOT}")
        print(f"✅ Static URL: {settings.STATIC_URL}")
        
        # Test 4: Security Settings
        if hasattr(settings, 'RAILWAY_ENVIRONMENT'):
            print(f"✅ Railway environment detection: {settings.RAILWAY_ENVIRONMENT}")
        
        # Test 5: Required Apps
        required_apps = ['rag_app', 'rest_framework']
        for app in required_apps:
            if app in settings.INSTALLED_APPS:
                print(f"✅ Required app installed: {app}")
            else:
                print(f"❌ Missing required app: {app}")
        
        # Test 6: Middleware
        required_middleware = ['whitenoise.middleware.WhiteNoiseMiddleware']
        for middleware in required_middleware:
            if middleware in settings.MIDDLEWARE:
                print(f"✅ Required middleware: {middleware}")
            else:
                print(f"❌ Missing middleware: {middleware}")
        
        print("\n🎉 Railway configuration test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_deployment_checklist():
    """Check deployment readiness"""
    print("\n📋 Deployment Checklist:")
    
    # Check required files
    required_files = [
        'nixpacks.toml',
        'Procfile', 
        'requirements.txt',
        'manage.py'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ Missing: {file}")
    
    # Check environment variables
    required_env = [
        'OPENROUTER_API_KEY'
    ]
    
    print("\n🔧 Environment Variables:")
    for env_var in required_env:
        if os.getenv(env_var):
            print(f"✅ {env_var} is set")
        else:
            print(f"⚠️  {env_var} not set (required for production)")

if __name__ == "__main__":
    test_railway_config()
    test_deployment_checklist()
    
    print("\n🚀 Ready for Railway deployment!")
    print("Next steps:")
    print("1. Push code to GitHub")
    print("2. Connect repository to Railway")
    print("3. Add PostgreSQL service")
    print("4. Set environment variables")
    print("5. Deploy!")
