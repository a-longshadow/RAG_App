# Django RAG MVP Implementation Plan

## 🎯 MVP Goal
Build a corporate Q&A system that replaces the n8n workflow with:
- Persistent PostgreSQL storage instead of in-memory
- Modern Tailwind UI instead of basic form
- Local embeddings instead of OpenAI API
- OpenRouter for LLM instead of OpenAI

## 📅 6-Day Implementation Schedule

---

## Day 1: Foundation Setup (6-8 hours)

### Morning (3-4 hours): Django Project Setup
```bash
# 1. Create Django project
mkdir django_rag && cd django_rag
python -m venv venv
source venv/bin/activate  # macOS
pip install Django==4.2 python-dotenv

# 2. Initialize project
django-admin startproject django_rag .
python manage.py startapp rag_app

# 3. Create .env file
touch .env
```

### Afternoon (3-4 hours): Database Setup
```bash
# 1. Install PostgreSQL + pgvector
# Option A: Docker (recommended)
docker run --name postgres-rag -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:15
docker exec -it postgres-rag psql -U postgres -c "CREATE EXTENSION vector;"

# Option B: Local install
brew install postgresql
brew services start postgresql
createdb django_rag

# 2. Install Python dependencies
pip install psycopg2-binary sentence-transformers requests pandas PyPDF2 PyMuPDF
pip freeze > requirements.txt
```

### Key Files to Create:
- `.env` with all configuration
- `settings.py` updates for PostgreSQL
- Basic models in `rag_app/models.py`

**Success Check**: Django server runs, database connects

---

## Day 2: File Processing Pipeline (8-10 hours)

### Morning (4-5 hours): File Upload System
```python
# rag_app/models.py
class Document(models.Model):
    title = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)  # json, md, pdf, csv
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.IntegerField()

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    text = models.TextField()
    chunk_index = models.IntegerField()
    embedding = VectorField(dimensions=768)  # pgvector field
```

```python
# rag_app/views.py
def upload_file(request):
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        # Validate file size, type
        # Process file based on extension
        # Return success/error
```

### Afternoon (4-5 hours): File Processors
```python
# rag_app/file_processors.py
def process_markdown(file_content):
    # Extract text from MD
    
def process_json(file_content):
    # Recursively extract text values
    
def process_pdf(file_path):
    # PyPDF2 extraction with PyMuPDF fallback
    
def process_csv(file_path):
    # Pandas to structured text
```

**Success Check**: Upload any file type, extract text, basic chunking

---

## Day 3: Embeddings & Vector Storage (6-8 hours)

### Morning (3-4 hours): Local Embeddings Setup
```python
# rag_app/embeddings.py
from sentence_transformers import SentenceTransformer
import os

class EmbeddingService:
    def __init__(self):
        model_name = os.getenv('EMBEDDINGS_MODEL', 'all-mpnet-base-v2')
        self.model = SentenceTransformer(model_name)
    
    def embed_text(self, text_chunks):
        return self.model.encode(text_chunks)
```

### Afternoon (3-4 hours): Vector Storage & Search
```python
# rag_app/vector_service.py
from django.db import connection

def store_chunks_with_embeddings(document, text_chunks):
    embeddings = embedding_service.embed_text(text_chunks)
    for i, (chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
        DocumentChunk.objects.create(
            document=document,
            text=chunk,
            chunk_index=i,
            embedding=embedding.tolist()
        )

def similarity_search(query_text, threshold=0.8, limit=5):
    query_embedding = embedding_service.embed_text([query_text])[0]
    # PostgreSQL vector similarity query
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT text, 1 - (embedding <=> %s) as similarity
            FROM rag_app_documentchunk 
            WHERE 1 - (embedding <=> %s) > %s
            ORDER BY similarity DESC
            LIMIT %s
        """, [query_embedding.tolist(), query_embedding.tolist(), threshold, limit])
        return cursor.fetchall()
```

**Success Check**: Upload file → chunks stored with embeddings → similarity search works

