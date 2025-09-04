"""
RAG Query Engine - Core implementation for Retrieval-Augmented Generation

This module handles:
1. Query preprocessing and embedding generation
2. Semantic similarity search across document chunks
3. Context assembly and ranking
4. Prompt engineering for LLM queries
5. Response generation via OpenRouter API
6. Performance tracking and logging
"""

import os
import time
import json
import logging
import asyncio
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from decimal import Decimal

import numpy as np
import requests
from sentence_transformers import SentenceTransformer
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.contrib.auth.models import User
from pgvector.django import CosineDistance

from .models import DocumentChunk, QueryLog, Embedding, SystemSettings
from .openrouter_client import get_openrouter_client
from .conversation_handler import ConversationHandler

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """Configuration for RAG operations"""
    similarity_threshold: float = 0.7
    max_chunks: int = 5
    max_context_length: int = 4000
    embedding_model: str = 'all-mpnet-base-v2'
    llm_model: str = 'google/gemini-2.5-flash'
    temperature: float = 0.7
    max_tokens: int = 1000
    include_metadata: bool = True
    
    @classmethod
    def from_settings(cls) -> 'RAGConfig':
        """Load configuration from SystemSettings"""
        config = cls()
        
        settings_map = {
            'rag_similarity_threshold': 'similarity_threshold',
            'rag_max_chunks': 'max_chunks',
            'rag_max_context_length': 'max_context_length',
            'rag_embedding_model': 'embedding_model',
            'rag_llm_model': 'llm_model',
            'rag_temperature': 'temperature',
            'rag_max_tokens': 'max_tokens',
            'rag_include_metadata': 'include_metadata',
        }
        
        for setting_key, config_attr in settings_map.items():
            try:
                setting = SystemSettings.objects.get(key=setting_key)
                value = setting.value
                
                # Enhanced type conversion with error handling
                try:
                    if setting.value_type == 'float' or config_attr in ['similarity_threshold', 'temperature']:
                        value = float(value)
                    elif setting.value_type == 'integer' or config_attr in ['max_chunks', 'max_context_length', 'max_tokens']:
                        value = int(value)
                    elif setting.value_type == 'boolean' or config_attr == 'include_metadata':
                        value = value.lower() in ('true', '1', 'yes', 'on')
                    # Keep string values as-is for model names
                except (ValueError, TypeError) as e:
                    logger.warning(f"Type conversion failed for {setting_key}={value}: {e}. Using default.")
                    continue
                
                setattr(config, config_attr, value)
                logger.debug(f"Loaded setting {setting_key}={value} (type: {type(value).__name__})")
            except SystemSettings.DoesNotExist:
                logger.info(f"Setting {setting_key} not found, using default")
                continue
        
        return config


@dataclass
class SearchResult:
    """Represents a search result with similarity score"""
    chunk: DocumentChunk
    similarity_score: float
    rank: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'chunk_id': str(self.chunk.id),
            'content': self.chunk.content,
            'similarity_score': self.similarity_score,
            'rank': self.rank,
            'document_title': self.chunk.document.title,
            'document_id': str(self.chunk.document.id),
            'position_start': self.chunk.start_char,
            'position_end': self.chunk.end_char,
            'word_count': self.chunk.word_count,
        }


@dataclass
class RAGResponse:
    """Complete RAG response with metadata"""
    query: str
    response: str
    source_chunks: List[SearchResult]
    total_chunks_found: int
    search_time: float
    llm_time: float
    total_time: float
    llm_model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: Decimal = Decimal('0.0')
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'query': self.query,
            'response': self.response,
            'source_chunks': [chunk.to_dict() for chunk in self.source_chunks],
            'total_chunks_found': self.total_chunks_found,
            'search_time': self.search_time,
            'llm_time': self.llm_time,
            'total_time': self.total_time,
            'llm_model': self.llm_model,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_cost': float(self.total_cost),
        }


