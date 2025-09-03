# Implementation Steps: OpenRouter Client & RAG Pipeline

## Step 1: Implement OpenRouter Client
**Timeline: 4-6 hours** ⚡

### What it involves:
```python
class OpenRouterClient:
    """Drop-in replacement for OpenAI client but with OpenRouter"""
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
    
    def get_available_models(self):
        """Fetch models like VS Code LLM selection"""
        # Returns list of models with metadata
    
    def chat_completion(self, messages, model):
        """Send chat request - identical to OpenAI API"""
        # Standard OpenAI-compatible API call
```

### High-level tasks:
1. **HTTP client setup** (30 mins)
   - requests library
   - error handling
   - timeout configuration

2. **Model management** (2 hours)
   - Fetch available models from OpenRouter API
   - Parse model metadata (name, pricing, context length)
   - Cache model list locally

3. **Chat completion** (1 hour)
   - Standard OpenAI-compatible chat endpoint
   - Message formatting
   - Response parsing

4. **VS Code-like model selector** (2-3 hours)
   - Django view to fetch models
   - Frontend dropdown component
   - Save user's model preference

### Challenges:
- ✅ **Minimal** - OpenRouter uses OpenAI API format
- ⚠️ **API key validation** - Handle invalid keys gracefully
- ⚠️ **Rate limits** - Basic retry logic

---

## Step 2: Build RAG Pipeline
**Timeline: 6-8 hours** ⚡

### What it involves:
```python
def rag_pipeline(user_question):
    # 1. Embed user question (local)
    question_embedding = embeddings_model.encode([user_question])
    
    # 2. Search vector DB (PostgreSQL + pgvector)
    similar_chunks = vector_db.similarity_search(question_embedding, top_k=5)
    
    # 3. Build context from chunks
    context = format_retrieved_chunks(similar_chunks)
    
    # 4. Generate response (OpenRouter)
    response = openrouter_client.chat_completion(
        messages=build_prompt(context, user_question),
        model=user_selected_model
    )
    
    return response
```

### High-level tasks:

#### A. Vector Database Operations (2-3 hours)
```python
# PostgreSQL + pgvector setup
- Vector similarity search queries
- Indexing for performance
- Chunk storage with metadata
```

#### B. Text Processing Pipeline (2 hours)
```python
# Document → Chunks → Embeddings → Storage
def process_document(file_content):
    chunks = split_text(file_content)  # Smart chunking
    embeddings = model.encode(chunks)  # Local embedding
    store_in_db(chunks, embeddings)    # Save to PostgreSQL
```

#### C. Retrieval Logic (1-2 hours)
```python
# Query → Similar chunks → Context
def retrieve_context(question):
    embedding = embed_question(question)
    chunks = search_similar(embedding, top_k=5)
    return format_context(chunks)
```

#### D. Response Generation (1 hour)
```python
# Context + Question → OpenRouter → Answer
def generate_response(context, question, model):
    prompt = f"Context: {context}\n\nQuestion: {question}"
    return openrouter_client.chat(prompt, model)
```

### Challenges:

#### 🟡 **Medium Complexity:**
- **Chunking strategy** - How to split text optimally
- **Vector search tuning** - Finding right similarity threshold
- **Context formatting** - How to present retrieved chunks to LLM

#### 🟢 **Low Risk:**
- **Embedding generation** - sentence-transformers handles this
- **OpenRouter integration** - Standard REST API
- **PostgreSQL queries** - Well-documented pgvector usage

---

## Combined Timeline: 10-14 hours (1.5-2 days)

### Day 1 (6-8 hours):
- Morning: OpenRouter client implementation
- Afternoon: Vector database setup + basic RAG pipeline

### Day 2 (4-6 hours):
- Morning: Fine-tune chunking and retrieval
- Afternoon: Integration testing + UI connection

---

## Risk Assessment: 🟢 **LOW RISK**

### Why it's straightforward:
1. **OpenRouter = OpenAI API** - Same interface, different URL
2. **sentence-transformers** - Mature, well-documented
3. **pgvector** - Proven PostgreSQL extension
4. **Django** - Handles HTTP/DB stuff automatically

### Potential gotchas:
- **Chunking logic** - Might need 2-3 iterations to get right
- **Vector search relevance** - May need to tune similarity thresholds
- **OpenRouter rate limits** - Need basic retry logic

### Fallback plan:
- Start with simple 500-char chunks
- Use default pgvector similarity search
- Add retry wrapper for OpenRouter calls

---

## Success Metrics:

After 1.5-2 days, you should have:
✅ Upload JSON/MD file → chunks stored in vector DB
✅ Ask question → retrieve relevant chunks
✅ Generate answer using OpenRouter model of choice
✅ Basic web interface for file upload + chat

**Bottom line:** This is very achievable in the timeline. The components are well-established and the integration points are straightforward.