---

## Day 4: OpenRouter Integration & RAG Pipeline (8-10 hours)

### Morning (4-5 hours): OpenRouter Client
```python
# rag_app/openrouter.py
import requests
import os

class OpenRouterClient:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        self.default_model = os.getenv('OPENROUTER_DEFAULT_MODEL', 'anthropic/claude-3-haiku')
    
    def get_available_models(self):
        response = requests.get(f"{self.base_url}/models", 
                              headers={"Authorization": f"Bearer {self.api_key}"})
        return response.json()
    
    def chat_completion(self, messages, model=None):
        model = model or self.default_model
        data = {
            "model": model,
            "messages": messages,
            "max_tokens": 1000,
            "temperature": 0.7
        }
        response = requests.post(f"{self.base_url}/chat/completions",
                               headers={"Authorization": f"Bearer {self.api_key}",
                                      "Content-Type": "application/json"},
                               json=data)
        return response.json()
```

### Afternoon (4-5 hours): RAG Pipeline
```python
# rag_app/rag_service.py
def rag_query(user_question, selected_model=None):
    # 1. Get similarity threshold from settings
    threshold = float(os.getenv('SIMILARITY_THRESHOLD', '0.8'))
    
    # 2. Search for similar chunks
    similar_chunks = similarity_search(user_question, threshold)
    
    # 3. If no high-similarity chunks, return "not found"
    if not similar_chunks:
        return "No information found in available documents."
    
    # 4. Format context
    context = "\n".join([chunk[0] for chunk in similar_chunks])
    
    # 5. Create messages for OpenRouter
    messages = [
        {
            "role": "system",
            "content": """You are a corporate data assistant. Answer ONLY based on provided context.
            If information is not in the context, say "Information not found in available documents."
            Always include dates when available. Be precise about employee names and projects.
            Do not guess or infer beyond what is explicitly stated."""
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {user_question}"
        }
    ]
    
    # 6. Get response from OpenRouter
    openrouter = OpenRouterClient()
    response = openrouter.chat_completion(messages, selected_model)
    
    return response["choices"][0]["message"]["content"]
```

**Success Check**: Ask question → retrieve relevant chunks → get accurate answer from OpenRouter

---

## Day 5: UI & Integration (6-8 hours)

### Morning (3-4 hours): Basic Templates with Tailwind
```html
<!-- rag_app/templates/base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Corporate RAG Q&A</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100">
    <div class="container mx-auto p-4">
        {% block content %}{% endblock %}
    </div>
</body>
</html>

<!-- rag_app/templates/upload.html -->
<div class="max-w-md mx-auto bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold mb-4">Upload Documents</h2>
    <form method="post" enctype="multipart/form-data">
        {% csrf_token %}
        <input type="file" name="file" accept=".json,.md,.pdf,.csv" 
               class="mb-4 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100">
        <button type="submit" class="w-full bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600">
            Upload
        </button>
    </form>
</div>

<!-- rag_app/templates/chat.html -->
<div class="max-w-4xl mx-auto">
    <div class="bg-white rounded-lg shadow-md p-6 mb-4">
        <h2 class="text-2xl font-bold mb-4">Ask Questions</h2>
        
        <!-- Model Selection -->
        <select id="model-select" class="mb-4 p-2 border rounded">
            <option value="anthropic/claude-3-haiku">Claude 3 Haiku</option>
            <option value="meta-llama/llama-3-8b-instruct">Llama 3 8B</option>
        </select>
        
        <!-- Chat Interface -->
        <div id="chat-messages" class="h-96 overflow-y-auto border p-4 mb-4"></div>
        
        <div class="flex">
            <input type="text" id="question-input" placeholder="Ask about employees, projects..." 
                   class="flex-1 p-2 border rounded-l">
            <button onclick="askQuestion()" class="bg-green-500 text-white px-4 py-2 rounded-r hover:bg-green-600">
                Ask
            </button>
        </div>
    </div>
</div>
```