class RAGQueryEngine:
    """
    Main RAG Query Engine for processing user queries and generating responses
    """
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """Initialize the RAG engine with configuration"""
        self.config = config or RAGConfig.from_settings()
        self._embedding_model = None
        self._openrouter_client = get_openrouter_client()
        self._conversation_handler = ConversationHandler()
        
        if not self._openrouter_client.api_key:
            logger.warning("OPENROUTER_API_KEY not found in environment variables")
    
    @property
    def embedding_model(self) -> SentenceTransformer:
        """Lazy loading of embedding model"""
        if self._embedding_model is None:
            logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self._embedding_model = SentenceTransformer(self.config.embedding_model)
        return self._embedding_model
    
    def generate_query_embedding(self, query: str) -> np.ndarray:
        """Generate embedding vector for user query"""
        start_time = time.time()
        
        # Preprocess query
        query = query.strip()
        if not query:
            raise ValueError("Query cannot be empty")
        
        # Generate embedding
        embedding = self.embedding_model.encode([query])[0]
        
        processing_time = time.time() - start_time
        logger.debug(f"Query embedding generated in {processing_time:.3f}s")
        
        return embedding
    
    def search_similar_chunks(
        self, 
        query_embedding: np.ndarray, 
        user: Optional[User] = None,
        document_ids: Optional[List[str]] = None
    ) -> List[SearchResult]:
        """
        Perform semantic similarity search across document chunks
        
        Args:
            query_embedding: Query vector embedding
            user: User to filter documents (optional)
            document_ids: Specific document IDs to search (optional)
        
        Returns:
            List of SearchResult objects ordered by similarity
        """
        start_time = time.time()
        
        # Build query
        chunks_query = DocumentChunk.objects.select_related('document').filter(
            embedding__isnull=False  # Only chunks with embeddings
        )
        
        # Filter by user if provided
        if user:
            chunks_query = chunks_query.filter(document__uploaded_by=user)
        
        # Filter by specific documents if provided
        if document_ids:
            chunks_query = chunks_query.filter(document__id__in=document_ids)
        
        # Perform similarity search using pgvector
        # Ensure similarity_threshold is a float for calculation
        threshold = float(self.config.similarity_threshold) if isinstance(self.config.similarity_threshold, str) else self.config.similarity_threshold
        distance_threshold = 1.0 - threshold  # Convert similarity to distance
        
        similar_chunks = chunks_query.annotate(
            similarity=CosineDistance('embedding__vector', query_embedding)
        ).filter(
            similarity__lt=distance_threshold
        ).order_by('similarity')[:self.config.max_chunks * 2]  # Get extra for filtering
        
        # Convert to SearchResult objects with similarity scores
        results = []
        for rank, chunk in enumerate(similar_chunks, 1):
            similarity_score = 1.0 - chunk.similarity  # Convert distance back to similarity
            
            result = SearchResult(
                chunk=chunk,
                similarity_score=similarity_score,
                rank=rank
            )
            results.append(result)
            
            # Stop when we have enough chunks
            if len(results) >= self.config.max_chunks:
                break
        
        search_time = time.time() - start_time
        logger.info(f"Found {len(results)} relevant chunks in {search_time:.3f}s")
        
        return results
    
    def assemble_context(self, search_results: List[SearchResult]) -> str:
        """
        Assemble context from search results for LLM prompt
        
        Args:
            search_results: List of SearchResult objects
        
        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant context found."
        
        context_parts = []
        current_length = 0
        
        for result in search_results:
            # Format chunk with metadata if enabled
            if self.config.include_metadata:
                chunk_text = (
                    f"[Document: {result.chunk.document.title}] "
                    f"[Similarity: {result.similarity_score:.3f}]\n"
                    f"{result.chunk.content}\n"
                )
            else:
                chunk_text = f"{result.chunk.content}\n"
            
            # Check if adding this chunk would exceed context limit
            if current_length + len(chunk_text) > self.config.max_context_length:
                logger.info(f"Context limit reached, using {len(context_parts)} chunks")
                break
            
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
        
        return "\n---\n".join(context_parts)
    
    def create_prompt(self, query: str, context: str) -> str:
        """
        Create a well-structured prompt for the LLM
        
        Args:
            query: User's original query
            context: Assembled context from relevant chunks
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a helpful AI assistant that answers questions based on the provided context. Follow these guidelines:

1. Answer the question using ONLY the information provided in the context
2. If the context doesn't contain enough information to answer the question, say so clearly
3. Cite specific parts of the context when possible
4. Be concise but comprehensive
5. If multiple documents are referenced, mention which document provides each piece of information

Context:
{context}

Question: {query}

