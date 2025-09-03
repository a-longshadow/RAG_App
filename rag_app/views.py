from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import json
import threading
import time
import logging

from .models import Document, DocumentChunk, Embedding, QueryLog
from .forms import DocumentUploadForm, QueryForm, DocumentSearchForm
from .document_processor import get_document_processor
from .embedding_utils import get_embedding_generator
from .rag_engine import RAGQueryEngine, quick_query
from .openrouter_client import get_openrouter_client
from .conversation_handler import get_conversation_handler

# Configure logging
logger = logging.getLogger(__name__)


def home_view(request):
    """
    Home page with upload form and recent documents
    """
    # Get recent documents
    recent_docs = Document.objects.filter(
        uploaded_by=request.user if request.user.is_authenticated else None
    ).order_by('-uploaded_at')[:5] if request.user.is_authenticated else []
    
    # Get statistics
    stats = {}
    if request.user.is_authenticated:
        stats = {
            'total_documents': Document.objects.filter(uploaded_by=request.user).count(),
            'processed_documents': Document.objects.filter(uploaded_by=request.user, status='processed').count(),
            'processing_documents': Document.objects.filter(uploaded_by=request.user, status='processing').count(),
            'total_chunks': DocumentChunk.objects.filter(document__uploaded_by=request.user).count(),
            'total_embeddings': Embedding.objects.filter(chunk__document__uploaded_by=request.user).count(),
        }
    
    # Get OpenRouter models for selection
    available_models = []
    selected_model = None
    if request.user.is_authenticated:
        try:
            client = get_openrouter_client()
            available_models = client.get_available_models()
            selected_model = request.session.get('selected_model', client.default_model)
        except Exception as e:
            logger.warning(f"Could not fetch OpenRouter models: {e}")
    
    context = {
        'recent_documents': recent_docs,
        'stats': stats,
        'upload_form': DocumentUploadForm(),
        'query_form': QueryForm(user=request.user) if request.user.is_authenticated else QueryForm(),
        'available_models': available_models,
        'selected_model': selected_model,
    }
    
    return render(request, 'rag_app/home.html', context)


@login_required
def upload_document(request):
    """
    Handle document upload and processing (supports multiple files)
    """
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                # Get uploaded files (support multiple files)
                files = request.FILES.getlist('file')
                if not files:
                    messages.error(request, "No files selected for upload.")
                    return redirect('home')
                
                processor = get_document_processor()
                uploaded_documents = []
                
                for uploaded_file in files:
                    try:
                        # Use filename as title if no custom title provided or multiple files
                        title = form.cleaned_data.get('title')
                        if not title or len(files) > 1:
                            # For multiple files, always use filename as title
                            title = uploaded_file.name.rsplit('.', 1)[0]
                        
                        # Create document record
                        document = processor.process_document(uploaded_file, request.user, title)
                        
                        # Set additional fields
                        if form.cleaned_data.get('tags'):
                            document.tags = form.cleaned_data['tags']
                        if form.cleaned_data.get('category'):
                            document.category = form.cleaned_data['category']
                        document.save()
                        
                        uploaded_documents.append(document)
                        
                    except Exception as e:
                        messages.error(request, f"Error uploading '{uploaded_file.name}': {str(e)}")
                        continue
                
                if uploaded_documents:
                    # Start background processing for all documents
                    def process_all_in_background():
                        for document in uploaded_documents:
                            try:
                                processor.create_chunks_and_embeddings(document)
                                logger.info(f"Background processing completed for document: {document.title}")
                            except Exception as e:
                                logger.error(f"Background processing failed for document {document.title}: {e}")
                    
                    # Start processing in background thread
                    threading.Thread(target=process_all_in_background, daemon=True).start()
                    
                    if len(uploaded_documents) == 1:
                        messages.success(
                            request, 
                            f"Document '{uploaded_documents[0].title}' uploaded successfully. "
                            f"Processing chunks and embeddings in background..."
                        )
                        return redirect('document_detail', document_id=uploaded_documents[0].id)
                    else:
                        messages.success(
                            request, 
                            f"{len(uploaded_documents)} documents uploaded successfully. "
                            f"Processing chunks and embeddings in background..."
                        )
                        return redirect('document_list')
                else:
                    messages.error(request, "No documents were successfully uploaded.")
                
            except Exception as e:
                messages.error(request, f"Error during upload: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    
    return redirect('home')


@login_required
def document_list(request):
    """
    List documents with search and filtering
    """
    form = DocumentSearchForm(request.GET)
    documents = Document.objects.filter(uploaded_by=request.user)
    
    if form.is_valid():
        search = form.cleaned_data.get('search')
        file_type = form.cleaned_data.get('file_type')
        status = form.cleaned_data.get('status')
        category = form.cleaned_data.get('category')
        
        if search:
            documents = documents.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tags__icontains=search) |
                Q(file_name__icontains=search)
            )
        
        if file_type:
            documents = documents.filter(file_type=file_type)
        
        if status:
            documents = documents.filter(status=status)
        
        if category:
            documents = documents.filter(category__icontains=category)
    
    # Add chunk counts
    documents = documents.annotate(chunk_count_actual=Count('chunks'))
    documents = documents.order_by('-uploaded_at')
    
    # Pagination
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Check if there are any processing documents for auto-refresh
    has_processing_documents = documents.filter(status='processing').exists()
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'documents': page_obj.object_list,
        'has_processing_documents': has_processing_documents,
    }
    
    return render(request, 'rag_app/document_list.html', context)