### Afternoon (3-4 hours): JavaScript & API Endpoints
```python
# rag_app/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question')
        model = data.get('model')
        
        try:
            answer = rag_query(question, model)
            return JsonResponse({'answer': answer})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

def models_api(request):
    try:
        openrouter = OpenRouterClient()
        models = openrouter.get_available_models()
        return JsonResponse(models)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
```

```javascript
// Static/js/chat.js
async function askQuestion() {
    const question = document.getElementById('question-input').value;
    const model = document.getElementById('model-select').value;
    
    if (!question.trim()) return;
    
    // Add user message to chat
    addMessage('user', question);
    
    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({question, model})
        });
        
        const data = await response.json();
        addMessage('assistant', data.answer || data.error);
    } catch (error) {
        addMessage('assistant', 'Error: ' + error.message);
    }
    
    document.getElementById('question-input').value = '';
}

function addMessage(role, content) {
    const messagesDiv = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = role === 'user' ? 'text-right mb-2' : 'text-left mb-2';
    messageDiv.innerHTML = `
        <div class="${role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-200'} 
                     inline-block p-2 rounded max-w-xs">
            ${content}
        </div>
    `;
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
```

**Success Check**: Upload files via UI → ask questions in chat → get responses → model selection works

---

## Day 6: Testing & Polish (4-6 hours)

### Morning (2-3 hours): Parameter Tuning
```python
# Test with your company data
test_questions = [
    "What is John Smith working on?",
    "Who is the project manager for API migration?",
    "What projects started in July 2024?",
    "What is Sarah's current assignment?"
]

# Adjust .env parameters based on results
SIMILARITY_THRESHOLD=0.8  # Start here, adjust up for more precision
MAX_CHUNKS_RETURNED=5     # Increase if context seems incomplete  
CHUNK_SIZE=1000          # Adjust based on document structure
```

### Afternoon (2-3 hours): Error Handling & Documentation
```python
# Add comprehensive error handling
def upload_file(request):
    try:
        # Validate file size
        if uploaded_file.size > int(os.getenv('MAX_FILE_SIZE_MB', '5')) * 1024 * 1024:
            return JsonResponse({'error': 'File too large'}, status=400)
        
        # Validate file type
        allowed_types = ['.json', '.md', '.pdf', '.csv']
        if not any(uploaded_file.name.endswith(ext) for ext in allowed_types):
            return JsonResponse({'error': 'Unsupported file type'}, status=400)
            
        # Process file with fallback
        try:
            text = process_file(uploaded_file)
        except Exception as e:
            return JsonResponse({'error': f'File processing failed: {str(e)}'}, status=400)
            
        # Success response
        return JsonResponse({'message': 'File uploaded successfully'})
        
    except Exception as e:
        return JsonResponse({'error': 'Upload failed'}, status=500)
```

**Success Check**: All error cases handled gracefully, parameters tuned for your data

---

## 🔧 .env Configuration
```bash
# OpenRouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3-haiku

# Database
DB_NAME=django_rag
DB_USER=postgres
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432

# Django
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# RAG Parameters (tune these)
EMBEDDINGS_MODEL=all-mpnet-base-v2
SIMILARITY_THRESHOLD=0.8
MAX_CHUNKS_RETURNED=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
MAX_FILE_SIZE_MB=5
```

## 🎯 MVP Success Criteria
✅ Upload JSON/MD/PDF/CSV files  
✅ Files processed and stored in PostgreSQL  
✅ Local embeddings generated (no API calls)  
✅ Vector similarity search working  
✅ OpenRouter integration with model selection  
✅ Chat interface with corporate accuracy  
✅ Zero hallucination on company data  
✅ Modern Tailwind UI  
✅ All settings in .env file  

## 🚀 Ready to Start?
This plan gives you a complete, working RAG system that's superior to your n8n workflow in every way. Each day builds on the previous, with clear success checkpoints.

**Time to build!** 🛠️
