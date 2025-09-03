# 🚀 Complete Deployment Guide - Railway.com + Localhost

## **📋 OVERVIEW**

This guide provides step-by-step instructions for deploying your RAG application to both localhost and Railway.com using PostgreSQL and modern best practices for 2025.

## **🎯 AUTOMATIC DUAL ENVIRONMENT SUPPORT**

Your application is now configured to automatically detect and adapt to both environments:

- **🏠 Localhost**: Uses local PostgreSQL with component environment variables
- **☁️ Railway**: Uses Railway's DATABASE_URL with automatic environment detection

## **⚙️ CONFIGURATION FILES CREATED**

### **Railway Configuration**
- ✅ `nixpacks.toml` - Railway build configuration with PostgreSQL 17
- ✅ `Procfile` - Process definitions with optimized Gunicorn settings
- ✅ `runtime.txt` - Python 3.12.10 runtime specification
- ✅ `.env.railway` - Production environment variables template

### **Deployment Automation**
- ✅ `deploy_to_railway.py` - Automated deployment script
- ✅ Updated `django_rag/settings.py` - Smart environment detection
- ✅ Enhanced `.env.example` - Comprehensive configuration template

## **🚀 QUICK DEPLOYMENT (30 SECONDS)**

### **Option A: Automated Deployment**
```bash
# Install Railway CLI (one-time setup)
npm install -g @railway/cli

# Run automated deployment
python deploy_to_railway.py
```

### **Option B: Manual Deployment**
```bash
# 1. Login to Railway
railway login

# 2. Create/link project
railway init

# 3. Add PostgreSQL
railway add postgresql

# 4. Deploy
railway up
```

## **📊 STEP-BY-STEP DEPLOYMENT PROCESS**

### **🔧 Step 1: Prerequisites**

**Local Environment:**
- ✅ Python 3.12+ installed
- ✅ PostgreSQL 17 running locally
- ✅ Virtual environment activated
- ✅ Dependencies installed (`pip install -r requirements.txt`)

**Railway Deployment:**
- ✅ GitHub account and repository
- ✅ Railway.com account
- ✅ OpenRouter API key

### **🗄️ Step 2: Database Setup**

**Localhost PostgreSQL:**
```bash
# Ensure PostgreSQL is running
brew services start postgresql

# Create database if needed
createdb rag_system

# Test connection
python manage.py check --database default
```

**Railway PostgreSQL:**
- Railway automatically provisions PostgreSQL 17
- DATABASE_URL provided automatically
- No manual database creation needed

### **⚙️ Step 3: Environment Variables**

**Localhost (`.env` file):**
```bash
# Copy and customize
cp .env.example .env

# Essential variables:
OPENROUTER_API_KEY=your_actual_api_key
DB_NAME=rag_system
DB_USER=joe
DEBUG=True
```

**Railway Dashboard Variables:**
```bash
# Required production variables:
SECRET_KEY=generate-new-django-secret-key
DEBUG=False
RAILWAY_ENVIRONMENT=production
OPENROUTER_API_KEY=your_actual_api_key
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=secure_password_123
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
```

### **🚀 Step 4: Deploy to Railway**

**Using Automated Script:**
```bash
python deploy_to_railway.py
```

**Manual Process:**
```bash
# 1. Commit all changes
git add .
git commit -m "Deploy to Railway"
git push origin main

# 2. Login to Railway
railway login

# 3. Link/create project
railway link  # or railway init for new project

# 4. Add PostgreSQL service
railway add postgresql

# 5. Set environment variables in Railway dashboard
# (See variables list above)

# 6. Deploy
railway up
```

### **✅ Step 5: Post-Deployment Verification**

**Localhost Testing:**
```bash
# Start local server
python manage.py runserver

# Test endpoints
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/admin/

# Run system health check
python test_rag_system.py
```

**Railway Testing:**
```bash
# Check deployment status
railway status

# View logs
railway logs

# Test live URL (provided by Railway)
curl https://your-app.railway.app/
```

## **🔍 ENVIRONMENT DETECTION LOGIC**

Your application automatically detects the environment:

```python
# settings.py logic:
if os.getenv('DATABASE_URL'):
    # Railway deployment detected
    # Uses DATABASE_URL with dj_database_url
    # Enables production security settings
else:
    # Local development detected  
    # Uses component database variables
    # Maintains development settings
```

## **🌐 ACCESS POINTS**

### **Localhost Development**
- **Home**: http://127.0.0.1:8000/
- **Chat**: http://127.0.0.1:8000/chat/
- **Admin**: http://127.0.0.1:8000/admin/
- **Models**: http://127.0.0.1:8000/models/
- **Analytics**: http://127.0.0.1:8000/analytics/

