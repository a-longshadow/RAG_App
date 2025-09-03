"""
Django forms for RAG application
"""
from django import forms
from django.core.exceptions import ValidationError
from .models import Document


class DocumentUploadForm(forms.Form):
    """
    Form for uploading documents
    """
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100',
            'accept': '.pdf,.txt,.csv,.json,.md',
            'multiple': True,
            'id': 'file-upload'
        }),
        help_text='Supported formats: PDF, TXT, CSV, JSON, Markdown. Maximum size: 5MB per file. Multiple files allowed.'
    )
    
    title = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Leave empty to use filename'
        }),
        help_text='Optional custom title for the document'
    )
    
    tags = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'tag1, tag2, tag3'
        }),
        help_text='Optional comma-separated tags'
    )
    
    category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'e.g., Manual, Policy, Report'
        }),
        help_text='Optional category for organization'
    )
    
    def clean_file(self):
        """
        Validate uploaded file
        """
        file = self.cleaned_data.get('file')
        if not file:
            return file
        
        # Import here to avoid circular imports
        from .document_processor import get_document_processor
        
        processor = get_document_processor()
        validation = processor.validate_file(file)
        
        if not validation['valid']:
            raise ValidationError('; '.join(validation['errors']))
        
        return file


class QueryForm(forms.Form):
    """
    Form for RAG queries
    """
    query = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'rows': 3,
            'placeholder': 'Ask a question about your documents...'
        }),
        help_text='Enter your question or search query'
    )
    
    document_filter = forms.ModelMultipleChoiceField(
        queryset=Document.objects.none(),  # Will be set in __init__
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded'
        }),
        help_text='Select specific documents to search (leave empty to search all)'
    )
    
    similarity_threshold = forms.FloatField(
        initial=0.3,
        min_value=0.1,
        max_value=1.0,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'step': '0.1'
        }),
        help_text='Minimum similarity score (0.1-1.0, higher = more strict)'
    )
    
    max_results = forms.IntegerField(
        initial=5,
        min_value=1,
        max_value=20,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        }),
        help_text='Maximum number of relevant chunks to find (1-20)'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and user.is_authenticated:
            self.fields['document_filter'].queryset = Document.objects.filter(
                uploaded_by=user,
                status='processed'
            ).order_by('title')


class DocumentSearchForm(forms.Form):
    """
    Form for searching documents
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Search documents by title, content, or tags...'
        })
    )
    
    file_type = forms.ChoiceField(
        choices=[('', 'All Types')] + [(ext, ext.upper()) for ext in ['pdf', 'txt', 'csv', 'json', 'md']],
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + Document.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'
        })
    )
    
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Filter by category...'
        })
    )
