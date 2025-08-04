"""
Django Models for Chat Application
==================================
"""

from django.db import models
from django.utils import timezone
import json


class ChatHistory(models.Model):
    """
    Model to store chat conversation history for users
    """
    
    # User identification
    user_email = models.EmailField(
        max_length=255,
        help_text="User's email address for session identification"
    )
    
    # Session information
    session_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        help_text="Optional session identifier for grouping conversations"
    )
    
    # Message content
    user_query = models.TextField(
        help_text="The user's question or query"
    )
    
    ai_response = models.TextField(
        help_text="The AI's response to the query"
    )
    
    # Query metadata
    query_complexity = models.CharField(
        max_length=20,
        choices=[
            ('simple', 'Simple'),
            ('medium', 'Medium'),
            ('complex', 'Complex'),
            ('technical', 'Technical'),
        ],
        default='simple',
        help_text="Complexity level of the query"
    )
    
    chunks_found = models.IntegerField(
        default=0,
        help_text="Number of relevant chunks retrieved"
    )
    
    retrieved_sources = models.JSONField(
        default=list,
        help_text="List of source files that contributed to the response"
    )
    
    # Response metadata
    response_time_ms = models.IntegerField(
        blank=True,
        null=True,
        help_text="Response time in milliseconds"
    )
    
    intent_analysis = models.JSONField(
        default=dict,
        blank=True,
        help_text="AI intent analysis results"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When this conversation exchange occurred"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last updated timestamp"
    )
    
    # Additional metadata
    is_helpful = models.BooleanField(
        blank=True,
        null=True,
        help_text="User feedback: was this response helpful?"
    )
    
    feedback_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Optional user feedback notes"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Chat History"
        verbose_name_plural = "Chat Histories"
        indexes = [
            models.Index(fields=['user_email', '-created_at']),
            models.Index(fields=['session_id', '-created_at']),
            models.Index(fields=['query_complexity']),
        ]
    
    def __str__(self):
        return f"{self.user_email}: {self.user_query[:50]}..."
    
    @classmethod
    def get_user_history(cls, user_email, limit=10):
        """
        Get recent chat history for a user
        
        Args:
            user_email (str): User's email address
            limit (int): Maximum number of exchanges to return
            
        Returns:
            list: List of (query, response) tuples
        """
        history = cls.objects.filter(
            user_email=user_email
        ).order_by('-created_at')[:limit]
        
        return [(h.user_query, h.ai_response) for h in reversed(history)]
    
    @classmethod
    def save_exchange(cls, user_email, user_query, ai_response, metadata=None, session_id=None):
        """
        Save a chat exchange to the database
        
        Args:
            user_email (str): User's email address
            user_query (str): User's question
            ai_response (str): AI's response
            metadata (dict): Additional metadata from RAG service
            session_id (str): Optional session identifier
            
        Returns:
            ChatHistory: Created chat history object
        """
        if metadata is None:
            metadata = {}
        
        chat_entry = cls.objects.create(
            user_email=user_email,
            session_id=session_id,
            user_query=user_query,
            ai_response=ai_response,
            query_complexity=metadata.get('complexity', 'simple'),
            chunks_found=metadata.get('chunks_found', 0),
            retrieved_sources=metadata.get('retrieved_sources', []),
            intent_analysis=metadata.get('intent_analysis', {}),
            response_time_ms=metadata.get('response_time_ms')
        )
        
        return chat_entry
    
    @classmethod
    def get_user_stats(cls, user_email):
        """
        Get usage statistics for a user
        
        Args:
            user_email (str): User's email address
            
        Returns:
            dict: User statistics
        """
        user_chats = cls.objects.filter(user_email=user_email)
        
        if not user_chats.exists():
            return {
                'total_queries': 0,
                'total_sessions': 0,
                'complexity_breakdown': {},
                'most_recent': None,
                'avg_chunks_retrieved': 0
            }
        
        complexity_counts = {}
        for complexity, _ in cls._meta.get_field('query_complexity').choices:
            complexity_counts[complexity] = user_chats.filter(
                query_complexity=complexity
            ).count()
        
        avg_chunks = user_chats.aggregate(
            models.Avg('chunks_found')
        )['chunks_found__avg'] or 0
        
        return {
            'total_queries': user_chats.count(),
            'total_sessions': user_chats.values('session_id').distinct().count(),
            'complexity_breakdown': complexity_counts,
            'most_recent': user_chats.first().created_at if user_chats.exists() else None,
            'avg_chunks_retrieved': round(avg_chunks, 1)
        }


class UserSession(models.Model):
    """
    Model to track user sessions and preferences
    """
    
    user_email = models.EmailField(
        max_length=255,
        unique=True,
        help_text="User's email address"
    )
    
    session_id = models.CharField(
        max_length=64,
        help_text="Current session identifier"
    )
    
    preferences = models.JSONField(
        default=dict,
        help_text="User preferences (theme, debug mode, etc.)"
    )
    
    first_visit = models.DateTimeField(
        default=timezone.now,
        help_text="First time user accessed the system"
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    
    total_queries = models.IntegerField(
        default=0,
        help_text="Total number of queries made by this user"
    )
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = "User Session"
        verbose_name_plural = "User Sessions"
    
    def __str__(self):
        return f"{self.user_email} (Last active: {self.last_activity})"
    
    def update_activity(self):
        """Update last activity timestamp and increment query count"""
        self.total_queries += 1
        self.save(update_fields=['last_activity', 'total_queries'])