Answer:"""
        
        return prompt
    
    async def generate_llm_response(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """
        Generate response using OpenRouter API via the client
        
        Args:
            prompt: Formatted prompt for the LLM
        
        Returns:
            Tuple of (response_text, usage_metadata)
        """
        if not self._openrouter_client.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        start_time = time.time()
        
        try:
            # Use the OpenRouter client for chat completion
            messages = [{"role": "user", "content": prompt}]
            
            result = self._openrouter_client.chat_completion(
                messages=messages,
                model=self.config.llm_model,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Extract response and usage information
            response_text = result['choices'][0]['message']['content']
            usage = result.get('usage', {})
            
            # Calculate cost (example rates - adjust based on actual pricing)
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            
            # Cost calculation would need actual model pricing
            # This is a placeholder calculation
            cost_per_1k_prompt = Decimal('0.003')  # Example rate
            cost_per_1k_completion = Decimal('0.015')  # Example rate
            
            total_cost = (
                (Decimal(prompt_tokens) / 1000) * cost_per_1k_prompt +
                (Decimal(completion_tokens) / 1000) * cost_per_1k_completion
            )
            
            llm_time = time.time() - start_time
            
            metadata = {
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'total_cost': total_cost,
                'llm_time': llm_time,
                'model': self.config.llm_model,
            }
            
            logger.info(f"LLM response generated in {llm_time:.3f}s using {self.config.llm_model}")
            return response_text, metadata
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def query(
        self, 
        query_text: str, 
        user: Optional[User] = None,
        document_ids: Optional[List[str]] = None,
        session_id: Optional[str] = None
    ) -> RAGResponse:
        """
        Main query processing method
        
        Args:
            query_text: User's question/query
            user: User making the query (optional)
            document_ids: Specific documents to search (optional)
            session_id: Session identifier for tracking (optional)
        
        Returns:
            RAGResponse object with complete response and metadata
        """
        total_start_time = time.time()
        
        # Check if this is a conversational query first
        conversational_response = self._conversation_handler.handle_conversational_query(query_text, user)
        if conversational_response:
            response = RAGResponse(
                query=query_text,
                response=conversational_response,
                source_chunks=[],
                total_chunks_found=0,
                search_time=0.0,
                llm_time=0.0,
                total_time=time.time() - total_start_time,
                llm_model=self.config.llm_model,
            )
            self._log_query(query_text, response, user, session_id)
            return response
        
        try:
            # 1. Generate query embedding
            logger.info(f"Processing query: {query_text[:100]}...")
            query_embedding = self.generate_query_embedding(query_text)
            
            # 2. Search for similar chunks
            search_start_time = time.time()
            search_results = self.search_similar_chunks(
                query_embedding, user, document_ids
            )
            search_time = time.time() - search_start_time
            
            if not search_results:
                # No relevant chunks found
                response = RAGResponse(
                    query=query_text,
                    response="I couldn't find any relevant information in the documents to answer your question. Please try rephrasing your query or check if the relevant documents have been uploaded.",
                    source_chunks=[],
                    total_chunks_found=0,
                    search_time=search_time,
                    llm_time=0.0,
                    total_time=time.time() - total_start_time,
                    llm_model=self.config.llm_model,
                )
                
                # Log the query
                self._log_query(query_text, response, user, session_id)
                return response
            
            # 3. Assemble context
            context = self.assemble_context(search_results)
            
            # 4. Create prompt
            prompt = self.create_prompt(query_text, context)
            
            # 5. Generate LLM response
            try:
                # Note: Making this synchronous for now - can be made async later
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                response_text, llm_metadata = loop.run_until_complete(
                    self.generate_llm_response(prompt)
                )
                loop.close()
            except Exception as e:
                logger.error(f"LLM generation failed: {e}")
                response_text = f"I found relevant information but encountered an error generating the response. Please try again. Error: {str(e)}"
                llm_metadata = {
                    'prompt_tokens': 0,
                    'completion_tokens': 0,
                    'total_cost': Decimal('0.0'),
                    'llm_time': 0.0,
                    'model': self.config.llm_model,
                }
            
            # 6. Create response object
            total_time = time.time() - total_start_time
            
            response = RAGResponse(
                query=query_text,
                response=response_text,
                source_chunks=search_results,
                total_chunks_found=len(search_results),
                search_time=search_time,
                llm_time=llm_metadata['llm_time'],
                total_time=total_time,
                llm_model=llm_metadata['model'],
                prompt_tokens=llm_metadata['prompt_tokens'],
                completion_tokens=llm_metadata['completion_tokens'],
                total_cost=llm_metadata['total_cost'],
            )
            
            # 7. Log the query
            self._log_query(query_text, response, user, session_id)
            
            logger.info(f"Query completed in {total_time:.3f}s")
            return response
            
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            
            # Return error response
            error_response = RAGResponse(
                query=query_text,
                response=f"An error occurred while processing your query: {str(e)}",
                source_chunks=[],
                total_chunks_found=0,
                search_time=0.0,
                llm_time=0.0,
                total_time=time.time() - total_start_time,
                llm_model=self.config.llm_model,
            )
            
            # Log the failed query
            self._log_query(query_text, error_response, user, session_id)
            return error_response
    
    def _log_query(
        self, 
        query_text: str, 
        response: RAGResponse, 
        user: Optional[User] = None,
        session_id: Optional[str] = None
    ) -> QueryLog:
        """Log query and response to database"""
        try:
            with transaction.atomic():
                query_log = QueryLog.objects.create(
                    query_text=query_text,
                    user=user,
                    session_id=session_id or '',
                    response_text=response.response,
                    similarity_threshold=self.config.similarity_threshold,
                    chunks_found=response.total_chunks_found,
                    llm_model=response.llm_model,
                    llm_provider='openrouter',
                    prompt_tokens=response.prompt_tokens,
                    completion_tokens=response.completion_tokens,
                    total_cost=response.total_cost,
                    search_time=response.search_time,
                    llm_time=response.llm_time,
                    total_time=response.total_time,
                )
                
                # Add source chunks
                if response.source_chunks:
                    chunks = [result.chunk for result in response.source_chunks]
                    query_log.source_chunks.set(chunks)
                
                logger.info(f"Query logged with ID: {query_log.id}")
                return query_log
                
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            # Don't fail the main query if logging fails
            return None


# Convenience function for quick queries
def quick_query(query_text: str, user: Optional[User] = None) -> RAGResponse:
    """
    Convenience function for quick RAG queries
    
    Args:
        query_text: User's question
        user: User making the query (optional)
    
    Returns:
        RAGResponse object
    """
    engine = RAGQueryEngine()
    return engine.query(query_text, user=user)
