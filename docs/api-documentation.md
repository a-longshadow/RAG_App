# API Documentation - RAG Document System

## 🔌 **API OVERVIEW**

**Base URL**: `http://127.0.0.1:8000/`
**Status**: ✅ Production Ready (Stage 5 Complete)
**Authentication**: Django session-based authentication
**Response Format**: JSON
**Interfaces**: Dual interface strategy (Chat + Advanced Query)

## 📋 **CURRENT API ENDPOINTS**

### **Chat Interface API**

#### Real-Time Chat Query
```http
POST /chat/query/
Content-Type: application/json

{
  "message": "What is TAT in the documents?",
  "conversation_id": "uuid-string"
}
```

**Response (Document-Based):**
```json
{
  "success": true,
  "response": "Based on your documents, TAT stands for...",
  "model": "google/gemini-2.5-flash",
  "total_time": 1.45,
  "search_time": 0.12,
  "llm_time": 1.33,
  "chunks_found": 3,
  "is_conversational": false,
  "sources": [
    {
      "document_title": "Meeting Notes",
      "page_number": 2,
      "similarity": 0.142
    }
  ]
}
```

**Response (Conversational):**
```json
{
  "success": true,
  "response": "Hello! I'm your AI document assistant...",
  "model": "google/gemini-2.5-flash", 
  "total_time": 0.85,
  "is_conversational": true,
  "sources": []
}
```

**Error Response:**
```json
{
  "success": false,
  "error": "Rate limit exceeded. Please wait a moment and try again."
}
```

### **Advanced Query Interface API**

#### Detailed Document Query
```http
POST /query/
Content-Type: application/x-www-form-urlencoded

query=What is TAT?
similarity_threshold=0.1
max_results=5
documents=doc-id-1,doc-id-2
model=anthropic/claude-3-sonnet
```

**Response:**
```json
{
  "query": "What is TAT?",
  "response": "TAT stands for Turn Around Time...",
  "source_chunks": [
    {
      "chunk_id": "uuid",
      "content": "TAT (Turn Around Time) refers to...",
      "similarity_score": 0.142,
      "document_title": "Process Documentation",
      "document_id": "uuid",
      "position_start": 1250,
      "position_end": 1750,
      "word_count": 85
    }
  ],
  "total_chunks_found": 3,
  "search_time": 0.030,
  "llm_time": 1.200,
  "total_time": 1.275,
  "llm_model": "anthropic/claude-3-sonnet",
  "prompt_tokens": 850,
  "completion_tokens": 120,
  "total_cost": 0.0025
}
```

### **Document Management**

#### Upload Document
```http
POST /upload_document/
Content-Type: multipart/form-data

Form Data:
- file: Document file (JSON, MD, PDF, CSV)
- title: Document title (optional)
```

**Response:**
```json
{
  "success": true,
  "message": "Document uploaded successfully",
  "document_id": 123,
  "chunks_created": 15,
  "processing_time": 2.34
}
```

#### List Documents
```http
GET /documents/
```

**Response:**
```json
{
  "documents": [
    {
      "id": 123,
      "title": "API Documentation",
      "file_type": "md",
      "chunk_count": 15,
      "uploaded_at": "2025-01-24T10:30:00Z",
      "file_size": 1024
    }
  ],
  "total_count": 1
}
```

#### Delete Document
```http
DELETE /documents/{id}/delete/
```

**Response:**
```json
{
  "success": true,
  "message": "Document deleted successfully"
}
```

### **Model Management**

#### List Available Models
```http
GET /models/api/
```

**Response:**
```json
{
  "models": [
    {
      "id": "anthropic/claude-3-haiku",
      "name": "Claude 3 Haiku",
      "provider": "Anthropic",
      "context_length": 200000,
      "pricing": {
        "prompt": 0.00025,
        "completion": 0.00125
      },
      "description": "Fast and efficient model for most tasks"
    }
  ],
  "total_count": 156,
  "categories": ["chat", "completion", "reasoning"]
}
```

