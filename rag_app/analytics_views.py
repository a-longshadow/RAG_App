from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Sum, Max, Min
from django.db.models.functions import TruncDate, TruncHour
from django.utils import timezone
from datetime import timedelta, datetime
import json

from .models import (Document, DocumentChunk, QuerySession, ConversationHistory, 
                     SystemAnalytics, QuerySuggestion, User)


@login_required
def analytics_dashboard(request):
    """
    Main analytics dashboard view
    """
    # Check if user is staff (admin)
    if not request.user.is_staff:
        return render(request, 'rag_app/access_denied.html', {
            'message': 'Analytics dashboard is only available to administrators.'
        })
    
    # Get time range from request (default: last 30 days)
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Document statistics
    total_documents = Document.objects.count()
    documents_by_status = Document.objects.values('status').annotate(count=Count('id'))
    documents_by_type = Document.objects.values('file_type').annotate(count=Count('id'))
    
    # Recent document uploads (last 30 days)
    recent_uploads = Document.objects.filter(
        uploaded_at__gte=start_date
    ).annotate(
        date=TruncDate('uploaded_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Query statistics
    total_queries = ConversationHistory.objects.count()
    unique_users = ConversationHistory.objects.values('session__user').distinct().count()
    avg_response_time = ConversationHistory.objects.aggregate(
        avg_time=Avg('total_response_time_ms')
    )['avg_time'] or 0
    
    # Popular documents (most queried)
    popular_documents = ConversationHistory.objects.values(
        'documents_used__title'
    ).annotate(
        query_count=Count('id')
    ).order_by('-query_count')[:10]
    
    # User activity
    active_users = ConversationHistory.objects.filter(
        created_at__gte=start_date
    ).values(
        'session__user__username'
    ).annotate(
        query_count=Count('id'),
        avg_response_time=Avg('total_response_time_ms')
    ).order_by('-query_count')[:10]
    
    # Query performance over time
    query_performance = ConversationHistory.objects.filter(
        created_at__gte=start_date
    ).annotate(
        hour=TruncHour('created_at')
    ).values('hour').annotate(
        count=Count('id'),
        avg_time=Avg('total_response_time_ms')
    ).order_by('hour')
    
    # System health metrics
    error_rate = SystemAnalytics.objects.filter(
        category='errors',
        recorded_at__gte=start_date
    ).count()
    
    total_requests = ConversationHistory.objects.filter(
        created_at__gte=start_date
    ).count()
    
    error_percentage = (error_rate / max(total_requests, 1)) * 100
    
    context = {
        'total_documents': total_documents,
        'total_queries': total_queries,
        'unique_users': unique_users,
        'avg_response_time': round(avg_response_time, 2),
        'error_percentage': round(error_percentage, 2),
        'documents_by_status': list(documents_by_status),
        'documents_by_type': list(documents_by_type),
        'recent_uploads': list(recent_uploads),
        'popular_documents': list(popular_documents),
        'active_users': list(active_users),
        'query_performance': list(query_performance),
        'days': days,
    }
    
    return render(request, 'rag_app/analytics_dashboard.html', context)


@login_required
def analytics_api(request):
    """
    API endpoint for analytics data (AJAX requests)
    """
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    metric = request.GET.get('metric')
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    if metric == 'query_trends':
        data = ConversationHistory.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return JsonResponse({
            'labels': [item['date'].strftime('%Y-%m-%d') for item in data],
            'values': [item['count'] for item in data]
        })
    
    elif metric == 'response_times':
        data = ConversationHistory.objects.filter(
            created_at__gte=start_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            avg_time=Avg('total_response_time_ms')
        ).order_by('date')
        
        return JsonResponse({
            'labels': [item['date'].strftime('%Y-%m-%d') for item in data],
            'values': [round(item['avg_time'] or 0, 2) for item in data]
        })
    
    elif metric == 'document_usage':
        data = ConversationHistory.objects.filter(
            created_at__gte=start_date
        ).values(
            'documents_used__title'
        ).annotate(
            usage_count=Count('id')
        ).order_by('-usage_count')[:20]
        
        return JsonResponse({
            'labels': [item['documents_used__title'] or 'Unknown' for item in data],
            'values': [item['usage_count'] for item in data]
        })
    
    elif metric == 'user_activity':
        data = ConversationHistory.objects.filter(
            created_at__gte=start_date
        ).values(
            'session__user__username'
        ).annotate(
            query_count=Count('id')
        ).order_by('-query_count')[:15]
        
        return JsonResponse({
            'labels': [item['session__user__username'] for item in data],
            'values': [item['query_count'] for item in data]
        })
    
    return JsonResponse({'error': 'Invalid metric'}, status=400)


@login_required 
def conversation_history(request):
    """
    View for browsing conversation history
    """
    # Get user's own sessions or all sessions if staff
    if request.user.is_staff:
        sessions = QuerySession.objects.all()
    else:
        sessions = QuerySession.objects.filter(user=request.user)
    
    # Filter by search query
    search = request.GET.get('search', '')
    if search:
        sessions = sessions.filter(
            conversations__query_text__icontains=search
        ).distinct()
    
    # Order by last activity
    sessions = sessions.order_by('-last_activity')[:50]
    
    context = {
        'sessions': sessions,
        'search': search,
    }
    
    return render(request, 'rag_app/conversation_history.html', context)


@login_required
def session_detail(request, session_id):
    """
    Detailed view of a specific conversation session
    """
    # Get session (user can only see their own unless staff)
    if request.user.is_staff:
        session = QuerySession.objects.get(id=session_id)
    else:
        session = QuerySession.objects.get(id=session_id, user=request.user)
    
    # Get all conversations in this session
    conversations = ConversationHistory.objects.filter(
        session=session
    ).order_by('created_at')
    
    # Calculate session statistics
    stats = {
        'total_queries': conversations.count(),
        'avg_response_time': conversations.aggregate(Avg('total_response_time_ms'))['total_response_time_ms__avg'] or 0,
        'total_tokens': conversations.aggregate(Sum('tokens_used'))['tokens_used__sum'] or 0,
        'bookmarked_count': conversations.filter(is_bookmarked=True).count(),
    }
    
    context = {
        'session': session,
        'conversations': conversations,
        'stats': stats,
    }
    
    return render(request, 'rag_app/session_detail.html', context)


@login_required
def bookmark_conversation(request, conversation_id):
    """
    Toggle bookmark status of a conversation
    """
    if request.method == 'POST':
        conversation = ConversationHistory.objects.get(
            id=conversation_id,
            session__user=request.user  # User can only bookmark their own conversations
        )
        
        conversation.is_bookmarked = not conversation.is_bookmarked
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'bookmarked': conversation.is_bookmarked
        })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def rate_conversation(request, conversation_id):
    """
    Rate a conversation response
    """
    if request.method == 'POST':
        conversation = ConversationHistory.objects.get(
            id=conversation_id,
            session__user=request.user
        )
        
        rating = int(request.POST.get('rating'))
        feedback = request.POST.get('feedback', '')
        
        if 1 <= rating <= 5:
            conversation.user_rating = rating
            conversation.user_feedback = feedback
            conversation.save()
            
            return JsonResponse({
                'success': True,
                'rating': rating
            })
    
    return JsonResponse({'error': 'Invalid request'}, status=400)
