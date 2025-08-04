"""
Django Views for RAG Chat Application
=====================================
"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.views import View
from django.utils.decorators import method_decorator
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import json
import logging
import time
import uuid

from .rag_service import RAGService
from .models import ChatHistory, UserSession

logger = logging.getLogger(__name__)

# Initialize RAG service (singleton pattern)
rag_service = None

def get_rag_service():
    """Get or create RAG service instance"""
    global rag_service
    if rag_service is None:
        try:
            rag_service = RAGService()
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {str(e)}")
            return None
    return rag_service

def home(request):
    """Main chat interface"""
    service = get_rag_service()
    
    context = {
        'title': 'Universal RAG System',
        'knowledge_base_available': service is not None
    }
    
    if service:
        kb_info = service.get_knowledge_base_info()
        suggestions = service.get_query_suggestions()
        
        context.update({
            'total_chunks': kb_info['total_chunks'],
            'total_files': len(kb_info['file_sources']),
            'file_types': kb_info['file_types'],
            'suggestions': suggestions[:6]  # Show first 6 suggestions
        })
    
    return render(request, 'chat/index.html', context)

@method_decorator(csrf_exempt, name='dispatch')
class ChatAPI(View):
    """API endpoint for chat functionality"""
    
    def post(self, request):
        """Handle chat messages"""
        start_time = time.time()
        
        try:
            # Parse request
            data = json.loads(request.body)
            user_query = data.get('query', '').strip()
            user_email = data.get('user_email', '').strip()
            session_id = data.get('session_id', None)
            use_db_history = data.get('use_db_history', True)
            
            if not user_query:
                return JsonResponse({
                    'success': False,
                    'error': 'Query is required'
                }, status=400)
            
            # Validate email if provided
            if user_email:
                try:
                    validate_email(user_email)
                except ValidationError:
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid email address format'
                    }, status=400)
            
            # Get RAG service
            service = get_rag_service()
            if not service:
                return JsonResponse({
                    'success': False,
                    'error': 'RAG service is not available. Please check if the knowledge base is properly initialized.'
                }, status=503)
            
            # Get conversation history
            conversation_history = []
            if user_email and use_db_history:
                # Load from database
                conversation_history = ChatHistory.get_user_history(user_email, limit=5)
            else:
                # Use provided history (for backward compatibility)
                conversation_history = data.get('history', [])
            
            # Process query
            result = service.process_query(user_query, conversation_history)
            
            # Calculate response time
            response_time = int((time.time() - start_time) * 1000)
            result['response_time_ms'] = response_time
            
            # Save to database if user email is provided and query was successful
            if user_email and result.get('success'):
                try:
                    # Update user session
                    user_session, created = UserSession.objects.get_or_create(
                        user_email=user_email,
                        defaults={
                            'session_id': session_id or str(uuid.uuid4()),
                            'preferences': {}
                        }
                    )
                    
                    if session_id and user_session.session_id != session_id:
                        user_session.session_id = session_id
                        user_session.save()
                    
                    user_session.update_activity()
                    
                    # Save chat exchange
                    metadata = {
                        'complexity': result.get('complexity'),
                        'chunks_found': result.get('chunks_found'),
                        'retrieved_sources': result.get('retrieved_sources', []),
                        'intent_analysis': result.get('intent_analysis', {}),
                        'response_time_ms': response_time
                    }
                    
                    ChatHistory.save_exchange(
                        user_email=user_email,
                        user_query=user_query,
                        ai_response=result.get('ai_response', ''),
                        metadata=metadata,
                        session_id=user_session.session_id
                    )
                    
                    result['saved_to_history'] = True
                    result['session_id'] = user_session.session_id
                    
                except Exception as e:
                    logger.error(f"Error saving chat history: {str(e)}")
                    result['saved_to_history'] = False
                    result['history_error'] = str(e)
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON in request body'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in chat API: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'Internal server error'
            }, status=500)
    
    def get(self, request):
        """Get knowledge base information"""
        service = get_rag_service()
        if not service:
            return JsonResponse({
                'success': False,
                'error': 'RAG service not available'
            }, status=503)
        
        kb_info = service.get_knowledge_base_info()
        suggestions = service.get_query_suggestions()
        
        return JsonResponse({
            'success': True,
            'knowledge_base': kb_info,
            'suggestions': suggestions
        })

@require_http_methods(["GET"])
def suggestions_api(request):
    """Get query suggestions"""
    service = get_rag_service()
    if not service:
        return JsonResponse({
            'success': False,
            'error': 'RAG service not available'
        }, status=503)
    
    # Get conversation history from query params for contextual suggestions
    history_param = request.GET.get('history', '[]')
    try:
        conversation_history = json.loads(history_param)
    except json.JSONDecodeError:
        conversation_history = []
    
    suggestions = service.get_conversation_suggestions(conversation_history)
    
    return JsonResponse({
        'success': True,
        'suggestions': suggestions
    })

@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint"""
    service = get_rag_service()
    
    if service:
        kb_info = service.get_knowledge_base_info()
        return JsonResponse({
            'status': 'healthy',
            'rag_service': 'available',
            'knowledge_base': {
                'total_chunks': kb_info['total_chunks'],
                'total_files': len(kb_info['file_sources']),
                'file_types': list(kb_info['file_types'].keys())
            }
        })
    else:
        return JsonResponse({
            'status': 'unhealthy',
            'rag_service': 'unavailable',
            'error': 'Could not initialize RAG service'
        }, status=503)

