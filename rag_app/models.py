from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from pgvector.django import VectorField
import uuid


class Document(models.Model):
    """
    Stores uploaded documents and their metadata
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    file_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    file_size = models.IntegerField()  # Size in bytes
    file_type = models.CharField(max_length=50)  # pdf, txt, docx, etc.
    mime_type = models.CharField(max_length=100)
    
    # Content and processing
    content = models.TextField()  # Extracted text content
    content_hash = models.CharField(max_length=64, unique=True)  # SHA256 hash for deduplication
    chunk_count = models.IntegerField(default=0)  # Number of chunks created
    
    # Processing status
    STATUS_CHOICES = [
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    processing_error = models.TextField(blank=True, null=True)
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Tags and categorization
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    category = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['file_type']),
            models.Index(fields=['uploaded_by']),
            models.Index(fields=['content_hash']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.file_name})"


class DocumentChunk(models.Model):
    """
    Stores document chunks for embedding and retrieval
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    
    # Chunk content and metadata
    content = models.TextField()
    chunk_index = models.IntegerField()  # Position in document (0-based)
    start_char = models.IntegerField()   # Character position in original document
    end_char = models.IntegerField()     # End character position
    
    # Chunk characteristics
    token_count = models.IntegerField(default=0)
    word_count = models.IntegerField(default=0)
    char_count = models.IntegerField(default=0)
    
    # Processing timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['document', 'chunk_index']
        unique_together = ['document', 'chunk_index']
        indexes = [
            models.Index(fields=['document', 'chunk_index']),
        ]
    
    def __str__(self):
        return f"{self.document.title} - Chunk {self.chunk_index}"


class Embedding(models.Model):
    """
    Stores vector embeddings for document chunks using pgvector
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chunk = models.OneToOneField(DocumentChunk, on_delete=models.CASCADE, related_name='embedding')
    
    # Vector embedding (768 dimensions for all-mpnet-base-v2)
    vector = VectorField(dimensions=768, null=True, blank=True)
    
    # Embedding metadata
    model_name = models.CharField(max_length=100, default='all-mpnet-base-v2')
    model_version = models.CharField(max_length=50, default='1.0')
    dimensions = models.IntegerField(default=768)
    
    # Processing info
    created_at = models.DateTimeField(default=timezone.now)
    processing_time = models.FloatField(default=0.0)  # Time in seconds to generate embedding
    
    class Meta:
        indexes = [
            models.Index(fields=['model_name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Embedding for {self.chunk}"


class QueryLog(models.Model):
    """
    Logs user queries and system responses for analytics and improvement
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Query details
    query_text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    
    # Response details
    response_text = models.TextField(blank=True)
    source_chunks = models.ManyToManyField(DocumentChunk, blank=True)
    similarity_threshold = models.FloatField(default=0.8)
    chunks_found = models.IntegerField(default=0)
    
    # LLM details
    llm_model = models.CharField(max_length=100, blank=True)  # e.g., "claude-3-sonnet"
    llm_provider = models.CharField(max_length=50, default='openrouter')
    prompt_tokens = models.IntegerField(default=0)
    completion_tokens = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=6, default=0.0)
    
    # Performance metrics
    search_time = models.FloatField(default=0.0)  # Vector search time
    llm_time = models.FloatField(default=0.0)     # LLM response time
    total_time = models.FloatField(default=0.0)   # Total query time
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    # User feedback
    user_rating = models.IntegerField(null=True, blank=True, choices=[
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ])
    feedback_text = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['created_at']),
            models.Index(fields=['llm_model']),
        ]
    
    def __str__(self):
        return f"Query: {self.query_text[:50]}..."


class SystemSettings(models.Model):
    """
    Stores system-wide configuration settings
    """
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True)
    
    # Data type hints for the frontend
    TYPE_CHOICES = [
        ('string', 'String'),
        ('integer', 'Integer'),
        ('float', 'Float'),
        ('boolean', 'Boolean'),
        ('json', 'JSON'),
    ]
    value_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='string')
    
    # Metadata
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['key']
    
    def __str__(self):
        return f"{self.key}: {self.value[:50]}"


class QuerySession(models.Model):
    """
    Tracks user query sessions for conversation history
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_name = models.CharField(max_length=255, blank=True, help_text="User-defined session name")
    started_at = models.DateTimeField(default=timezone.now)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Session metadata
    query_count = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    total_response_time_ms = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        name = self.session_name or f"Session {self.id.hex[:8]}"
        return f"{self.user.username} - {name}"


class ConversationHistory(models.Model):
    """
    Stores individual queries and responses within sessions
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(QuerySession, on_delete=models.CASCADE, related_name='conversations')
    
    # Query details
    query_text = models.TextField()
    query_hash = models.CharField(max_length=64, help_text="SHA256 hash of query for deduplication")
    
    # Response details
    response_text = models.TextField()
    response_source = models.CharField(max_length=100, help_text="LLM model used")
    
    # RAG metadata
    documents_used = models.ManyToManyField(Document, blank=True, related_name='query_history')
    chunks_retrieved = models.IntegerField(default=0)
    similarity_threshold = models.FloatField()
    max_similarity_score = models.FloatField(null=True, blank=True)
    
    # Performance metrics
    search_time_ms = models.IntegerField(default=0)
    generation_time_ms = models.IntegerField(default=0)
    total_response_time_ms = models.IntegerField(default=0)
    tokens_used = models.IntegerField(default=0)
    
    # User interaction
    is_bookmarked = models.BooleanField(default=False)
    user_rating = models.IntegerField(null=True, blank=True, help_text="1-5 star rating")
    user_feedback = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', 'created_at']),
            models.Index(fields=['query_hash']),
            models.Index(fields=['is_bookmarked']),
            models.Index(fields=['user_rating']),
        ]
    
    def __str__(self):
        return f"{self.session.user.username}: {self.query_text[:50]}..."


class SystemAnalytics(models.Model):
    """
    Stores system-wide analytics and metrics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Metric details
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=50, blank=True, help_text="e.g., 'ms', 'count', 'percent'")
    
    # Categorization
    category = models.CharField(max_length=50, help_text="e.g., 'performance', 'usage', 'errors'")
    subcategory = models.CharField(max_length=50, blank=True)
    
    # Context
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, null=True, blank=True)
    session = models.ForeignKey(QuerySession, on_delete=models.CASCADE, null=True, blank=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamp
    recorded_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['metric_name', 'recorded_at']),
            models.Index(fields=['category', 'recorded_at']),
            models.Index(fields=['user', 'recorded_at']),
        ]
    
    def __str__(self):
        return f"{self.metric_name}: {self.metric_value} {self.metric_unit}"


class QuerySuggestion(models.Model):
    """
    Stores AI-generated query suggestions and improvements
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Original and suggested queries
    original_query = models.TextField()
    suggested_query = models.TextField()
    improvement_reason = models.TextField(help_text="Why this suggestion was made")
    
    # Suggestion metadata
    suggestion_type = models.CharField(max_length=50, choices=[
        ('expansion', 'Query Expansion'),
        ('refinement', 'Query Refinement'),
        ('correction', 'Spelling/Grammar Correction'),
        ('clarification', 'Clarification Request'),
    ])
    
    # Usage tracking
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    was_accepted = models.BooleanField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    
    # Performance
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence in suggestion (0-1)")
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'was_accepted']),
            models.Index(fields=['suggestion_type']),
        ]
    
    def __str__(self):
        return f"{self.suggestion_type}: {self.original_query[:30]}..."
