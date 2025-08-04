import chromadb
import requests
import json
import os
from collections import Counter
from ai_prompts import (
    determine_query_complexity, 
    create_enhanced_system_prompt, 
    get_query_suggestions,
    analyze_query_intent,
    get_prompt_for_intent
)

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "universal_content"

# Debug flag - set to True to see detailed processing information
DEBUG_CONFIG = {'enabled': False}

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

print("🌍 Universal Content Q&A System")
print("=" * 60)
print("Query across all your files: Text, PDF, Word, JSON, CSV, Code & more!")
print()

# Get the universal collection
try:
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    
    # Get comprehensive collection statistics
    all_data = collection.get()
    total_chunks = len(all_data['ids'])
    
    if total_chunks == 0:
        print("❌ No content found in the database!")
        print("Run 'python fill_db.py' first to add content.")
        exit(1)
    
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
    
    print(f"✅ Connected to universal knowledge base")
    print(f"📊 Database contains {total_chunks} chunks from {len(file_sources)} files")
    
    if DEBUG_CONFIG['enabled']:
        print(f"📁 From {len(file_sources)} files across {len(file_extensions)} file types")
        
        if file_types:
            print(f"\n🗂️  File formats in your knowledge base:")
            for ftype, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_chunks) * 100
                print(f"   • {ftype.upper()}: {count} chunks ({percentage:.1f}%)")
        
        if content_types:
            print(f"\n🎯 Content types detected:")
            for ctype, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_chunks) * 100
                print(f"   • {ctype}: {count} chunks ({percentage:.1f}%)")
        
        if file_extensions:
            print(f"\n📄 File extensions: {', '.join(sorted(file_extensions))}")
        
        if len(file_sources) <= 10:
            print(f"\n📚 Available files:")
            for i, filename in enumerate(sorted(file_sources), 1):
                print(f"   {i}. {filename}")
        else:
            print(f"\n📚 Sample files (showing 10 of {len(file_sources)}):")
            for i, filename in enumerate(sorted(list(file_sources)[:10]), 1):
                print(f"   {i}. {filename}")
            print(f"   ... and {len(file_sources) - 10} more files")
    
    print()
    
except Exception as e:
    print(f"❌ Error: Could not find collection '{COLLECTION_NAME}'")
    print("Make sure you've run 'python fill_db.py' first!")
    print(f"Error details: {str(e)}")
    exit(1)





# Initialize conversation history
conversation_history = []

# Get user query with suggestions
suggestions = get_query_suggestions(file_types, content_types)

def show_help():
    """Display help information for chat commands"""
    print("\n💡 Chat Commands:")
    print("   • Type your question normally")
    print("   • 'help' - Show this help")
    print("   • 'history' - Show conversation history")
    print("   • 'clear' - Clear conversation history")
    print("   • 'suggestions' - Show query suggestions")
    print("   • 'stats' - Show knowledge base statistics")
    print("   • 'debug on' - Enable detailed processing information")
    print("   • 'debug off' - Disable detailed processing information")
    print("   • 'exit' or 'quit' - End the conversation")
    print(f"\n🔧 Debug mode is currently: {'ON' if DEBUG_CONFIG['enabled'] else 'OFF'}")
    print()

def show_conversation_history():
    """Display the conversation history"""
    if not conversation_history:
        print("📝 No conversation history yet.")
        return
    
    print(f"\n📝 Conversation History ({len(conversation_history)} exchanges):")
    print("=" * 60)
    for i, (q, a_preview) in enumerate(conversation_history, 1):
        print(f"\n💭 Q{i}: {q}")
        # Show first 100 chars of answer
        preview = a_preview[:100] + "..." if len(a_preview) > 100 else a_preview
        print(f"🤖 A{i}: {preview}")
    print("=" * 60)

def show_suggestions():
    """Show query suggestions"""
    if suggestions:
        print("\n💡 Query suggestions based on your content:")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"   {i}. {suggestion}")
    else:
        print("\n💡 No specific suggestions available. Try asking about your content!")

def show_stats():
    """Show knowledge base statistics"""
    print(f"\n📊 Knowledge Base Statistics:")
    print(f"   📄 Total chunks: {total_chunks}")
    print(f"   📁 Files: {len(file_sources)}")
    print(f"   🗂️  File types: {len(file_types)}")
    print(f"   🎯 Content types: {len(content_types)}")
    
    if file_types:
        print(f"\n🗂️  File formats:")
        for ftype, count in sorted(file_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_chunks) * 100
            print(f"   • {ftype.upper()}: {count} chunks ({percentage:.1f}%)")
    
    if content_types:
        print(f"\n🎯 Content types:")
        for ctype, count in sorted(content_types.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_chunks) * 100
            print(f"   • {ctype}: {count} chunks ({percentage:.1f}%)")

# Show initial suggestions in debug mode
if DEBUG_CONFIG['enabled'] and suggestions:
    print("\n💡 Query suggestions based on your content:")
    for i, suggestion in enumerate(suggestions, 1):
        print(f"   {i}. {suggestion}")

