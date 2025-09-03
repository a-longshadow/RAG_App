# Stage 4: RAG Query Engine - Implementation Guide

## Overview

Stage 4 implements the complete RAG (Retrieval-Augmented Generation) query engine that combines semantic search with Large Language Model (LLM) response generation. This stage provides both web interface and API access to query documents using natural language.

## Features Implemented

### 🔍 Semantic Search Engine
- **Vector Similarity Search**: Uses pgvector with cosine distance for finding relevant document chunks
- **Configurable Thresholds**: Adjustable similarity thresholds for filtering results
- **Multi-document Support**: Search across all user documents or specific document sets
- **Ranking System**: Results ranked by similarity score with metadata

### 🤖 LLM Integration
- **OpenRouter API**: Integration with multiple LLM providers through OpenRouter
- **Model Selection**: Support for various models (Claude, GPT, etc.)
- **Prompt Engineering**: Structured prompts with context and instructions
- **Token Tracking**: Monitor usage and costs for different models

### 🌐 Web Interface
- **Query Form**: User-friendly interface for submitting questions
- **Results Display**: Comprehensive results with AI response and source chunks
- **Performance Metrics**: Real-time display of search and generation times
- **Source Attribution**: Clear links to source documents and chunk positions

### 📡 API Endpoints
- **RESTful API**: JSON-based query processing for programmatic access
- **Authentication Support**: User-based document filtering
- **Error Handling**: Comprehensive error responses and fallback mechanisms
- **Performance Tracking**: Detailed timing and usage metrics

## Architecture

### Core Components

#### 1. RAG Query Engine (`rag_engine.py`)
```python
class RAGQueryEngine:
    """Main RAG processing engine"""
    
    # Configuration management
    def __init__(self, config: RAGConfig)
    
    # Query processing pipeline
    def query(self, query_text: str, user: User) -> RAGResponse
    
    # Component methods
    def generate_query_embedding(self, query: str) -> np.ndarray
    def search_similar_chunks(self, embedding: np.ndarray) -> List[SearchResult]
    def assemble_context(self, results: List[SearchResult]) -> str
    def generate_llm_response(self, prompt: str) -> Tuple[str, Dict]
```

#### 2. Configuration System
- **Database Settings**: Stored in `SystemSettings` model for dynamic configuration
- **Environment Variables**: Support for `.env` file configuration
- **Default Values**: Sensible defaults for all parameters

#### 3. Data Models
- **QueryLog**: Complete logging of queries, responses, and performance metrics
- **SearchResult**: Structured representation of search results with metadata
- **RAGResponse**: Complete response object with timing and usage information

### Processing Pipeline

```
User Query → Query Embedding → Semantic Search → Context Assembly → LLM Generation → Response
     ↓              ↓               ↓                ↓               ↓            ↓
   Logging    Vector Model    Similarity Calc   Prompt Build    OpenRouter    Query Log
```

## Configuration

### System Settings

The RAG engine uses the following configurable parameters:

```python
# Similarity and Search
rag_similarity_threshold = 0.3      # Minimum similarity for chunk inclusion
rag_max_chunks = 5                  # Maximum chunks to include in context
rag_max_context_length = 4000       # Maximum character length for context

# LLM Configuration  
rag_llm_model = "anthropic/claude-3-sonnet"  # OpenRouter model identifier
rag_temperature = 0.7               # Response creativity (0.0-2.0)
rag_max_tokens = 1000              # Maximum response length

# Processing Options
rag_include_metadata = true         # Include document metadata in context
```

### Environment Variables

Create a `.env` file from `.env.example`:

```bash
# Required for LLM functionality
OPENROUTER_API_KEY=your_api_key_here

# Optional overrides
RAG_SIMILARITY_THRESHOLD=0.3
RAG_LLM_MODEL=anthropic/claude-3-sonnet
```

## Usage

### Web Interface

1. **Navigate to Home Page**: http://127.0.0.1:8000/
2. **Submit Query**: Use the query form with your question
3. **View Results**: See AI response with source attribution
4. **Adjust Parameters**: Modify similarity threshold and result limits

### API Access

#### Query Endpoint
```bash
POST /api/query/
Content-Type: application/json

{
    "query": "What meetings are scheduled with Young?",
    "similarity_threshold": 0.3,
    "max_results": 5
}
```

#### Response Format
```json
{
    "query": "What meetings are scheduled with Young?",
    "response": "Based on the documents, there is a meeting scheduled...",
    "source_chunks": [
        {
            "chunk_id": "uuid",
            "content": "Meeting content...",
            "similarity_score": 0.482,
            "document_title": "Document Name",
            "position_start": 1250,
            "position_end": 1750
        }
    ],
    "total_chunks_found": 5,
    "search_time": 0.030,
    "llm_time": 0.800,
    "total_time": 0.875,
    "prompt_tokens": 500,
    "completion_tokens": 150,
    "total_cost": 0.002
}
```