@login_required
def document_detail(request, document_id):
    """
    Display document details with chunks
    """
    document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)
    chunks = document.chunks.all().order_by('chunk_index')
    
    # Pagination for chunks
    paginator = Paginator(chunks, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'document': document,
        'chunks': page_obj.object_list,
        'page_obj': page_obj,
    }
    
    return render(request, 'rag_app/document_detail.html', context)


@login_required
def delete_document(request, document_id):
    """
    Delete a document and its associated files
    """
    document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        try:
            # Delete file from disk
            import os
            from django.conf import settings
            file_path = os.path.join(settings.MEDIA_ROOT, document.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Delete database record (cascades to chunks and embeddings)
            title = document.title
            document.delete()
            
            # Handle AJAX requests vs regular form submissions
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'message': f"Document '{title}' deleted successfully.",
                    'redirect': reverse('document_list')
                })
            else:
                messages.success(request, f"Document '{title}' deleted successfully.")
                return redirect('document_list')
            
        except Exception as e:
            error_msg = f"Error deleting document: {str(e)}"
            
            # Handle AJAX requests vs regular form submissions
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                })
            else:
                messages.error(request, error_msg)
                return redirect('document_list')
    
    return redirect('document_list')


@login_required
def reprocess_document(request, document_id):
    """
    Reprocess document chunks and embeddings
    """
    document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)
    
    if request.method == 'POST':
        try:
            # Delete existing chunks and embeddings
            document.chunks.all().delete()
            
            # Reset document status
            document.status = 'processing'
            document.chunk_count = 0
            document.processing_error = ''
            document.save()
            
            # Start background reprocessing
            def reprocess_in_background():
                try:
                    processor = get_document_processor()
                    processor.create_chunks_and_embeddings(document)
                    print(f"Background reprocessing completed for document: {document.title}")
                except Exception as e:
                    print(f"Background reprocessing failed for document {document.title}: {e}")
            
            threading.Thread(target=reprocess_in_background, daemon=True).start()
            
            messages.success(
                request,
                f"Reprocessing started for document '{document.title}'. "
                f"New chunks and embeddings will be generated in background."
            )
            
        except Exception as e:
            messages.error(request, f"Error reprocessing document: {str(e)}")
    
    return redirect('document_detail', document_id=document_id)


