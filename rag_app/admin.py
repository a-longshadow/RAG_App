from django.contrib import admin
from .models import (Document, DocumentChunk, Embedding, QueryLog, SystemSettings,
                     QuerySession, ConversationHistory, SystemAnalytics, QuerySuggestion)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'file_name', 'file_type', 'status', 'chunk_count', 'uploaded_by', 'uploaded_at']
    list_filter = ['status', 'file_type', 'uploaded_at']
    search_fields = ['title', 'file_name', 'content']
    readonly_fields = ['id', 'content_hash', 'chunk_count', 'uploaded_at', 'processed_at']
    ordering = ['-uploaded_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'file_name', 'file_type', 'mime_type')
        }),
        ('Content', {
            'fields': ('content', 'content_hash'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('status', 'processing_error', 'chunk_count')
        }),
        ('Metadata', {
            'fields': ('file_size', 'uploaded_by', 'uploaded_at', 'processed_at', 'tags', 'category')
        }),
    )


@admin.register(DocumentChunk)
class DocumentChunkAdmin(admin.ModelAdmin):
    list_display = ['document', 'chunk_index', 'word_count', 'char_count', 'created_at']
    list_filter = ['document__status', 'created_at']
    search_fields = ['content', 'document__title']
    readonly_fields = ['id', 'token_count', 'word_count', 'char_count', 'created_at']
    ordering = ['document', 'chunk_index']
    
    fieldsets = (
        ('Chunk Information', {
            'fields': ('document', 'chunk_index', 'content')
        }),
        ('Position', {
            'fields': ('start_char', 'end_char')
        }),
        ('Statistics', {
            'fields': ('token_count', 'word_count', 'char_count', 'created_at')
        }),
    )


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ['chunk', 'model_name', 'dimensions', 'processing_time', 'created_at']
    list_filter = ['model_name', 'created_at']
    readonly_fields = ['id', 'vector', 'processing_time', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Embedding Information', {
            'fields': ('chunk', 'model_name', 'model_version', 'dimensions')
        }),
        ('Processing', {
            'fields': ('processing_time', 'created_at')
        }),
        ('Vector Data', {
            'fields': ('vector',),
            'classes': ('collapse',)
        }),
    )


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ['query_text_short', 'user', 'llm_model', 'chunks_found', 'total_time', 'user_rating', 'created_at']
    list_filter = ['llm_model', 'llm_provider', 'user_rating', 'created_at']
    search_fields = ['query_text', 'response_text']
    readonly_fields = ['id', 'search_time', 'llm_time', 'total_time', 'created_at']
    ordering = ['-created_at']
    
    def query_text_short(self, obj):
        return obj.query_text[:50] + "..." if len(obj.query_text) > 50 else obj.query_text
    query_text_short.short_description = 'Query'
    
    fieldsets = (
        ('Query Information', {
            'fields': ('query_text', 'user', 'session_id')
        }),
        ('Response', {
            'fields': ('response_text', 'source_chunks', 'similarity_threshold', 'chunks_found')
        }),
        ('LLM Details', {
            'fields': ('llm_model', 'llm_provider', 'prompt_tokens', 'completion_tokens', 'total_cost')
        }),
        ('Performance', {
            'fields': ('search_time', 'llm_time', 'total_time')
        }),
        ('Feedback', {
            'fields': ('user_rating', 'feedback_text', 'created_at')
        }),
    )


@admin.register(SystemSettings)
class SystemSettingsAdmin(admin.ModelAdmin):
    list_display = ['key', 'value_short', 'value_type', 'updated_at', 'updated_by']
    list_filter = ['value_type', 'updated_at']
    search_fields = ['key', 'description']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['key']
    
    def value_short(self, obj):
        return obj.value[:50] + "..." if len(obj.value) > 50 else obj.value
    value_short.short_description = 'Value'
    
    fieldsets = (
        ('Setting Information', {
            'fields': ('key', 'value', 'value_type', 'description')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'updated_by')
        }),
    )


