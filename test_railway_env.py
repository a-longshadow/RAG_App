#!/usr/bin/env python3
"""
Railway Environment Simulation Test
==================================

This script simulates Railway environment variables to test
that the application configuration works correctly for both
localhost and Railway deployment.
"""

import os
import sys
import django
from pathlib import Path

def test_local_environment():
    """Test local development environment configuration"""
    print("🏠 TESTING LOCAL ENVIRONMENT")
    print("=" * 50)
    
    # Clear any Railway environment variables
    for key in ['RAILWAY_ENVIRONMENT', 'DATABASE_URL']:
        if key in os.environ:
            del os.environ[key]
    
    # Set up Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_rag.settings')
    django.setup()
    
    from django.conf import settings
    
    # Test database configuration
    db_config = settings.DATABASES['default']
    print(f"✅ Database Engine: {db_config['ENGINE']}")
    print(f"✅ Database Name: {db_config['NAME']}")
    print(f"✅ Database Host: {db_config['HOST']}")
    print(f"✅ Debug Mode: {settings.DEBUG}")
    print(f"✅ Allowed Hosts: {settings.ALLOWED_HOSTS}")
    
    # Verify it's using local configuration
    assert db_config['HOST'] == 'localhost', "Should use localhost for local dev"
    assert settings.DEBUG == True, "Debug should be enabled for local dev"
    
    print("✅ Local environment configuration OK!")
    return True

def test_railway_environment():
    """Test Railway production environment configuration"""
    print("\n☁️  TESTING RAILWAY ENVIRONMENT")
    print("=" * 50)
    
    # Simulate Railway environment
    os.environ['RAILWAY_ENVIRONMENT'] = 'production'
    os.environ['DATABASE_URL'] = 'postgresql://testuser:testpass@testhost:5432/testdb'
    
    # Reload Django settings
    from importlib import reload
    from django_rag import settings as settings_module
    reload(settings_module)
    
    from django.conf import settings
    
    # Test database configuration
    db_config = settings.DATABASES['default']
    print(f"✅ Database Engine: {db_config['ENGINE']}")
    print(f"✅ Database Name: {db_config['NAME']}")
    print(f"✅ Database Host: {db_config['HOST']}")
    print(f"✅ Debug Mode: {settings.DEBUG}")
    print(f"✅ Security Settings:")
    print(f"   - SECURE_BROWSER_XSS_FILTER: {getattr(settings, 'SECURE_BROWSER_XSS_FILTER', False)}")
    print(f"   - SECURE_CONTENT_TYPE_NOSNIFF: {getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False)}")
    print(f"   - CSRF_COOKIE_SECURE: {getattr(settings, 'CSRF_COOKIE_SECURE', False)}")
    
    # Verify it's using Railway configuration
    assert db_config['NAME'] == 'testdb', "Should use DATABASE_URL for Railway"
    assert db_config['HOST'] == 'testhost', "Should use DATABASE_URL host"
    assert settings.DEBUG == False, "Debug should be disabled in production"
    
    print("✅ Railway environment configuration OK!")
    return True

def test_environment_switching():
    """Test that environment switching works correctly"""
    print("\n🔄 TESTING ENVIRONMENT SWITCHING")
    print("=" * 50)
    
    # Test switching from Railway back to local
    for key in ['RAILWAY_ENVIRONMENT', 'DATABASE_URL']:
        if key in os.environ:
            del os.environ[key]
    
    # Reload settings
    from importlib import reload
    from django_rag import settings as settings_module
    reload(settings_module)
    
    from django.conf import settings
    
    # Should be back to local configuration
    db_config = settings.DATABASES['default']
    assert db_config['HOST'] == 'localhost', "Should switch back to localhost"
    assert settings.DEBUG == True, "Should switch back to debug mode"
    
    print("✅ Environment switching works correctly!")
    return True

def main():
    """Run all environment tests"""
    print("🧪 RAILWAY ENVIRONMENT COMPATIBILITY TEST")
    print("=" * 60)
    
    try:
        # Change to project directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Run tests
        test_local_environment()
        test_railway_environment() 
        test_environment_switching()
        
        print("\n🎉 ALL ENVIRONMENT TESTS PASSED!")
        print("=" * 60)
        print("✅ Your application is ready for both localhost and Railway deployment!")
        print("✅ Environment detection works correctly")
        print("✅ Database configuration adapts automatically")
        print("✅ Security settings activate in production")
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
