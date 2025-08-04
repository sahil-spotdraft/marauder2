"""
URL configuration for chat app
"""

from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Main chat interface
    path('', views.home, name='home'),
    
    # API endpoints
    path('api/', views.ChatAPI.as_view(), name='chat_api'),
    path('suggestions/', views.suggestions_api, name='suggestions_api'),
    path('health/', views.health_check, name='health_check'),
    path('debug/', views.debug_api, name='debug_api'),
    
    # User-specific endpoints
    path('user/history/', views.user_history_api, name='user_history_api'),
    path('user/feedback/', views.user_feedback_api, name='user_feedback_api'),
    path('user/stats/', views.user_stats_api, name='user_stats_api'),
]