#### Test Model
```http
POST /models/test/
Content-Type: application/json

{
  "model_id": "anthropic/claude-3-haiku",
  "test_message": "Hello, how are you?"
}
```

**Response:**
```json
{
  "success": true,
  "model_id": "anthropic/claude-3-haiku",
  "response": "Hello! I'm doing well, thank you for asking...",
  "response_time": 1.23,
  "tokens_used": {
    "prompt": 8,
    "completion": 15
  },
  "cost_estimate": 0.0001875
}
```

### **Query Processing**

#### Query Documents
```http
POST /query_documents/
Content-Type: application/json

{
  "query": "What is the API rate limit?",
  "selected_documents": [123, 456],
  "model_id": "anthropic/claude-3-haiku",
  "max_results": 5
}
```

**Response:**
```json
{
  "success": true,
  "query": "What is the API rate limit?",
  "response": "Based on the documentation, the API rate limit is...",
  "sources": [
    {
      "document_id": 123,
      "document_title": "API Documentation",
      "chunk_text": "Rate limiting is implemented...",
      "similarity_score": 0.89,
      "chunk_index": 5
    }
  ],
  "model_used": "anthropic/claude-3-haiku",
  "processing_time": 2.45,
  "session_id": "session_abc123"
}
```

### **Analytics**

#### Get Analytics Dashboard Data
```http
GET /analytics/api/
```

**Response:**
```json
{
  "summary": {
    "total_queries": 150,
    "total_documents": 12,
    "avg_response_time": 2.34,
    "most_used_model": "anthropic/claude-3-haiku"
  },
  "query_stats": {
    "queries_last_24h": 25,
    "avg_similarity_score": 0.82,
    "success_rate": 98.5
  },
  "model_usage": [
    {
      "model_id": "anthropic/claude-3-haiku",
      "usage_count": 89,
      "avg_response_time": 1.8,
      "success_rate": 99.2
    }
  ],
  "document_stats": [
    {
      "document_id": 123,
      "title": "API Documentation",
      "query_count": 45,
      "avg_relevance": 0.85
    }
  ]
}
```

#### Get Conversation History
```http
GET /conversations/api/
```

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "session_abc123",
      "started_at": "2025-01-24T10:30:00Z",
      "query_count": 5,
      "last_activity": "2025-01-24T10:45:00Z",
      "queries": [
        {
          "query": "What is the API rate limit?",
          "response_preview": "Based on the documentation...",
          "model_used": "anthropic/claude-3-haiku",
          "timestamp": "2025-01-24T10:35:00Z",
          "response_time": 2.3
        }
      ]
    }
  ],
  "total_sessions": 25,
  "total_queries": 150
}
```

## 🔐 **AUTHENTICATION**

### Current Implementation
- **Session-based**: Uses Django's built-in session authentication
- **Admin Access**: Django admin panel for user management
- **CSRF Protection**: Required for all POST requests

### Future API Key Support
```http
Authorization: Bearer sk-rag-your-api-key-here
```

## ⚠️ **ERROR HANDLING**

### Standard Error Response
```json
{
  "success": false,
  "error": "Error description",
  "error_code": "INVALID_MODEL",
  "details": {
    "model_id": "invalid-model",
    "available_models": ["anthropic/claude-3-haiku", "..."]
  }
}
```

### Common Error Codes
- `INVALID_MODEL`: Model ID not found or unavailable
- `NO_DOCUMENTS`: No documents uploaded or selected
- `UPLOAD_FAILED`: Document processing failed
- `API_KEY_INVALID`: OpenRouter API key invalid
- `QUERY_FAILED`: Query processing encountered error
- `RATE_LIMITED`: Too many requests (if implemented)

## 📊 **RATE LIMITS**

### Current Limits
- **No hard limits**: Development environment
- **OpenRouter limits**: Based on your API key tier
- **File uploads**: 5MB per file, 10 files per session

### Production Recommendations
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643723400
```

## 🚀 **WEBHOOKS** (Future Feature)