@login_required
@require_http_methods(["GET"])
def document_status_api(request, document_id):
    """
    API endpoint to check document processing status
    """
    try:
        document = get_object_or_404(Document, id=document_id, uploaded_by=request.user)
        
        data = {
            'status': document.status,
            'chunk_count': document.chunk_count,
            'processing_error': document.processing_error,
            'processed_at': document.processed_at.isoformat() if document.processed_at else None,
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def query_documents(request):
    """
    Query documents using RAG engine
    """
    if request.method == 'POST':
        form = QueryForm(request.POST)
        
        if form.is_valid():
            query_text = form.cleaned_data['query']
            similarity_threshold = form.cleaned_data['similarity_threshold']
            max_results = form.cleaned_data['max_results']
            selected_documents = form.cleaned_data.get('documents', [])
            
            # Get selected model from form, session, or use default
            selected_model = request.POST.get('model')
            if not selected_model:
                # Try to get from session first
                selected_model = request.session.get('selected_model')
                if not selected_model:
                    # Fall back to client default
                    try:
                        client = get_openrouter_client()
                        selected_model = client.default_model
                    except Exception as e:
                        logger.warning(f"Could not get default model: {e}")
                        selected_model = 'google/gemini-2.5-flash'  # Hard fallback to free model
            
            # Store the selected model in session for future use
            if selected_model:
                request.session['selected_model'] = selected_model
            
            try:
                # Check if this is a conversational query first
                conversation_handler = get_conversation_handler()
                user_has_docs = Document.objects.filter(uploaded_by=request.user).exists() if request.user.is_authenticated else False
                
                conversational_response = conversation_handler.get_context_aware_response(
                    query_text, 
                    request.user if request.user.is_authenticated else None,
                    user_has_docs
                )
                
                if conversational_response:
                    # Handle conversational query without RAG processing
                    logger.info(f"Handling conversational query: {query_text}")
                    
                    # Create a simple response object for template compatibility
                    class ConversationalResponse:
                        def __init__(self, response_text, query):
                            self.response_text = response_text
                            self.query_text = query
                            self.sources = []
                            self.total_chunks_found = 0
                            self.search_time = 0.0
                            self.llm_time = 0.0
                            self.total_time = 0.0
                            self.is_conversational = True
                    
                    response = ConversationalResponse(conversational_response, query_text)
                    
                    messages.success(
                        request,
                        "💬 Conversational response generated instantly"
                    )
                    
                    context = {
                        'query': query_text,
                        'response': response,
                        'form': QueryForm(),
                        'selected_model': selected_model,
                        'selected_documents': selected_documents,
                        'is_conversational': True
                    }
                    
                    return render(request, 'rag_app/query_results.html', context)
                
                # Continue with RAG processing for document queries
                # Initialize RAG engine
                logger.info(f"Processing RAG query: {query_text}")
                logger.info(f"Selected documents: {[doc.id for doc in selected_documents] if selected_documents else 'All documents'}")
                logger.info(f"Selected model: {selected_model}")
                
                engine = RAGQueryEngine()
                
                # Override configuration if provided
                if similarity_threshold:
                    engine.config.similarity_threshold = similarity_threshold
                if max_results:
                    engine.config.max_chunks = max_results
                if selected_model:
                    engine.config.llm_model = selected_model
                
                # Process document selection
                document_ids = None
                if selected_documents:
                    document_ids = [str(doc.id) for doc in selected_documents]
                
                # Process the query
                response = engine.query(
                    query_text=query_text,
                    user=request.user if request.user.is_authenticated else None,
                    document_ids=document_ids,
                    session_id=request.session.session_key
                )
                
                # Add success message with more details
                doc_info = f" in {len(selected_documents)} selected documents" if selected_documents else " across all documents"
                messages.success(
                    request,
                    f"Found {response.total_chunks_found} relevant chunks{doc_info} in {response.total_time:.2f}s using {selected_model or 'default model'}"
                )
                
                context = {
                    'query': query_text,
                    'response': response,
                    'form': QueryForm(),
                    'selected_model': selected_model,
                    'selected_documents': selected_documents,
                    'is_conversational': False
                }
                
                return render(request, 'rag_app/query_results.html', context)
                
            except Exception as e:
                logger.error(f"RAG query failed: {str(e)}")
                messages.error(
                    request,
                    f"Query processing failed: {str(e)}"
                )
                
                # Fallback to simple text search
                if request.user.is_authenticated:
                    query_filter = {
                        'uploaded_by': request.user,
                        'content__icontains': query_text,
                        'status': 'processed'
                    }
                    
                    # Apply document selection to fallback search too
                    if selected_documents:
                        query_filter['id__in'] = [doc.id for doc in selected_documents]
                    
                    matching_docs = Document.objects.filter(**query_filter)[:max_results or 5]
                    
                    context = {
                        'query': query_text,
                        'matching_documents': matching_docs,
                        'form': QueryForm(),
                        'fallback_search': True,
                        'selected_documents': selected_documents,
                    }
                    
                    return render(request, 'rag_app/query_results.html', context)
    
    return redirect('home')


@csrf_exempt
def api_query(request):
    """
    API endpoint for RAG queries
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    try:
        data = json.loads(request.body)
        query_text = data.get('query', '').strip()
        
        if not query_text:
            return JsonResponse({'error': 'Query text is required'}, status=400)
        
        # Get optional parameters
        similarity_threshold = data.get('similarity_threshold')
        max_results = data.get('max_results')
        
        # Initialize RAG engine
        engine = RAGQueryEngine()
        
        # Override configuration if provided
        if similarity_threshold is not None:
            engine.config.similarity_threshold = float(similarity_threshold)
        if max_results is not None:
            engine.config.max_chunks = int(max_results)
        
        # Process the query
        response = engine.query(
            query_text=query_text,
            user=request.user if request.user.is_authenticated else None,
            session_id=request.session.session_key
        )
        
        # Return JSON response
        return JsonResponse(response.to_dict())
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.error(f"API query failed: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)


# Error handlers
def handler404(request, exception):
    """Custom 404 handler"""
    return render(request, 'rag_app/404.html', status=404)


def handler500(request):
    """Custom 500 handler"""
    return render(request, 'rag_app/500.html', status=500)