### **Railway Production**
- **Home**: https://your-app.railway.app/
- **Chat**: https://your-app.railway.app/chat/
- **Admin**: https://your-app.railway.app/admin/
- **API**: https://your-app.railway.app/api/

## **🔧 TROUBLESHOOTING**

### **Common Issues & Solutions**

**Database Connection Errors:**
```bash
# Localhost: Check PostgreSQL is running
brew services restart postgresql

# Railway: Verify DATABASE_URL is set
railway variables
```

**Static Files Not Loading:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify WhiteNoise is in MIDDLEWARE
```

**Environment Variable Issues:**
```bash
# Check local environment
python -c "import os; print('API Key:', bool(os.getenv('OPENROUTER_API_KEY')))"

# Check Railway environment
railway run python -c "import os; print(os.getenv('RAILWAY_ENVIRONMENT'))"
```

**Deployment Failures:**
```bash
# Check Railway logs
railway logs --tail

# Verify Procfile syntax
cat Procfile

# Test migrations locally
python manage.py migrate --dry-run
```

### **Debug Commands**

```bash
# Local system health check
python test_rag_system.py

# Check Django configuration
python manage.py check --deploy

# Validate database connection
python manage.py dbshell

# Test OpenRouter connection
python manage.py test_api

# Railway-specific debugging
railway logs --tail
railway run python manage.py check
railway run python test_rag_system.py
```

## **🔐 SECURITY CONSIDERATIONS**

### **Production Security Features**
- ✅ HTTPS enforcement (Railway automatic)
- ✅ Secure cookies in production
- ✅ XSS protection headers
- ✅ CSRF protection with trusted origins
- ✅ Content type sniffing protection
- ✅ HSTS headers for secure connections

### **Environment-Specific Settings**
```python
# Development (DEBUG=True)
- Detailed error pages
- Local file serving
- Relaxed security headers

# Production (RAILWAY_ENVIRONMENT=production)
- Minimal error information
- Secure cookie handling
- Enhanced security headers
- Static file compression
```

## **📈 PERFORMANCE OPTIMIZATIONS**

### **Database Connection Management**
- Connection pooling with `conn_max_age=600`
- Health checks for connection reliability
- Timeout settings for problematic connections

### **Static File Serving**
- WhiteNoise compression and caching
- Far-future expires headers
- Gzip compression for text assets

### **Gunicorn Configuration**
- 4 workers for optimal performance
- Connection limits and timeouts
- Request recycling for memory management

## **🎯 MONITORING & LOGS**

### **Railway Monitoring**
```bash
# Real-time logs
railway logs --tail

# Service status
railway status

# Resource usage
railway metrics

# Environment variables
railway variables
```

### **Application Health Checks**
```bash
# System health
python test_rag_system.py

# Database connectivity
python manage.py check --database default

# API functionality
curl -f https://your-app.railway.app/api/health/
```

## **🔄 CONTINUOUS DEPLOYMENT**

### **Automatic Deployments**
Railway automatically deploys when you push to your main branch:

```bash
# Make changes
git add .
git commit -m "Feature update"
git push origin main

# Railway automatically:
# 1. Detects changes
# 2. Builds with nixpacks.toml
# 3. Runs migrations
# 4. Deploys new version
# 5. Updates URL
```

### **Manual Deployments**
```bash
# Force deployment
railway up

# Deploy specific branch
railway up --branch feature-branch
```

## **📋 DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] All code committed and pushed to GitHub
- [ ] Environment variables configured
- [ ] OpenRouter API key obtained
- [ ] Local testing completed
- [ ] Requirements.txt updated

### **Railway Setup**
- [ ] Railway account created
- [ ] Project created/linked
- [ ] PostgreSQL service added
- [ ] Environment variables set
- [ ] Domain configured (optional)

### **Post-Deployment**
- [ ] Application loads successfully
- [ ] Admin panel accessible
- [ ] Document upload works
- [ ] AI chat functional
- [ ] Analytics dashboard loads
- [ ] All features tested

## **🎉 NEXT STEPS**

After successful deployment:

1. **Configure Custom Domain** (Optional)
   - Add your domain in Railway dashboard
   - Update DNS settings
   - SSL certificate auto-generated

2. **Monitor Performance**
   - Use Railway metrics
   - Set up error tracking
   - Monitor resource usage

3. **Scale as Needed**
   - Upgrade Railway plan
   - Add more workers
   - Implement caching

4. **Backup Strategy**
   - Regular database backups
   - Environment variables backup
   - Code repository maintenance

**Your RAG application is now ready for production with automatic dual-environment support!** 🚀
