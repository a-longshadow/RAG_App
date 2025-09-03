"""
OpenRouter API client with model selection and management
"""
import os
import requests
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ModelInfo:
    """Information about an available model"""
    id: str
    name: str
    description: str
    pricing: Dict[str, float]
    context_length: int
    provider: str

class OpenRouterClient:
    """
    Client for interacting with OpenRouter API
    Provides model listing, selection, and chat completion
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter client
        
        Args:
            api_key: OpenRouter API key (defaults to environment variable)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.base_url = "https://openrouter.ai/api/v1"
        # Use a free model as default - Google Gemini Flash 2.5 is typically free
        self.default_model = os.getenv('OPENROUTER_DEFAULT_MODEL', 'google/gemini-2.5-flash')
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not configured")
    
    def get_headers(self) -> Dict[str, str]:
        """Get headers for OpenRouter API requests"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "RAG Document System",
        }
    
    def get_available_models(self) -> List[ModelInfo]:
        """
        Fetch available models from OpenRouter
        
        Returns:
            List of ModelInfo objects
        """
        if not self.api_key:
            logger.warning("No API key available for fetching models")
            return self._get_default_models()
        
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.get_headers(),
                timeout=30
            )
            response.raise_for_status()
            
            models_data = response.json()
            models = []
            
            for model_data in models_data.get('data', []):
                try:
                    # Sanitize pricing data
                    pricing = model_data.get('pricing', {})
                    
                    # Ensure pricing values are floats
                    sanitized_pricing = {}
                    for key, value in pricing.items():
                        try:
                            sanitized_pricing[key] = float(value) if value is not None else 0.0
                        except (ValueError, TypeError):
                            sanitized_pricing[key] = 0.0
                    
                    # Ensure context_length is an integer
                    context_length = model_data.get('context_length', 4096)
                    try:
                        context_length = int(context_length) if context_length is not None else 4096
                    except (ValueError, TypeError):
                        context_length = 4096
                    
                    model = ModelInfo(
                        id=model_data['id'],
                        name=model_data.get('name', model_data['id']),
                        description=model_data.get('description', ''),
                        pricing=sanitized_pricing,
                        context_length=context_length,
                        provider=model_data.get('id', '').split('/')[0] if '/' in model_data.get('id', '') else 'unknown'
                    )
                    models.append(model)
                except Exception as e:
                    logger.warning(f"Error parsing model data: {e}")
                    continue
            
            # Filter to recommended models for RAG
            filtered_models = self._filter_recommended_models(models)
            logger.info(f"Found {len(filtered_models)} recommended models")
            return filtered_models
            
        except Exception as e:
            logger.error(f"Error fetching models from OpenRouter: {e}")
            return self._get_default_models()
    
    def _filter_recommended_models(self, models: List[ModelInfo]) -> List[ModelInfo]:
        """Filter to models that work well for RAG applications"""
        
        # Get ALL models, don't filter by specific IDs
        # Sort by provider and context length for better organization
        filtered = []
        
        for model in models:
            # Only filter out models that are clearly not suitable for text generation
            model_id_lower = model.id.lower()
            
            # Skip models that are clearly not for text generation
            skip_keywords = [
                'whisper', 'dall-e', 'tts-', 'embedding', 'moderation',
                'vision-only', 'audio-only', 'image-only'
            ]
            
            if any(keyword in model_id_lower for keyword in skip_keywords):
                continue
                
            # Skip models with very low context length (less than 1000 tokens)
            if model.context_length < 1000:
                continue
                
            filtered.append(model)
        
        # Sort by provider name, then by context length (descending)
        return sorted(filtered, key=lambda x: (x.provider, -x.context_length))
    
    def _get_default_models(self) -> List[ModelInfo]:
        """Return expanded default model list when API is unavailable"""
        return [
            # Anthropic models
            ModelInfo(
                id="anthropic/claude-3-haiku",
                name="Claude 3 Haiku",
                description="Fast, accurate, and affordable model",
                pricing={"prompt": 0.00025, "completion": 0.00125},
                context_length=200000,
                provider="anthropic"
            ),
            ModelInfo(
                id="anthropic/claude-3-sonnet",
                name="Claude 3 Sonnet", 
                description="Balanced intelligence and speed",
                pricing={"prompt": 0.003, "completion": 0.015},
                context_length=200000,
                provider="anthropic"
            ),
            ModelInfo(
                id="anthropic/claude-3-opus",
                name="Claude 3 Opus",
                description="Most powerful Claude model",
                pricing={"prompt": 0.015, "completion": 0.075},
                context_length=200000,
                provider="anthropic"
            ),
            ModelInfo(
                id="anthropic/claude-3.5-sonnet",
                name="Claude 3.5 Sonnet",
                description="Latest Claude model with enhanced capabilities",
                pricing={"prompt": 0.003, "completion": 0.015},
                context_length=200000,
                provider="anthropic"
            ),
            # Google models (including newer Gemini versions)
            ModelInfo(
                id="google/gemini-pro",
                name="Gemini Pro",
                description="Google's advanced multimodal model",
                pricing={"prompt": 0.000125, "completion": 0.000375},
                context_length=30720,
                provider="google"
            ),
            ModelInfo(
                id="google/gemini-flash-1.5",
                name="Gemini 1.5 Flash",
                description="Fast and efficient Gemini model",
                pricing={"prompt": 0.000075, "completion": 0.0003},
                context_length=1048576,
                provider="google"
            ),
            ModelInfo(
                id="google/gemini-pro-1.5",
                name="Gemini 1.5 Pro",
                description="Advanced Gemini with long context",
                pricing={"prompt": 0.00125, "completion": 0.005},
                context_length=2097152,
                provider="google"
            ),
            # OpenAI models
            ModelInfo(
                id="openai/gpt-4o-mini",
                name="GPT-4o Mini",
                description="OpenAI's efficient model",
                pricing={"prompt": 0.00015, "completion": 0.0006},
                context_length=128000,
                provider="openai"
            ),
            ModelInfo(
                id="openai/gpt-4o",
                name="GPT-4o",
                description="OpenAI's latest multimodal model",
                pricing={"prompt": 0.005, "completion": 0.015},
                context_length=128000,
                provider="openai"
            ),
            # Meta Llama models
            ModelInfo(
                id="meta-llama/llama-3.1-8b-instruct",
                name="Llama 3.1 8B",
                description="Open source model with good performance",
                pricing={"prompt": 0.0000005, "completion": 0.0000005},
                context_length=131072,
                provider="meta-llama"
            ),
            ModelInfo(
                id="meta-llama/llama-3.1-70b-instruct",
                name="Llama 3.1 70B",
                description="Large open source model with excellent performance",
                pricing={"prompt": 0.000004, "completion": 0.000004},
                context_length=131072,
                provider="meta-llama"
            ),
        ]
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request to OpenRouter
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model ID to use (defaults to configured default)
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary from OpenRouter API
        """
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not configured. Please add your OpenRouter API key to the .env file.")
        
        model = model or self.default_model
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            logger.info(f"Making OpenRouter API request to model: {model}")
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.get_headers(),
                json=data,
                timeout=60
            )
            
            # Enhanced error handling with specific status codes
            if response.status_code == 401:
                raise ValueError("Invalid OpenRouter API key. Please check your OPENROUTER_API_KEY in .env file.")
            elif response.status_code == 404:
                raise ValueError(f"Model '{model}' not found or not accessible with your API key. Try a different model.")
            elif response.status_code == 429:
                raise ValueError("Rate limit exceeded. Please wait a moment and try again.")
            elif response.status_code == 503:
                raise ValueError("OpenRouter service temporarily unavailable. Please try again later.")
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"OpenRouter API request successful for model: {model}")
            return result
            
        except requests.exceptions.Timeout:
            raise ValueError("Request timed out. OpenRouter service may be slow. Please try again.")
        except requests.exceptions.ConnectionError:
            raise ValueError("Cannot connect to OpenRouter. Please check your internet connection.")
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', {}).get('message', str(e))
                    raise ValueError(f"OpenRouter API error: {error_msg}")
                except:
                    pass
            raise ValueError(f"OpenRouter API request failed: {str(e)}")
    
    def simple_chat(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple chat interface - send prompt, get response text
        
        Args:
            prompt: User prompt/question
            model: Model ID to use
            **kwargs: Additional parameters
            
        Returns:
            Response text from the model
        """
        messages = [{"role": "user", "content": prompt}]
        response = self.chat_completion(messages, model, **kwargs)
        return response['choices'][0]['message']['content']
    
    def test_connection(self) -> bool:
        """
        Test if the API key and connection work
        
        Returns:
            True if connection successful, False otherwise
        """
        if not self.api_key:
            return False
        
        try:
            # Simple test request
            messages = [{"role": "user", "content": "Hello"}]
            self.chat_completion(messages, max_tokens=10)
            return True
        except Exception as e:
            logger.warning(f"OpenRouter connection test failed: {e}")
            return False

# Global client instance
_client = None

def get_openrouter_client() -> OpenRouterClient:
    """Get global OpenRouter client instance"""
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client