### Query Completion Webhook
```http
POST {webhook_url}
Content-Type: application/json

{
  "event": "query.completed",
  "timestamp": "2025-01-24T10:35:00Z",
  "data": {
    "session_id": "session_abc123",
    "query": "What is the API rate limit?",
    "model_used": "anthropic/claude-3-haiku",
    "response_time": 2.3,
    "success": true
  }
}
```

## 📝 **REQUEST EXAMPLES**

### cURL Examples

**Upload Document:**
```bash
curl -X POST \
  http://127.0.0.1:8000/upload_document/ \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@documentation.md' \
  -F 'title=API Documentation'
```

**Query Documents:**
```bash
curl -X POST \
  http://127.0.0.1:8000/query_documents/ \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What is the API rate limit?",
    "selected_documents": [123],
    "model_id": "anthropic/claude-3-haiku"
  }'
```

### Python Examples

**Using requests library:**
```python
import requests

# Upload document
with open('documentation.md', 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:8000/upload_document/',
        files={'file': f},
        data={'title': 'API Documentation'}
    )

# Query documents
response = requests.post(
    'http://127.0.0.1:8000/query_documents/',
    json={
        'query': 'What is the API rate limit?',
        'selected_documents': [123],
        'model_id': 'anthropic/claude-3-haiku'
    }
)
```

### JavaScript Examples

**Using fetch API:**
```javascript
// Upload document
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('title', 'API Documentation');

const uploadResponse = await fetch('/upload_document/', {
    method: 'POST',
    body: formData
});

// Query documents
const queryResponse = await fetch('/query_documents/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        query: 'What is the API rate limit?',
        selected_documents: [123],
        model_id: 'anthropic/claude-3-haiku'
    })
});
```

## 🔧 **SDK & LIBRARIES**

### Python SDK (Planned)
```python
from rag_client import RAGClient

client = RAGClient(base_url='http://127.0.0.1:8000')

# Upload document
document = client.upload_document('path/to/file.md')

# Query documents
response = client.query(
    'What is the API rate limit?',
    documents=[document.id],
    model='anthropic/claude-3-haiku'
)
```

### Node.js Library (Planned)
```javascript
const { RAGClient } = require('@rag/client');

const client = new RAGClient('http://127.0.0.1:8000');

// Upload and query
const document = await client.uploadDocument('./file.md');
const response = await client.query('What is the API rate limit?', {
    documents: [document.id],
    model: 'anthropic/claude-3-haiku'
});
```

## 📚 **INTEGRATION EXAMPLES**

### Slack Bot Integration
```python
from slack_sdk import WebClient
import requests

def handle_slack_query(event):
    query = event['text']
    
    # Query RAG system
    response = requests.post('http://127.0.0.1:8000/query_documents/', 
        json={
            'query': query,
            'model_id': 'anthropic/claude-3-haiku'
        }
    )
    
    # Send response back to Slack
    slack_client.chat_postMessage(
        channel=event['channel'],
        text=response.json()['response']
    )
```

### Discord Bot Integration
```python
import discord
import requests

class RAGBot(discord.Client):
    async def on_message(self, message):
        if message.author == self.user:
            return
            
        if message.content.startswith('!ask'):
            query = message.content[5:]
            
            response = requests.post('http://127.0.0.1:8000/query_documents/', 
                json={'query': query, 'model_id': 'anthropic/claude-3-haiku'}
            )
            
            await message.channel.send(response.json()['response'])
```

## 🏗️ **ARCHITECTURE NOTES**

### Request Flow
1. **Authentication**: Session validation
2. **Rate Limiting**: Check user limits
3. **Validation**: Input sanitization
4. **Processing**: Core logic execution
5. **Response**: JSON formatting
6. **Logging**: Analytics tracking

### Database Queries
- All queries use Django ORM
- Vector similarity using pgvector
- Optimized indexes for performance
- Connection pooling recommended

### Caching Strategy
- Model list cached for 1 hour
- Document embeddings cached permanently
- Query results cached for 5 minutes
- Analytics data cached for 15 minutes

**API is production-ready with comprehensive endpoints!**
