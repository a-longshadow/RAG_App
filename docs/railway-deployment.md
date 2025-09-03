# Railway.com Deployment Guide

## 🚀 Deploy Django RAG System on Railway

This guide walks you through deploying your Django RAG application on Railway.com with PostgreSQL database.

### 📋 Prerequisites

- Railway.com account ([sign up here](https://railway.app))
- GitHub repository with your code
- OpenRouter API key

### 🛠️ Deployment Steps

#### 1. **Prepare Your Repository**

Ensure these files are in your repository:
- ✅ `nixpacks.toml` - Nixpacks configuration
- ✅ `Procfile` - Process definitions
- ✅ `requirements.txt` - Python dependencies (with gunicorn, dj-database-url, whitenoise)
- ✅ `django_rag/settings.py` - Updated with Railway configurations

#### 2. **Create Railway Project**

1. Go to [railway.app](https://railway.app) and sign in
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Choose your RAG repository

#### 3. **Add PostgreSQL Database**

1. In your Railway project dashboard, click **"New Service"**
2. Select **"Database"** → **"PostgreSQL"**
3. Railway will automatically create a PostgreSQL database
4. The `DATABASE_URL` environment variable will be automatically set

#### 4. **Configure Environment Variables**

In your Railway project settings, add these environment variables:

```bash
# Django Configuration
SECRET_KEY=your-super-secret-django-key-here
DEBUG=False
RAILWAY_ENVIRONMENT=production

# OpenRouter API (Required)
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
OPENROUTER_DEFAULT_MODEL=google/gemini-2.5-flash

# RAG System Settings
SIMILARITY_THRESHOLD=0.8
MAX_CHUNKS_RETURNED=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
MAX_FILE_SIZE_MB=5
EMBEDDINGS_MODEL=all-mpnet-base-v2
```

**Important Notes:**
- `DATABASE_URL` is automatically provided by Railway PostgreSQL
- Generate a new `SECRET_KEY` for production (don't use the default one)
- Keep `DEBUG=False` for production

#### 5. **Deploy the Application**

1. Railway will automatically start building when you connect your repo
2. The build process will:
   - Install Python 3.12
   - Install requirements from `requirements.txt`
   - Run `collectstatic` to gather static files
   - Run database migrations
   - Start the application with Gunicorn

#### 6. **Verify Deployment**

1. Once deployed, Railway will provide a public URL (e.g., `your-app.up.railway.app`)
2. Visit the URL to confirm your app is running
3. Test key functionality:
   - Document upload
   - Model selection
   - Query processing

### 🔧 Railway Configuration Files

#### `nixpacks.toml`
```toml
[variables]
NIXPACKS_PYTHON_VERSION = "3.12"
PYTHONPATH = "/app"

[phases.setup]
nixPkgs = ["python312", "postgresql", "pkg-config"]

[phases.install]
cmds = [
    "pip install --upgrade pip",
    "pip install -r requirements.txt"
]

[phases.build]
cmds = [
    "python manage.py collectstatic --noinput",
    "python manage.py migrate --noinput"
]

[start]
cmd = "gunicorn django_rag.wsgi:application --bind 0.0.0.0:$PORT --workers 4"
```

#### `Procfile`
```
web: gunicorn django_rag.wsgi:application --bind 0.0.0.0:$PORT --workers 4
release: python manage.py migrate --noinput
```

### 📊 Database Configuration

Railway PostgreSQL provides these automatically:
- **Host**: `postgres.railway.internal`
- **Port**: `5432`
- **Database**: `railway`
- **Username**: `postgres`
- **Password**: Auto-generated
- **DATABASE_URL**: Complete connection string

Your Django app will automatically use the `DATABASE_URL` when deployed.

### 🔐 Security Features

The deployment includes production security settings:
- HTTPS enforcement
- Secure cookies
- XSS protection
- Content type sniffing protection
- HSTS headers

### 📁 Static Files

Static files are handled by WhiteNoise middleware:
- CSS, JavaScript, and images are served efficiently
- Files are compressed and cached
- No additional CDN required

### 🚨 Troubleshooting

#### Common Issues:

1. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **Database Connection Errors**
   - Ensure PostgreSQL service is running
   - Check that `DATABASE_URL` is set

3. **Static Files Not Loading**
   - Run `python manage.py collectstatic` locally to test
   - Verify `STATIC_ROOT` and `STATIC_URL` settings

4. **Environment Variables**
   - Double-check all required variables are set
   - Ensure no typos in variable names

#### Debug Commands:

```bash
# Check logs in Railway dashboard
# View build logs and runtime logs

# Test locally with Railway environment
railway login
railway link
railway run python manage.py check --deploy
```

### 🎯 Production Checklist

Before going live:
- [ ] Set a strong `SECRET_KEY`
- [ ] Confirm `DEBUG=False`
- [ ] Test document upload functionality
- [ ] Verify OpenRouter API integration
- [ ] Test all major features
- [ ] Set up monitoring/logging
- [ ] Configure custom domain (optional)

### 📈 Scaling

Railway offers easy scaling options:
- **Vertical Scaling**: Increase CPU/RAM resources
- **Database Scaling**: Upgrade PostgreSQL plan
- **Multiple Regions**: Deploy in different geographical regions

### 💰 Cost Estimates

Railway pricing (as of 2025):
- **Hobby Plan**: $5/month (includes PostgreSQL)
- **Pro Plan**: Usage-based pricing
- **PostgreSQL**: Included in plans

Your RAG app should fit comfortably in the Hobby plan for development and small-scale production use.

### 🔗 Useful Links

- [Railway Documentation](https://docs.railway.app)
- [Nixpacks Documentation](https://nixpacks.com/docs)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)

---

## 🎉 Next Steps

After successful deployment:
1. Upload test documents
2. Configure your preferred AI models
3. Set up user accounts
4. Monitor performance and usage
5. Consider setting up a custom domain

Your Django RAG system is now production-ready on Railway! 🚀
