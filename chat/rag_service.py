"""
RAG Service Module
==================

This module provides the core RAG functionality extracted from ask.py
for use in Django views and other applications.
"""

import chromadb
import requests
import json
import os
from collections import Counter
from ai_prompts import (
    determine_query_complexity, 
    create_enhanced_system_prompt,
    create_in_app_assistant_prompt,
    get_query_suggestions,
    analyze_query_intent,
    get_prompt_for_intent
)

class RAGService:
    """
    Service class for RAG operations
    """
    
    def __init__(self, chroma_path="chroma_db", collection_name="universal_content"):
        self.chroma_path = chroma_path
        self.collection_name = collection_name
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = None
        self.knowledge_base_stats = None
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        """Initialize connection to ChromaDB and get collection stats"""
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            
            # Get comprehensive collection statistics
            all_data = self.collection.get()
            total_chunks = len(all_data['ids'])
            
            if total_chunks == 0:
                raise Exception("No content found in the database!")
            
            # Analyze content diversity
            file_types = {}
            content_types = {}
            strategies = {}
            file_sources = set()
            file_extensions = set()
            
            for meta in all_data['metadatas']:
                if meta:
                    # Count file types
                    file_type = meta.get('file_type', 'unknown')
                    file_types[file_type] = file_types.get(file_type, 0) + 1
                    
                    # Count content types
                    content_type = meta.get('content_type', 'unknown')
                    content_types[content_type] = content_types.get(content_type, 0) + 1
                    
                    # Count strategies
                    strategy = meta.get('chunking_strategy', 'unknown')
                    strategies[strategy] = strategies.get(strategy, 0) + 1
                    
                    # Count sources and extensions
                    source = meta.get('source', 'unknown')
                    file_sources.add(source)
                    
                    if '.' in source:
                        ext = '.' + source.split('.')[-1].lower()
                        file_extensions.add(ext)
            
            self.knowledge_base_stats = {
                'total_chunks': total_chunks,
                'file_types': file_types,
                'content_types': content_types,
                'strategies': strategies,
                'file_sources': file_sources,
                'file_extensions': file_extensions
            }
            
            return True
            
        except Exception as e:
            raise Exception(f"Could not initialize RAG service: {str(e)}")
    
    def get_knowledge_base_info(self):
        """Get information about the knowledge base"""
        if not self.knowledge_base_stats:
            return None
            
        stats = self.knowledge_base_stats.copy()
        stats['file_sources'] = list(stats['file_sources'])
        stats['file_extensions'] = list(stats['file_extensions'])
        
        return stats
    
    def get_query_suggestions(self):
        """Get query suggestions based on content"""
        if not self.knowledge_base_stats:
            return []
            
        return get_query_suggestions(
            self.knowledge_base_stats['file_types'], 
            self.knowledge_base_stats['content_types']
        )
    
    def query_ollama(self, prompt, user_question):
        """Query Ollama API for response generation"""
        url = "http://localhost:11434/api/generate"
        
        payload = {
            "model": "llama3.2",
            "prompt": f"{prompt}\n\nUser Question: {user_question}\n\nAssistant:",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 200:
                return {
                    'success': True,
                    'response': response.json()['response']
                }
            else:
                return {
                    'success': False,
                    'error': f"Error: {response.status_code} - {response.text}"
                }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': "Could not connect to Ollama. Make sure Ollama is running with: ollama serve"
            }
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': "Request timed out. The model might be processing a complex response."
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Error: {str(e)}"
            }
    
    def process_query(self, user_query, conversation_history=None):
        """
        Process a user query and return comprehensive results
        
        Args:
            user_query (str): The user's question
            conversation_history (list): Previous conversation exchanges
            
        Returns:
            dict: Complete response with metadata
        """
        
        if not self.collection:
            return {
                'success': False,
                'error': 'RAG service not properly initialized'
            }
        
        # Determine query complexity and retrieval count
        query_complexity, suggested_n_results = determine_query_complexity(user_query)
        
        # Query the collection
        results = self.collection.query(
            query_texts=[user_query],
            n_results=suggested_n_results
        )
        
        if not results['documents'][0]:
            return {
                'success': False,
                'error': 'No relevant information found. Try rephrasing your question.'
            }
        
        # Collect metadata for prompt context
        retrieved_file_types = Counter()
        retrieved_content_types = Counter()
        retrieved_sources = set()
        chunks_info = []
        
        for i, doc in enumerate(results['documents'][0], 1):
            meta = results['metadatas'][0][i-1] if results['metadatas'][0] else {}
            
            source = meta.get('source', 'Unknown file')
            title = meta.get('title', 'No title')
            file_type = meta.get('file_type', 'unknown')
            content_type = meta.get('content_type', 'unknown')
            strategy = meta.get('chunking_strategy', 'unknown')
            chunk_size = meta.get('actual_chunk_size', len(doc))
            
            # Track what was retrieved
            retrieved_file_types[file_type] += 1
            retrieved_content_types[content_type] += 1
            retrieved_sources.add(source)
            
            chunks_info.append({
                'index': i,
                'source': source,
                'title': title[:80] + ('...' if len(title) > 80 else ''),
                'file_type': file_type,
                'content_type': content_type,
                'strategy': strategy,
                'chunk_size': chunk_size,
                'content': doc
            })
        
        # Create in-app assistant prompt with structured format
        intent_analysis = analyze_query_intent(user_query)
        base_prompt = create_enhanced_system_prompt(
            self.knowledge_base_stats['file_types'], 
            self.knowledge_base_stats['content_types'], 
            retrieved_sources,
            query_complexity, 
            retrieved_file_types, 
            results,
            # user_query
        )
        # Note: Using in-app assistant format, so no additional intent prompt needed
        
        # Add conversation history context if available
        history_context = ""
        if conversation_history:
            history_context = f"""

CONVERSATION HISTORY CONTEXT:
The user has asked {len(conversation_history)} previous question(s). Here's the recent conversation:

"""
            # Include last 3 exchanges to avoid overwhelming the context
            recent_history = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
            for i, (prev_q, prev_a) in enumerate(recent_history, 1):
                history_context += f"Previous Q{len(conversation_history) - len(recent_history) + i}: {prev_q}\n"
                # Include a summary of the previous answer (first 200 chars)
                prev_a_summary = prev_a[:200] + "..." if len(prev_a) > 200 else prev_a
                history_context += f"Previous A{len(conversation_history) - len(recent_history) + i}: {prev_a_summary}\n\n"
            
            history_context += """Use this conversation history to:
1. Understand follow-up questions and references (e.g., "that", "it", "the previous step")
2. Provide related information when relevant
3. Avoid repeating information already provided unless specifically asked
4. Build upon previous context for more coherent responses

"""
        
        system_prompt = base_prompt + history_context
        
        # Get AI response
        ai_result = self.query_ollama(system_prompt, user_query)
        
        # Return comprehensive results
        return {
            'success': ai_result['success'],
            'query': user_query,
            'complexity': query_complexity,
            'chunks_found': len(results['documents'][0]),
            'chunks_info': chunks_info,
            'retrieved_file_types': dict(retrieved_file_types),
            'retrieved_content_types': dict(retrieved_content_types),
            'retrieved_sources': list(retrieved_sources),
            'ai_response': ai_result.get('response', ''),
            'error': ai_result.get('error', None),
            'intent_analysis': intent_analysis
        }
    
    def get_conversation_suggestions(self, conversation_history):
        """Get contextual suggestions based on conversation history"""
        base_suggestions = self.get_query_suggestions()
        
        if not conversation_history:
            return base_suggestions
        
        # Add contextual follow-up suggestions based on last exchange
        last_query = conversation_history[-1][0].lower() if conversation_history else ""
        
        contextual_suggestions = []
        
        if "workflow" in last_query:
            contextual_suggestions.extend([
                "What are the steps to create a workflow?",
                "How do I modify an existing workflow?",
                "What types of workflows are supported?"
            ])
        
        if "contract" in last_query:
            contextual_suggestions.extend([
                "How do I create a new contract type?",
                "What are the access control options?",
                "How do I set default signatories?"
            ])
        
        # Mix base and contextual suggestions
        all_suggestions = contextual_suggestions + base_suggestions
        return all_suggestions[:8]  # Return top 8 suggestions