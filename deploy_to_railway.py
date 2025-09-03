#!/usr/bin/env python3
"""
Railway Deployment Automation Script
===================================

This script helps automate the deployment process to Railway.com
with proper environment setup and validation.

Usage:
    python deploy_to_railway.py

Requirements:
    - Railway CLI installed (npm install -g @railway/cli)
    - GitHub repository set up
    - OpenRouter API key
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Error: {result.stderr}")
            return False
        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 CHECKING PREREQUISITES")
    print("=" * 50)
    
    # Check if Railway CLI is installed
    if not run_command("railway --version", "Checking Railway CLI"):
        print("❌ Railway CLI not found. Install it with: npm install -g @railway/cli")
        return False
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        print("❌ Git repository not initialized. Run: git init")
        return False
        
    # Check if OpenRouter API key is set
    if not os.getenv('OPENROUTER_API_KEY'):
        print("⚠️  OPENROUTER_API_KEY not found in environment")
        print("   Make sure to set it in Railway dashboard after deployment")
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found")
        return False
        
    # Check critical files
    required_files = ['Procfile', 'runtime.txt', 'nixpacks.toml', 'manage.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Required file missing: {file}")
            return False
    
    print("✅ All prerequisites met!")
    return True

def validate_django_setup():
    """Validate Django configuration"""
    print("\n🔍 VALIDATING DJANGO SETUP")
    print("=" * 50)
    
    # Check Django configuration
    if not run_command("python manage.py check --deploy", "Django deployment check"):
        print("⚠️  Django deployment check failed - review settings")
        
    # Check if migrations are up to date
    run_command("python manage.py showmigrations", "Checking migrations")
    
    return True

def setup_railway_project():
    """Set up Railway project and environment"""
    print("\n🚀 SETTING UP RAILWAY PROJECT")
    print("=" * 50)
    
    # Login to Railway (if not already logged in)
    run_command("railway login", "Logging into Railway")
    
    # Initialize Railway project
    if not run_command("railway link", "Linking to existing Railway project"):
        print("Creating new Railway project...")
        if not run_command("railway init", "Creating Railway project"):
            return False
    
    # Add PostgreSQL service
    print("\n📊 Setting up PostgreSQL...")
    run_command("railway add postgresql", "Adding PostgreSQL service")
    
    return True

def deploy_application():
    """Deploy the application to Railway"""
    print("\n🚀 DEPLOYING APPLICATION")
    print("=" * 50)
    
    # Commit any uncommitted changes
    run_command("git add .", "Staging changes")
    
    # Check if there are changes to commit
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        commit_message = input("Enter commit message (or press Enter for default): ").strip()
        if not commit_message:
            commit_message = "Deploy to Railway with automated setup"
        run_command(f'git commit -m "{commit_message}"', "Committing changes")
    
    # Deploy to Railway
    if not run_command("railway up", "Deploying to Railway"):
        return False
    
    print("✅ Deployment initiated!")
    return True

def setup_environment_variables():
    """Guide user through setting up environment variables"""
    print("\n⚙️  ENVIRONMENT VARIABLES SETUP")
    print("=" * 50)
    
    print("Please set the following environment variables in Railway dashboard:")
    print("1. Go to your Railway project dashboard")
    print("2. Click on your service")
    print("3. Go to 'Variables' tab")
    print("4. Add these variables:")
    
    env_vars = {
        'SECRET_KEY': 'Generate a new Django secret key',
        'DEBUG': 'False',
        'RAILWAY_ENVIRONMENT': 'production',
        'OPENROUTER_API_KEY': 'Your OpenRouter API key',
        'OPENROUTER_DEFAULT_MODEL': 'google/gemini-2.5-flash',
        'DJANGO_SUPERUSER_USERNAME': 'admin',
        'DJANGO_SUPERUSER_PASSWORD': 'Change this password!',
        'DJANGO_SUPERUSER_EMAIL': 'your-admin@email.com',
    }
    
    for key, description in env_vars.items():
        print(f"   • {key}: {description}")
    
    print("\nNote: Railway automatically provides DATABASE_URL for PostgreSQL")
    
def show_next_steps():
    """Show what to do after deployment"""
    print("\n🎉 DEPLOYMENT COMPLETE!")
    print("=" * 50)
    
    # Get Railway URL
    result = subprocess.run("railway domain", shell=True, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        url = result.stdout.strip()
        print(f"🌐 Your app is available at: {url}")
    else:
        print("🌐 Your app URL will be available in Railway dashboard")
    
    print("\n📋 NEXT STEPS:")
    print("1. ✅ Set environment variables in Railway dashboard")
    print("2. ✅ Wait for deployment to complete")
    print("3. ✅ Test your application")
    print("4. ✅ Check logs if there are any issues: railway logs")
    print("5. ✅ Access admin panel: https://your-app.railway.app/admin/")
    print("   Login: admin / (your password)")

def main():
    """Main deployment function"""
    print("🚀 RAILWAY DEPLOYMENT AUTOMATION")
    print("=" * 50)
    print("This script will help you deploy your RAG application to Railway.com")
    print("")
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Step 1: Check prerequisites
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return False
    
    # Step 2: Validate Django setup
    validate_django_setup()
    
    # Step 3: Setup Railway project
    if not setup_railway_project():
        print("\n❌ Failed to set up Railway project.")
        return False
    
    # Step 4: Deploy application
    if not deploy_application():
        print("\n❌ Deployment failed.")
        return False
    
    # Step 5: Show environment variables setup
    setup_environment_variables()
    
    # Step 6: Show next steps
    show_next_steps()
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
