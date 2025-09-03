"""
Views for OpenRouter model management and selection
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from typing import List
from .openrouter_client import get_openrouter_client
import logging

logger = logging.getLogger(__name__)

@login_required
@require_GET
def model_selection(request):
    """
    Display available OpenRouter models for selection
    """
    client = get_openrouter_client()
    
    # Test connection
    connection_status = client.test_connection()
    
    # Get available models
    models = client.get_available_models()
    
    # Group models by provider
    models_by_provider = {}
    for model in models:
        provider = model.provider
        if provider not in models_by_provider:
            models_by_provider[provider] = []
        models_by_provider[provider].append(model)
    
    context = {
        'models_by_provider': models_by_provider,
        'connection_status': connection_status,
        'api_key_configured': bool(client.api_key),
        'default_model': client.default_model,
        'total_models': len(models)
    }
    
    return render(request, 'rag_app/model_selection.html', context)

@login_required
@require_GET
def models_api(request):
    """
    API endpoint to get available models as JSON with search and filtering
    """
    try:
        client = get_openrouter_client()
        models = client.get_available_models()
        
        # Get search and filter parameters
        search_query = request.GET.get('q', '').lower().strip()
        provider_filter = request.GET.get('provider', '').lower().strip()
        category_filter = request.GET.get('category', '').lower().strip()
        max_price = request.GET.get('max_price', '')
        min_context = request.GET.get('min_context', '')
        sort_by = request.GET.get('sort', 'name')  # name, price, context, provider
        
        # Filter models based on search criteria
        filtered_models = []
        
        for model in models:
            # Search filter - check name, provider, description
            if search_query:
                searchable_text = f"{model.name} {model.provider} {model.description}".lower()
                if search_query not in searchable_text:
                    continue
            
            # Provider filter
            if provider_filter and provider_filter != model.provider.lower():
                continue
            
            # Category filter (basic categorization)
            if category_filter:
                model_categories = get_model_categories(model)
                if category_filter not in model_categories:
                    continue
            
            # Price filter
            if max_price:
                try:
                    max_price_val = float(max_price)
                    completion_price = model.pricing.get('completion', 0)
                    # Pricing data is now sanitized to be float at source
                    if completion_price > max_price_val:
                        continue
                except (ValueError, TypeError):
                    # Skip models with invalid pricing data
                    continue
            
            # Context length filter
            if min_context:
                try:
                    min_context_val = int(min_context)
                    if model.context_length < min_context_val:
                        continue
                except ValueError:
                    pass
            
            filtered_models.append(model)
        
        # Sort models - data is now sanitized in OpenRouterClient
        if sort_by == 'price':
            filtered_models.sort(key=lambda x: x.pricing.get('completion', 0))
        elif sort_by == 'context':
            filtered_models.sort(key=lambda x: x.context_length, reverse=True)
        elif sort_by == 'provider':
            filtered_models.sort(key=lambda x: x.provider)
        else:  # default: name
            filtered_models.sort(key=lambda x: x.name)
        
        models_data = []
        for model in filtered_models:
            models_data.append({
                'id': model.id,
                'name': model.name,
                'description': model.description,
                'provider': model.provider,
                'context_length': model.context_length,
                'pricing': model.pricing,
                'categories': get_model_categories(model)
            })
        
        return JsonResponse({
            'success': True,
            'models': models_data,
            'total_count': len(models_data),
            'filtered_count': len(models_data),
            'connection_status': client.test_connection(),
            'default_model': client.default_model,
            'search_params': {
                'query': search_query,
                'provider': provider_filter,
                'category': category_filter,
                'max_price': max_price,
                'min_context': min_context,
                'sort': sort_by
            }
        })
        
    except Exception as e:
        logger.error(f"Error in models API: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
            'models': []
        })


def get_model_categories(model) -> List[str]:
    """Categorize model based on its properties"""
    categories = []
    
    # Provider-based categories
    if 'anthropic' in model.provider.lower():
        categories.append('claude')
    elif 'openai' in model.provider.lower():
        categories.append('gpt')
    elif 'google' in model.provider.lower():
        categories.append('gemini')
    elif 'meta' in model.provider.lower():
        categories.append('llama')
    
    # Speed categories based on pricing and context
    completion_price = model.pricing.get('completion', 0)
    if completion_price < 0.001:
        categories.append('budget')
    elif completion_price < 0.01:
        categories.append('fast')
    else:
        categories.append('premium')
    
    # Context length categories
    if model.context_length >= 128000:
        categories.append('long-context')
    elif model.context_length >= 32000:
        categories.append('medium-context')
    else:
        categories.append('standard-context')
    
    # Model type categories based on name
    model_name_lower = model.name.lower()
    if any(word in model_name_lower for word in ['chat', 'instruct', 'turbo']):
        categories.append('chat')
    if any(word in model_name_lower for word in ['reasoning', 'thinking', 'analysis']):
        categories.append('reasoning')
    if any(word in model_name_lower for word in ['code', 'coding', 'programming']):
        categories.append('coding')
    
    return categories

@login_required 
@require_GET
def test_model(request):
    """
    Test a specific model with a simple query
    """
    model_id = request.GET.get('model')
    if not model_id:
        return JsonResponse({'success': False, 'error': 'Model ID required'})
    
    try:
        client = get_openrouter_client()
        
        # Simple test prompt
        test_prompt = "Hello! Please respond with 'Model test successful' to confirm you're working."
        
        response = client.simple_chat(
            prompt=test_prompt,
            model=model_id,
            max_tokens=50,
            temperature=0.1
        )
        
        return JsonResponse({
            'success': True,
            'model': model_id,
            'response': response.strip(),
            'message': f'Model {model_id} is working correctly'
        })
        
    except Exception as e:
        logger.error(f"Error testing model {model_id}: {e}")
        return JsonResponse({
            'success': False,
            'model': model_id,
            'error': str(e),
            'message': f'Model {model_id} test failed'
        })

@login_required
def select_model(request):
    """
    Set the selected model for the user session
    """
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            model_id = data.get('model_id')
            
            if not model_id:
                return JsonResponse({'success': False, 'error': 'Model ID required'})
            
            # Store in session
            request.session['selected_model'] = model_id
            request.session.save()
            
            logger.info(f"User {request.user.username} selected model: {model_id}")
            
            return JsonResponse({
                'success': True,
                'model': model_id,
                'message': f'Model {model_id} selected successfully'
            })
            
        except Exception as e:
            logger.error(f"Error selecting model: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'POST method required'})