@require_http_methods(["POST"])
@csrf_exempt
def debug_api(request):
    """Debug endpoint for development"""
    try:
        data = json.loads(request.body)
        user_query = data.get('query', '').strip()
        
        if not user_query:
            return JsonResponse({
                'success': False,
                'error': 'Query is required'
            }, status=400)
        
        service = get_rag_service()
        if not service:
            return JsonResponse({
                'success': False,
                'error': 'RAG service not available'
            }, status=503)
        
        # Get detailed debug information
        result = service.process_query(user_query, [])
        
        # Add extra debug info
        debug_info = {
            'query_analysis': {
                'complexity': result.get('complexity'),
                'intent': result.get('intent_analysis'),
                'chunks_retrieved': result.get('chunks_found')
            },
            'retrieval_info': {
                'file_types': result.get('retrieved_file_types'),
                'content_types': result.get('retrieved_content_types'),
                'sources': result.get('retrieved_sources')
            },
            'chunks_detail': result.get('chunks_info', [])
        }
        
        return JsonResponse({
            'success': result.get('success'),
            'query': result.get('query'),
            'ai_response': result.get('ai_response'),
            'debug_info': debug_info,
            'error': result.get('error')
        })
        
    except Exception as e:
        logger.error(f"Error in debug API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Debug API error: {str(e)}'
        }, status=500)

@require_http_methods(["GET"])
def user_history_api(request):
    """Get chat history for a user"""
    user_email = request.GET.get('user_email', '').strip()
    
    if not user_email:
        return JsonResponse({
            'success': False,
            'error': 'user_email parameter is required'
        }, status=400)
    
    try:
        validate_email(user_email)
    except ValidationError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid email address format'
        }, status=400)
    
    try:
        limit = int(request.GET.get('limit', 20))
        limit = min(limit, 100)  # Cap at 100 entries
    except ValueError:
        limit = 20
    
    try:
        # Get chat history
        history_tuples = ChatHistory.get_user_history(user_email, limit=limit)
        
        # Get detailed history objects for additional metadata
        history_objects = ChatHistory.objects.filter(
            user_email=user_email
        ).order_by('-created_at')[:limit]
        
        detailed_history = []
        for i, chat in enumerate(reversed(history_objects)):
            detailed_history.append({
                'id': chat.id,
                'user_query': chat.user_query,
                'ai_response': chat.ai_response,
                'complexity': chat.query_complexity,
                'chunks_found': chat.chunks_found,
                'retrieved_sources': chat.retrieved_sources,
                'created_at': chat.created_at.isoformat(),
                'response_time_ms': chat.response_time_ms,
                'is_helpful': chat.is_helpful
            })
        
        # Get user stats
        user_stats = ChatHistory.get_user_stats(user_email)
        
        return JsonResponse({
            'success': True,
            'user_email': user_email,
            'history': history_tuples,
            'detailed_history': detailed_history,
            'user_stats': user_stats
        })
        
    except Exception as e:
        logger.error(f"Error in user history API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["POST"])
@csrf_exempt
def user_feedback_api(request):
    """Submit user feedback for a chat response"""
    try:
        data = json.loads(request.body)
        chat_id = data.get('chat_id')
        is_helpful = data.get('is_helpful')
        feedback_notes = data.get('feedback_notes', '').strip()
        
        if not chat_id:
            return JsonResponse({
                'success': False,
                'error': 'chat_id is required'
            }, status=400)
        
        if is_helpful is None:
            return JsonResponse({
                'success': False,
                'error': 'is_helpful is required (true/false)'
            }, status=400)
        
        try:
            chat_entry = ChatHistory.objects.get(id=chat_id)
            chat_entry.is_helpful = is_helpful
            if feedback_notes:
                chat_entry.feedback_notes = feedback_notes
            chat_entry.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Feedback saved successfully'
            })
            
        except ChatHistory.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Chat entry not found'
            }, status=404)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON in request body'
        }, status=400)
    except Exception as e:
        logger.error(f"Error in user feedback API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

@require_http_methods(["GET"])
def user_stats_api(request):
    """Get usage statistics for a user"""
    user_email = request.GET.get('user_email', '').strip()
    
    if not user_email:
        return JsonResponse({
            'success': False,
            'error': 'user_email parameter is required'
        }, status=400)
    
    try:
        validate_email(user_email)
    except ValidationError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid email address format'
        }, status=400)
    
    try:
        stats = ChatHistory.get_user_stats(user_email)
        
        # Get user session info
        try:
            user_session = UserSession.objects.get(user_email=user_email)
            session_info = {
                'first_visit': user_session.first_visit.isoformat(),
                'last_activity': user_session.last_activity.isoformat(),
                'current_session_id': user_session.session_id,
                'preferences': user_session.preferences
            }
        except UserSession.DoesNotExist:
            session_info = None
        
        return JsonResponse({
            'success': True,
            'user_email': user_email,
            'chat_stats': stats,
            'session_info': session_info
        })
        
    except Exception as e:
        logger.error(f"Error in user stats API: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)