"""
URL configuration for RAG app
"""
from django.urls import path
from . import views
from . import analytics_views
from . import model_views
from . import chat_views

urlpatterns = [
    # Main pages
    path('', views.home_view, name='home'),
    path('documents/', views.document_list, name='document_list'),
    path('documents/<uuid:document_id>/', views.document_detail, name='document_detail'),
    
    # Document actions
    path('upload/', views.upload_document, name='upload_document'),
    path('documents/<uuid:document_id>/delete/', views.delete_document, name='delete_document'),
    path('documents/<uuid:document_id>/reprocess/', views.reprocess_document, name='reprocess_document'),
    
    # Query functionality
    path('query/', views.query_documents, name='query_documents'),
    
    # Chat interface
    path('chat/', chat_views.chat_interface, name='chat_interface'),
    path('chat/query/', chat_views.chat_query, name='chat_query'),
    
    # Model selection and management
    path('models/', model_views.model_selection, name='model_selection'),
    path('models/api/', model_views.models_api, name='models_api'),
    path('models/test/', model_views.test_model, name='test_model'),
    path('models/select/', model_views.select_model, name='select_model'),
    
    # Analytics and conversation history
    path('analytics/', analytics_views.analytics_dashboard, name='analytics_dashboard'),
    path('analytics/api/', analytics_views.analytics_api, name='analytics_api'),
    path('conversations/', analytics_views.conversation_history, name='conversation_history'),
    path('conversations/<uuid:session_id>/', analytics_views.session_detail, name='session_detail'),
    
    # API endpoints
    path('api/query/', views.api_query, name='api_query'),
    path('api/documents/<uuid:document_id>/status/', views.document_status_api, name='document_status_api'),
]