@admin.register(QuerySession)
class QuerySessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_name_display', 'query_count', 'is_active', 'started_at', 'last_activity']
    list_filter = ['is_active', 'started_at', 'last_activity']
    search_fields = ['user__username', 'session_name']
    readonly_fields = ['id', 'started_at', 'query_count', 'total_tokens_used', 'total_response_time_ms']
    ordering = ['-last_activity']
    
    def session_name_display(self, obj):
        return obj.session_name or f"Session {obj.id.hex[:8]}"
    session_name_display.short_description = 'Session Name'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'session_name', 'is_active')
        }),
        ('Statistics', {
            'fields': ('query_count', 'total_tokens_used', 'total_response_time_ms')
        }),
        ('Timestamps', {
            'fields': ('started_at', 'last_activity')
        }),
    )


@admin.register(ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    list_display = ['session_user', 'query_preview', 'response_source', 'chunks_retrieved', 
                   'total_response_time_ms', 'is_bookmarked', 'user_rating', 'created_at']
    list_filter = ['response_source', 'is_bookmarked', 'user_rating', 'created_at']
    search_fields = ['query_text', 'response_text', 'session__user__username']
    readonly_fields = ['id', 'query_hash', 'search_time_ms', 'generation_time_ms', 
                      'total_response_time_ms', 'created_at']
    ordering = ['-created_at']
    filter_horizontal = ['documents_used']
    
    def session_user(self, obj):
        return obj.session.user.username
    session_user.short_description = 'User'
    
    def query_preview(self, obj):
        return obj.query_text[:50] + "..." if len(obj.query_text) > 50 else obj.query_text
    query_preview.short_description = 'Query'
    
    fieldsets = (
        ('Query Information', {
            'fields': ('session', 'query_text', 'query_hash')
        }),
        ('Response', {
            'fields': ('response_text', 'response_source')
        }),
        ('RAG Details', {
            'fields': ('documents_used', 'chunks_retrieved', 'similarity_threshold', 'max_similarity_score')
        }),
        ('Performance', {
            'fields': ('search_time_ms', 'generation_time_ms', 'total_response_time_ms', 'tokens_used')
        }),
        ('User Interaction', {
            'fields': ('is_bookmarked', 'user_rating', 'user_feedback')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        }),
    )


@admin.register(SystemAnalytics)
class SystemAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['metric_name', 'metric_value_display', 'category', 'subcategory', 
                   'user', 'recorded_at']
    list_filter = ['category', 'subcategory', 'metric_name', 'recorded_at']
    search_fields = ['metric_name', 'category', 'user__username']
    readonly_fields = ['id', 'recorded_at']
    ordering = ['-recorded_at']
    
    def metric_value_display(self, obj):
        return f"{obj.metric_value} {obj.metric_unit}"
    metric_value_display.short_description = 'Value'
    
    fieldsets = (
        ('Metric Information', {
            'fields': ('metric_name', 'metric_value', 'metric_unit')
        }),
        ('Categorization', {
            'fields': ('category', 'subcategory')
        }),
        ('Context', {
            'fields': ('user', 'document', 'session')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
        ('Timestamp', {
            'fields': ('recorded_at',)
        }),
    )


@admin.register(QuerySuggestion)
class QuerySuggestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'suggestion_type', 'original_preview', 'suggested_preview', 
                   'was_accepted', 'confidence_score', 'created_at']
    list_filter = ['suggestion_type', 'was_accepted', 'created_at']
    search_fields = ['original_query', 'suggested_query', 'user__username']
    readonly_fields = ['id', 'created_at', 'accepted_at']
    ordering = ['-created_at']
    
    def original_preview(self, obj):
        return obj.original_query[:30] + "..." if len(obj.original_query) > 30 else obj.original_query
    original_preview.short_description = 'Original Query'
    
    def suggested_preview(self, obj):
        return obj.suggested_query[:30] + "..." if len(obj.suggested_query) > 30 else obj.suggested_query
    suggested_preview.short_description = 'Suggested Query'
    
    fieldsets = (
        ('Query Information', {
            'fields': ('user', 'original_query', 'suggested_query', 'suggestion_type')
        }),
        ('Reasoning', {
            'fields': ('improvement_reason', 'confidence_score')
        }),
        ('Usage Tracking', {
            'fields': ('was_accepted', 'accepted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
