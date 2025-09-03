"""
Document processing utilities for RAG system
Handles file upload, text extraction, and content processing
"""
import os
import hashlib
import mimetypes
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time

# Document processing imports
import PyPDF2
import fitz  # PyMuPDF
import pandas as pd
from io import StringIO

from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
from django.utils import timezone

from .models import Document, DocumentChunk, Embedding
from .embedding_utils import get_embedding_generator, chunk_text, calculate_content_hash, estimate_tokens


class DocumentProcessor:
    """
    Handles document upload, text extraction, and processing
    """
    
    # Supported file types and their MIME types
    SUPPORTED_TYPES = {
        'pdf': ['application/pdf'],
        'txt': ['text/plain', 'text/csv'],
        'csv': ['text/csv', 'application/csv'],
        'json': ['application/json'],
        'md': ['text/markdown', 'text/x-markdown'],
    }
    
    # Maximum file size (from environment or default 5MB)
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE_MB', 5)) * 1024 * 1024
    
    def __init__(self):
        self.upload_dir = Path(settings.MEDIA_ROOT) / 'uploads'
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, uploaded_file: UploadedFile) -> Dict[str, any]:
        """
        Validate uploaded file for size, type, and format
        
        Returns:
            dict: Validation result with 'valid' boolean and 'errors' list
        """
        result = {'valid': True, 'errors': []}
        
        # Check file size
        if uploaded_file.size > self.MAX_FILE_SIZE:
            result['valid'] = False
            result['errors'].append(
                f"File size ({uploaded_file.size / 1024 / 1024:.1f}MB) exceeds maximum "
                f"allowed size ({self.MAX_FILE_SIZE / 1024 / 1024}MB)"
            )
        
        # Check file type
        content_type = uploaded_file.content_type
        file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
        
        supported = False
        for ext, mime_types in self.SUPPORTED_TYPES.items():
            if file_extension == ext or content_type in mime_types:
                supported = True
                break
        
        if not supported:
            result['valid'] = False
            result['errors'].append(
                f"File type '{file_extension}' with MIME type '{content_type}' is not supported. "
                f"Supported types: {list(self.SUPPORTED_TYPES.keys())}"
            )
        
        # Check if file has content
        if uploaded_file.size == 0:
            result['valid'] = False
            result['errors'].append("File is empty")
        
        return result
    
    def save_uploaded_file(self, uploaded_file: UploadedFile, user) -> str:
        """
        Save uploaded file to disk and return file path
        
        Returns:
            str: Relative path to saved file
        """
        # Create user-specific subdirectory
        user_dir = self.upload_dir / f"user_{user.id}"
        user_dir.mkdir(exist_ok=True)
        
        # Generate unique filename to avoid conflicts
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{uploaded_file.name}"
        file_path = user_dir / filename
        
        # Save file
        with open(file_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)
        
        # Return relative path from MEDIA_ROOT
        return str(file_path.relative_to(settings.MEDIA_ROOT))
    
    def extract_text_from_pdf(self, file_path: Path) -> Tuple[str, Dict]:
        """
        Extract text from PDF using both PyPDF2 and PyMuPDF for best results
        """
        text = ""
        metadata = {'pages': 0, 'extraction_method': 'none', 'errors': []}
        
        try:
            # Try PyMuPDF first (better text extraction)
            doc = fitz.open(file_path)
            pages_text = []
            
            for page_num in range(doc.page_count):
                page = doc[page_num]
                page_text = page.get_text()
                if page_text.strip():
                    pages_text.append(page_text)
            
            if pages_text:
                text = "\n\n".join(pages_text)
                metadata['extraction_method'] = 'pymupdf'
                metadata['pages'] = len(pages_text)
            
            doc.close()
            
        except Exception as e:
            metadata['errors'].append(f"PyMuPDF error: {str(e)}")
            
            # Fallback to PyPDF2
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    pages_text = []
                    
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text.strip():
                            pages_text.append(page_text)
                    
                    if pages_text:
                        text = "\n\n".join(pages_text)
                        metadata['extraction_method'] = 'pypdf2'
                        metadata['pages'] = len(pages_text)
                        
            except Exception as e2:
                metadata['errors'].append(f"PyPDF2 error: {str(e2)}")
        
        if not text.strip():
            raise ValueError("Could not extract text from PDF file")
        
        return text, metadata
    
    def extract_text_from_csv(self, file_path: Path) -> Tuple[str, Dict]:
        """
        Extract text from CSV file
        """
        try:
            # Try to read CSV with pandas
            df = pd.read_csv(file_path)
            
            # Convert DataFrame to a readable text format
            text_parts = []
            
            # Add column headers
            text_parts.append("Columns: " + ", ".join(df.columns))
            text_parts.append("")  # Empty line
            
            # Add data rows (limit to prevent huge files)
            max_rows = 1000
            for idx, row in df.head(max_rows).iterrows():
                row_text = []
                for col in df.columns:
                    value = str(row[col]) if pd.notna(row[col]) else ""
                    if value:
                        row_text.append(f"{col}: {value}")
                
                if row_text:
                    text_parts.append("; ".join(row_text))
            
            if len(df) > max_rows:
                text_parts.append(f"\n[Note: Only first {max_rows} rows shown, total rows: {len(df)}]")
            
            text = "\n".join(text_parts)
            metadata = {
                'rows': len(df),
                'columns': len(df.columns),
                'extraction_method': 'pandas'
            }
            
            return text, metadata
            
        except Exception as e:
            raise ValueError(f"Could not extract text from CSV file: {str(e)}")
    
    def extract_text_from_file(self, file_path: str, file_type: str) -> Tuple[str, Dict]:
        """
        Extract text from file based on file type
        
        Returns:
            tuple: (extracted_text, metadata_dict)
        """
        full_path = Path(settings.MEDIA_ROOT) / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        if file_type == 'pdf':
            return self.extract_text_from_pdf(full_path)
        
        elif file_type in ['txt', 'md', 'json']:
            # Read as plain text
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                metadata = {
                    'extraction_method': 'plain_text',
                    'encoding': 'utf-8'
                }
                return text, metadata
                
            except UnicodeDecodeError:
                # Try different encodings
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        with open(full_path, 'r', encoding=encoding) as f:
                            text = f.read()
                        
                        metadata = {
                            'extraction_method': 'plain_text',
                            'encoding': encoding
                        }
                        return text, metadata
                    except UnicodeDecodeError:
                        continue
                
                raise ValueError("Could not decode file with any supported encoding")
        
        elif file_type == 'csv':
            return self.extract_text_from_csv(full_path)
        
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
    
    def process_document(self, uploaded_file: UploadedFile, user, title: str = None) -> Document:
        """
        Complete document processing pipeline
        
        Args:
            uploaded_file: Django UploadedFile object
            user: User who uploaded the file
            title: Optional custom title (uses filename if not provided)
        
        Returns:
            Document: Created document instance
        """
        # Validate file
        validation = self.validate_file(uploaded_file)
        if not validation['valid']:
            raise ValueError(f"File validation failed: {'; '.join(validation['errors'])}")
        
        # Save file
        file_path = self.save_uploaded_file(uploaded_file, user)
        
        # Determine file type
        file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
        file_type = file_extension
        
        # Use provided title or filename
        document_title = title or Path(uploaded_file.name).stem
        
        try:
            # Extract text
            print(f"Extracting text from {uploaded_file.name}...")
            start_time = time.time()
            content, extraction_metadata = self.extract_text_from_file(file_path, file_type)
            extraction_time = time.time() - start_time
            
            if not content.strip():
                raise ValueError("No text content could be extracted from file")
            
            # Calculate content hash for deduplication
            content_hash = calculate_content_hash(content)
            
            # Check for duplicate content
            existing_doc = Document.objects.filter(content_hash=content_hash).first()
            if existing_doc:
                # Delete the newly uploaded file since it's a duplicate
                full_path = Path(settings.MEDIA_ROOT) / file_path
                if full_path.exists():
                    full_path.unlink()
                
                raise ValueError(
                    f"Document with identical content already exists: '{existing_doc.title}' "
                    f"uploaded by {existing_doc.uploaded_by.username} on {existing_doc.uploaded_at.date()}"
                )
            
            # Create document record
            document = Document.objects.create(
                title=document_title,
                file_name=uploaded_file.name,
                file_path=file_path,
                file_size=uploaded_file.size,
                file_type=file_type,
                mime_type=uploaded_file.content_type,
                content=content,
                content_hash=content_hash,
                uploaded_by=user,
                status='processing'
            )
            
            print(f"Text extracted in {extraction_time:.2f} seconds")
            print(f"Content length: {len(content)} characters")
            print(f"Extraction metadata: {extraction_metadata}")
            
            return document
            
        except Exception as e:
            # Clean up uploaded file on error
            full_path = Path(settings.MEDIA_ROOT) / file_path
            if full_path.exists():
                full_path.unlink()
            raise e
    
    def create_chunks_and_embeddings(self, document: Document) -> None:
        """
        Create text chunks and generate embeddings for a document
        """
        if document.status != 'processing':
            raise ValueError(f"Document status must be 'processing', got '{document.status}'")
        
        try:
            # Get chunking parameters from environment or use defaults
            chunk_size = int(os.getenv('CHUNK_SIZE', 500))
            overlap = int(os.getenv('CHUNK_OVERLAP', 50))
            
            print(f"Creating chunks for document '{document.title}'...")
            start_time = time.time()
            
            # Create chunks
            chunks_data = chunk_text(document.content, chunk_size=chunk_size, overlap=overlap)
            
            if not chunks_data:
                raise ValueError("No chunks could be created from document content")
            
            # Get embedding generator
            embedding_gen = get_embedding_generator()
            
            # Prepare texts for batch embedding
            chunk_texts = [chunk['content'] for chunk in chunks_data]
            
            print(f"Generating embeddings for {len(chunk_texts)} chunks...")
            embeddings, total_embedding_time = embedding_gen.generate_embeddings_batch(chunk_texts)
            
            # Create DocumentChunk and Embedding objects
            created_chunks = []
            for i, chunk_data in enumerate(chunks_data):
                # Create chunk
                doc_chunk = DocumentChunk.objects.create(
                    document=document,
                    content=chunk_data['content'],
                    chunk_index=chunk_data['chunk_index'],
                    start_char=chunk_data['start_char'],
                    end_char=chunk_data['end_char'],
                    word_count=chunk_data['word_count'],
                    char_count=chunk_data['char_count'],
                    token_count=estimate_tokens(chunk_data['content'])
                )
                
                # Create embedding
                Embedding.objects.create(
                    chunk=doc_chunk,
                    vector=embeddings[i].tolist(),  # Convert numpy array to list
                    model_name=embedding_gen.model_name,
                    processing_time=total_embedding_time / len(chunk_texts)  # Average time per chunk
                )
                
                created_chunks.append(doc_chunk)
            
            # Update document
            processing_time = time.time() - start_time
            document.chunk_count = len(created_chunks)
            document.status = 'processed'
            document.processed_at = timezone.now()
            document.save()
            
            print(f"Document processing completed in {processing_time:.2f} seconds")
            print(f"Created {len(created_chunks)} chunks with embeddings")
            
        except Exception as e:
            # Update document status to failed
            document.status = 'failed'
            document.processing_error = str(e)
            document.save()
            
            print(f"Document processing failed: {str(e)}")
            raise e


# Global document processor instance
_document_processor = None

def get_document_processor() -> DocumentProcessor:
    """
    Get or create global document processor instance
    """
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor()
    return _document_processor