### Python Integration

```python
from rag_app.rag_engine import quick_query

# Simple query
response = quick_query("What documents discuss AI?", user=request.user)
print(response.response)

# Advanced usage
from rag_app.rag_engine import RAGQueryEngine

engine = RAGQueryEngine()
engine.config.similarity_threshold = 0.4
response = engine.query("Complex question about documents", user=user)
```

## Testing

### Management Commands

```bash
# Test semantic search only
python manage.py test_search --user-id 2 --query "Your question"

# Test complete RAG pipeline with mock LLM
python manage.py test_rag_pipeline --user-id 2 --threshold 0.3

# Test API endpoint
python manage.py test_api_mock --query "Your question"
```

### Manual Testing

1. **Upload Documents**: Ensure documents are processed and have embeddings
2. **Submit Queries**: Test various query types and complexity levels
3. **Check Performance**: Monitor response times and accuracy
4. **Verify Logging**: Confirm queries are logged in Django admin

## Performance Optimization

### Similarity Thresholds
- **0.2-0.3**: Very inclusive, good for exploratory queries
- **0.4-0.5**: Balanced relevance and recall
- **0.6+**: High precision, may miss relevant content

### Context Management
- **Chunk Limits**: Balance context richness with token limits
- **Context Length**: Adjust based on LLM model capabilities
- **Metadata Inclusion**: Toggle for cleaner or richer context

### Cost Management
- **Model Selection**: Choose cost-effective models for your use case
- **Token Limits**: Set appropriate maximum response lengths
- **Caching**: Consider caching for repeated queries

## Error Handling

### Fallback Mechanisms
1. **No Embeddings**: Falls back to simple text search
2. **LLM Failure**: Returns search results with error message
3. **Network Issues**: Graceful degradation with offline functionality
4. **Configuration Errors**: Default values prevent system failures

### Monitoring
- **Query Logging**: All queries logged with performance metrics
- **Error Tracking**: Failed queries logged with error details
- **Usage Analytics**: Token usage and cost tracking
- **Performance Metrics**: Response time and accuracy monitoring

## Integration with Other Stages

### Stage 3 Integration
- Uses document chunks and embeddings from document processing
- Leverages existing vector storage and similarity search
- Maintains user isolation and access control

### Future Enhancements (Stage 5-6)
- Advanced query routing and intent detection
- Multi-modal document support (images, tables)
- Conversation history and context management
- User feedback integration for result improvement

## Troubleshooting

### Common Issues

#### "No chunks found above similarity threshold"
- **Solution**: Lower similarity threshold or check document processing
- **Command**: `python manage.py test_search --threshold 0.1`

#### "OpenRouter API error: 401 Unauthorized"
- **Solution**: Set OPENROUTER_API_KEY environment variable
- **Alternative**: Use mock testing commands for development

#### "DocumentChunk object has no attribute 'position_start'"
- **Solution**: Field mapping corrected in current version
- **Check**: Ensure database migrations are applied

### Debug Commands

```bash
# Check available chunks and embeddings
python manage.py shell -c "
from rag_app.models import DocumentChunk, Embedding
print(f'Chunks: {DocumentChunk.objects.count()}')
print(f'Embeddings: {Embedding.objects.count()}')
"

# Test embedding generation
python manage.py test_search --query 'test' --user-id 2

# Verify system settings
python manage.py shell -c "
from rag_app.models import SystemSettings
for setting in SystemSettings.objects.all():
    print(f'{setting.key}: {setting.value}')
"
```

## Security Considerations

### API Security
- **Authentication**: User-based access control for documents
- **Rate Limiting**: Consider implementing for production use
- **Input Validation**: Query sanitization and length limits
- **CORS Headers**: Configure for cross-origin requests if needed

### Data Privacy
- **User Isolation**: Queries only access user's documents
- **Logging**: Sensitive information handling in query logs
- **API Keys**: Secure storage of OpenRouter credentials
- **Session Management**: Proper session handling for web interface

## Next Steps

With Stage 4 complete, you have a fully functional RAG system. Consider these enhancements:

1. **Production Deployment**: Configure for production environment
2. **Advanced Features**: Implement conversation history and context
3. **User Feedback**: Add rating and feedback systems
4. **Analytics Dashboard**: Create usage and performance dashboards
5. **API Documentation**: Generate comprehensive API documentation
6. **Mobile Interface**: Responsive design improvements for mobile

The RAG query engine provides a solid foundation for intelligent document querying and can be extended to support more advanced use cases as your requirements evolve.
