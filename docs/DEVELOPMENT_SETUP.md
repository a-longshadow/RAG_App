# Development Environment Setup Guide

## 🚀 Quick Start

### Automated Setup (Recommended)
```bash
# Clone the repository
git clone <your-repo-url>
cd RAG

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env
# Edit .env with your OpenRouter API key

# Run automated setup
python setup_dev_environment.py
```

### Manual Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py ensure_superuser

# Initialize system settings
python manage.py init_settings

# Start development server
python manage.py runserver
```

## 🔐 Default Superuser Credentials

The system automatically creates a default superuser for development:

- **Username**: `admin`
- **Password**: `testpass123`
- **Email**: `admin@localhost.local`

These credentials are configured via environment variables in your `.env` file:

```bash
# Default Superuser Configuration
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=testpass123
DJANGO_SUPERUSER_EMAIL=admin@localhost.local
```

## 🛠️ Management Commands

### `ensure_superuser`
Creates a superuser from environment variables if it doesn't exist.

```bash
# Create superuser with default credentials
python manage.py ensure_superuser

# Skip creation if any superuser already exists
python manage.py ensure_superuser --skip-if-exists
```

### `init_settings`
Initializes system settings with values from environment variables.

```bash
python manage.py init_settings
```

## 📱 Access Points

After setup, your RAG system will be available at:

- **Web Interface**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Chat Interface**: http://127.0.0.1:8000/chat/
- **Advanced Query**: http://127.0.0.1:8000/query/
- **Analytics**: http://127.0.0.1:8000/analytics/

## 🔧 Environment Variables

### Required
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Optional (with defaults)
```bash
# Database
DB_NAME=rag_system
DB_USER=joe
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=django-insecure-temp-key-change-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# RAG Configuration
SIMILARITY_THRESHOLD=0.8
MAX_CHUNKS_RETURNED=50
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
MAX_FILE_SIZE_MB=5

# AI Model
OPENROUTER_DEFAULT_MODEL=google/gemini-2.5-flash
EMBEDDINGS_MODEL=all-mpnet-base-v2

# Superuser (for development)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=testpass123
DJANGO_SUPERUSER_EMAIL=admin@localhost.local
```

## 🎯 Troubleshooting

### "Session data corrupted" messages
This is normal during development and doesn't affect functionality. The admin login will still work.

### Missing dependencies error
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Database connection issues
```bash
# Check PostgreSQL is running
brew services restart postgresql

# Verify database exists
createdb rag_system
```

### OpenRouter API issues
1. Verify your API key in `.env`
2. Check internet connection
3. Try a different model in the interface

## 🔄 Reset Development Environment

To completely reset your development environment:

```bash
# Remove database (optional - will lose all data)
python manage.py flush

# Run setup again
python setup_dev_environment.py
```

## 📚 Next Steps

1. **Upload Documents**: Use the web interface to upload PDFs, Word docs, etc.
2. **Test Chat**: Try the conversational interface at `/chat/`
3. **Explore Models**: Check out 100+ AI models at `/models/`
4. **View Analytics**: Monitor performance at `/analytics/`
5. **API Integration**: Use the REST API endpoints for programmatic access

Your RAG system is now ready for development! 🎉