print("\n💬 Starting continuous chat mode...")
print("🔗 Your questions will build on previous context for better answers!")
print("💡 Type 'help' for commands, 'debug on/off' to toggle details, or 'exit' to quit")
print("=" * 60)

# Use Ollama local API
def query_ollama(prompt, user_question):
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.2",
        "prompt": f"{prompt}\n\nUser Question: {user_question}\n\nAssistant:",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running.\n\nStart with: ollama serve"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The model might be processing a complex response."
    except Exception as e:
        return f"Error: {str(e)}"

# Continuous chat loop  
while True:
    # Get user input
    try:
        user_query = input(f"\n💭 You [{len(conversation_history) + 1}]: ").strip()
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Thanks for using the Universal RAG System! Goodbye!")
        break
    
    # Handle empty input
    if not user_query:
        continue
    
    # Handle special commands
    if user_query.lower() in ['exit', 'quit', 'bye']:
        print("\n👋 Thanks for using the Universal RAG System! Goodbye!")
        break
    elif user_query.lower() == 'help':
        show_help()
        continue
    elif user_query.lower() == 'history':
        show_conversation_history()
        continue
    elif user_query.lower() == 'clear':
        conversation_history.clear()
        print("🗑️  Conversation history cleared!")
        continue
    elif user_query.lower() == 'suggestions':
        show_suggestions()
        continue
    elif user_query.lower() == 'stats':
        show_stats()
        continue
    elif user_query.lower() in ['debug on', 'debug']:
        DEBUG_CONFIG['enabled'] = True
        print("🔧 Debug mode enabled - showing detailed processing information")
        continue
    elif user_query.lower() == 'debug off':
        DEBUG_CONFIG['enabled'] = False
        print("🔇 Debug mode disabled - showing only essential information")
        continue

    # Intelligent retrieval based on query type
    query_complexity, suggested_n_results = determine_query_complexity(user_query)

    if DEBUG_CONFIG['enabled']:
        print(f"🔍 Query complexity: {query_complexity}")
        print(f"🔍 Searching through your universal knowledge base...")

    # Query the collection with adaptive result count
    results = collection.query(
        query_texts=[user_query],
        n_results=suggested_n_results
    )

    if not results['documents'][0]:
        print("❌ No relevant information found.")
        print("Try rephrasing your question or check that your query matches your content.")
        continue

    if DEBUG_CONFIG['enabled']:
        print(f"\n📄 Found {len(results['documents'][0])} relevant chunks:")
        print("="*80)

    # Collect metadata for prompt context (always needed)
    retrieved_file_types = Counter()
    retrieved_content_types = Counter()
    retrieved_sources = set()

    for i, doc in enumerate(results['documents'][0], 1):
        meta = results['metadatas'][0][i-1] if results['metadatas'][0] else {}
        
        source = meta.get('source', 'Unknown file')
        title = meta.get('title', 'No title')
        file_type = meta.get('file_type', 'unknown')
        content_type = meta.get('content_type', 'unknown')
        strategy = meta.get('chunking_strategy', 'unknown')
        chunk_size = meta.get('actual_chunk_size', len(doc))
        
        # Track what was retrieved (needed for AI prompt)
        retrieved_file_types[file_type] += 1
        retrieved_content_types[content_type] += 1
        retrieved_sources.add(source)
        
        # Show detailed chunk information only in debug mode
        if DEBUG_CONFIG['enabled']:
            print(f"\n📋 Chunk {i}")
            print(f"📁 File: {source}")
            print(f"📝 Title: {title[:80]}{'...' if len(title) > 80 else ''}")
            print(f"🎯 Type: {content_type} | Format: {file_type.upper()} | Strategy: {strategy} | Size: {chunk_size} chars")
            print("-" * 80)
            
            # Show preview with length based on content type
            if content_type == 'code':
                preview_length = 300  # More code context
            elif content_type == 'data':
                preview_length = 250  # Data can be compact
            else:
                preview_length = 400  # Standard preview
            
            preview = doc[:preview_length] + "..." if len(doc) > preview_length else doc
            print(preview)

    # Create enhanced system prompt with intent analysis and conversation history
    intent_analysis = analyze_query_intent(user_query)
    base_prompt = create_enhanced_system_prompt(
        file_types, content_types, retrieved_sources, 
        query_complexity, retrieved_file_types, results
    )
    intent_prompt = get_prompt_for_intent(intent_analysis)
    
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
    
    system_prompt = base_prompt + "\n\n" + intent_prompt + history_context

    # Generate AI response
    print("\n" + "="*80)
    print(f"\033[92m🤖 AI [{len(conversation_history) + 1}]:\033[0m")
    print("="*80)

    response = query_ollama(system_prompt, user_query)
    print(f"\n{response}")
    
    # Store conversation in history
    conversation_history.append((user_query, response))
    
    # Show conversation context hint in debug mode
    if DEBUG_CONFIG['enabled'] and len(conversation_history) > 1:
        print(f"\n💭 This response builds on {len(conversation_history) - 1} previous exchange(s)")
        print("💡 Ask follow-up questions - I remember our conversation!")

# End of continuous chat mode