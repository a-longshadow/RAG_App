"""
Chat views for real-time conversation interface
"""
import json
import time
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Document
from .rag_engine import RAGQueryEngine
from .conversation_handler import get_conversation_handler
from .openrouter_client import get_openrouter_client

logger = logging.getLogger(__name__)


@login_required
def chat_interface(request):
    """
    Display the chat interface
    """
    # Get user stats
    stats = {
        'total_documents': Document.objects.filter(uploaded_by=request.user).count()
    }
    
    # Get selected model
    selected_model = request.session.get('selected_model')
    if not selected_model:
        try:
            client = get_openrouter_client()
            selected_model = client.default_model
            request.session['selected_model'] = selected_model
        except Exception as e:
            logger.warning(f"Could not get default model: {e}")
            selected_model = 'google/gemini-2.5-flash'
    
    context = {
        'stats': stats,
        'selected_model': selected_model,
    }
    
    return render(request, 'rag_app/chat.html', context)


@login_required
@require_http_methods(["POST"])
def chat_query(request):
    """
    Handle AJAX chat queries
    """
    try:
        data = json.loads(request.body)
        message = data.get('message', '').strip()
        conversation_id = data.get('conversation_id')
        
        if not message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            })
        
        start_time = time.time()
        
        # Get selected model from session
        selected_model = request.session.get('selected_model')
        if not selected_model:
            try:
                client = get_openrouter_client()
                selected_model = client.default_model
            except Exception:
                selected_model = 'google/gemini-2.5-flash'
        
        # Check if this is a conversational query first
        conversation_handler = get_conversation_handler()
        user_has_docs = Document.objects.filter(uploaded_by=request.user).exists()
        
        # First try to get an LLM-generated conversational response
        conversational_response = None
        try:
            # For greetings and simple queries, use the LLM for more natural responses
            if conversation_handler.classify_query(message) in ['greeting', 'hear_me', 'capability']:
                client = get_openrouter_client()
                
                # Create a more dynamic prompt
                doc_info = f"The user has {Document.objects.filter(uploaded_by=request.user).count()} documents uploaded" if user_has_docs else "The user hasn't uploaded any documents yet"
                
                prompt = f"""You are a helpful AI assistant for a document search system. 
                
User's message: "{message}"
Context: {doc_info}

Respond naturally and helpfully. If it's a greeting, be welcoming and explain what you can do. If they're asking about capabilities, explain the document search features. Keep it conversational and friendly, not robotic.

Be specific about the document search capabilities:
- Semantic search across uploaded documents
- AI-powered answers with source citations
- Support for PDFs, Word docs, and other formats
- Multiple AI model options (Claude, GPT-4, Gemini, etc.)

Keep your response concise but informative."""

                # Try with rate limiting protection
                try:
                    llm_response = client.simple_chat(
                        prompt=prompt,
                        model=selected_model,
                        max_tokens=200,
                        temperature=0.7
                    )
                    
                    if llm_response and llm_response.strip():
                        conversational_response = llm_response.strip()
                        
                except Exception as llm_error:
                    logger.warning(f"LLM call failed: {llm_error}")
                    # Fall back to conversation handler
                    conversational_response = conversation_handler.handle_conversational_query(message, request.user)
        
        except Exception as e:
            logger.warning(f"LLM conversational response failed: {e}")
            # Fall back to conversation handler
            conversational_response = conversation_handler.handle_conversational_query(message, request.user)
        
        # If we got an LLM conversational response, use it
        if conversational_response:
            total_time = time.time() - start_time
            return JsonResponse({
                'success': True,
                'response': conversational_response,
                'model': selected_model,
                'total_time': round(total_time, 2),
                'is_conversational': True,
                'sources': []
            })
        
        # Otherwise, proceed with RAG processing for document queries
        logger.info(f"Processing RAG query: {message}")
        
        engine = RAGQueryEngine()
        
        # Override configuration with selected model
        if selected_model:
            engine.config.llm_model = selected_model
        
        # Process the query
        response = engine.query(
            query_text=message,
            user=request.user,
            session_id=conversation_id
        )
        
        # Format sources for frontend
        sources = []
        for search_result in response.source_chunks:
            sources.append({
                'document_title': search_result.chunk.document.title,
                'page_number': search_result.chunk.page_number if hasattr(search_result.chunk, 'page_number') else None,
                'similarity': round(search_result.similarity_score, 3)
            })
        
        total_time = time.time() - start_time
        
        return JsonResponse({
            'success': True,
            'response': response.response,
            'model': response.llm_model,
            'total_time': round(total_time, 2),
            'search_time': round(response.search_time, 2),
            'llm_time': round(response.llm_time, 2),
            'chunks_found': response.total_chunks_found,
            'sources': sources,
            'is_conversational': False
        })
        
    except Exception as e:
        logger.error(f"Chat query failed: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
