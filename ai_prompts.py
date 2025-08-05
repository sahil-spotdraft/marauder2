"""
AI Prompts and Query Analysis for Universal RAG System
=====================================================

This module contains all prompt engineering and query analysis logic
for the universal content retrieval and generation system.
"""

def create_in_app_assistant_prompt(file_types, content_types, retrieved_sources, 
                                 query_complexity, retrieved_file_types, results, user_query):
    """
    Create an in-app assistant system prompt with structured response format
    
    Args:
        file_types (dict): Available file types in knowledge base
        content_types (dict): Available content types in knowledge base
        retrieved_sources (set): Source files that contributed to this query
        query_complexity (str): Query complexity level
        retrieved_file_types (dict): File types in retrieved results
        results (dict): ChromaDB query results
        
    Returns:
        str: In-app assistant system prompt with structured format
    """
    
    context_docs = ""
    if results and results['documents'] and results['documents'][0]:
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i] if results['metadatas'][0] else {}
            source = metadata.get('source', 'Unknown')
            title = metadata.get('title', 'No title')
            
            context_docs += f"\n--- Document {i+1} (Source: {source}) ---\n"
            context_docs += f"Title: {title}\n"
            context_docs += f"Content: {doc}\n"
    
    sources_list = ', '.join(retrieved_sources) if retrieved_sources else "various sources"
    
    prompt = f"""You are an AI-powered in-app assistant helping users navigate application workflows and processes.

Your role is to respond to user questions when they are stuck in a workflow or need guidance. For each query, you have access to relevant documentation and should provide structured, actionable guidance.

CRITICAL RESPONSE FORMAT - You MUST respond in this exact structure:

**Summary:** [Brief description of what the user is trying to accomplish]

**Next Steps:**
[Provide ALL necessary steps in sequence - don't limit to just 3 steps. Include every actionable step needed to complete the task or resolve the issue]
1. [First actionable step with specific details - include actual button names, menu locations, or specific actions]
2. [Second actionable step with specific details - be precise about where to click or what to do]
3. [Third actionable step with specific details]
4. [Continue with as many steps as needed to complete the process]
5. [Include all intermediate steps - don't skip any part of the workflow]
[...continue numbering until the complete process is covered]

**Key Information:**
- [Important details, warnings, or context the user should know]
- [Any prerequisites or requirements]
- [Definitions of key terms if the user is asking "what is X"]

**Related Resources:**
- [Mention specific sections, features, or related topics by their exact names]
- [Any follow-up actions they might need]

CONTENT GUIDELINES:
✅ Base your answer strictly on the retrieved context below
✅ Use specific terminology from the documentation (exact feature names, button labels, section titles)
✅ Include actual names of features, buttons, sections, or processes mentioned in the documentation
✅ Provide ALL necessary steps in the Next Steps section - don't limit yourself to 3 steps
✅ Include every intermediate step needed to complete the process or task
✅ Number steps sequentially until the entire workflow is covered
✅ Provide 1-10+ concrete, immediately actionable next steps as needed for completeness
✅ When referencing other sections, ALWAYS resolve those references and include the actual steps inline
✅ For "what is" questions, provide clear definitions and explanations from the documentation
✅ Be specific about locations (e.g., "Click the 'Create Workflow' button in the top-right corner")

❌ Do not make up information not found in the context
❌ Do not use generic placeholder text or vague instructions
❌ Do not skip the required format structure
❌ Do not say "follow steps in section X" or "refer to document Y" without providing the actual content
❌ Do not reference document numbers or sources in your response - integrate the information naturally
❌ Do not leave steps incomplete or unclear

SPECIAL INSTRUCTIONS FOR DIFFERENT QUERY TYPES:

For "What is..." questions:
- Provide clear definition in Key Information section
- Include practical context about how it's used
- Give specific next steps to explore or use the feature

For troubleshooting questions:
- Focus on immediate solutions the user can try
- Include specific error messages or symptoms to look for
- Provide fallback options if the first solution doesn't work

For process/workflow questions:
- Break down complex processes into simple, sequential steps
- Include where to find each feature or option
- Mention any permissions or prerequisites needed

CONTEXT INFORMATION:
- Query Complexity: {query_complexity}
- Retrieved from: {sources_list}
- Content includes: {', '.join(retrieved_file_types.keys()) if retrieved_file_types else 'various content types'}

RETRIEVED DOCUMENTATION:
{context_docs}

USER QUERY: {user_query}

Remember: Your response should be immediately actionable and specific. Avoid referencing document numbers or sources directly - instead, seamlessly integrate the information to help the user move forward in their workflow."""

    return prompt

def determine_query_complexity(query):
    """Analyze query to determine how many results to retrieve"""
    query_lower = query.lower()
    
    # Complex query indicators
    complex_indicators = [
        'steps', 'how to', 'procedure', 'process', 'guide', 'tutorial',
        'explain', 'describe', 'what are all', 'types of', 'list all',
        'compare', 'difference', 'versus', 'vs', 'analyze', 'breakdown',
        'comprehensive', 'detailed', 'complete', 'full'
    ]
    
    # Simple query indicators  
    simple_indicators = [
        'what is', 'define', 'meaning', 'who is', 'when', 'where',
        'true or false', 'yes or no', 'which', 'name'
    ]
    
    # Technical query indicators
    technical_indicators = [
        'function', 'method', 'class', 'api', 'code', 'syntax',
        'error', 'debug', 'implement', 'algorithm'
    ]
    
    complex_score = sum(1 for indicator in complex_indicators if indicator in query_lower)
    simple_score = sum(1 for indicator in simple_indicators if indicator in query_lower)
    technical_score = sum(1 for indicator in technical_indicators if indicator in query_lower)
    
    if technical_score > 0:
        return "technical", 8  # Technical queries need good context
    elif complex_score > simple_score:
        return "complex", 10   # More results for complex queries to ensure complete procedures
    elif simple_score > complex_score:
        return "simple", 4     # Fewer results for simple queries
    else:
        return "medium", 6     # Balanced approach

def create_enhanced_system_prompt(file_types, content_types, retrieved_sources, 
                                query_complexity, retrieved_file_types, results):
    """
    Create a simple system prompt for the AI assistant to just give a summary and all steps from the context.
    """
    system_prompt = f"""You are an AI assistant. Using only the information below, provide:
- A brief summary of the context.
- All step-by-step instructions or procedures found in the context, in order, with no extra commentary.
- Relevant links to the context if present other wise don't include a Relevant Links section".

Context:
--------------------
{str(results['documents'])}
--------------------

Only include the summary, the relevant links at the end, and the complete steps as found in the context. Do not add extra explanations or formatting. Do not reference document numbers or sources. Do not speculate or add missing steps. Just present the summary and all steps as they appear.
"""
    return system_prompt
def create_specialized_prompts():
    """
    Create specialized prompts for different types of content and queries
    Returns a dictionary of prompt templates for specific use cases
    """
    
    prompts = {
        'code_analysis': """
You are analyzing code content. Focus on:
- Function/method purposes and parameters
- Code flow and logic
- Dependencies and imports
- Error handling and edge cases
- Usage examples where available
        """,
        
        'data_analysis': """
You are analyzing structured data (JSON, CSV, etc.). Focus on:
- Data schema and structure
- Key fields and their meanings
- Relationships between data elements
- Data types and constraints
- Sample values and patterns
        """,
        
        'procedure_analysis': """
You are analyzing step-by-step procedures. Focus on:
- Complete sequential steps
- Prerequisites and setup requirements
- Expected outcomes for each step
- Important notes and warnings
- Alternative paths or options
        """,
        
        'troubleshooting': """
You are helping with troubleshooting. Focus on:
- Problem identification
- Diagnostic steps
- Common causes and solutions
- Prevention measures
- When to escalate or seek additional help
        """
    }
    
    return prompts

def get_query_suggestions(file_types, content_types):
    """Provide intelligent query suggestions based on available content"""
    
    suggestions = []
    
    # Suggestions based on content types
    if 'procedures' in content_types:
        suggestions.extend([
            "What are the steps to...",
            "How do I set up...",
            "What is the procedure for..."
        ])
    
    if 'lists' in content_types:
        suggestions.extend([
            "What types of... are available?",
            "List all the options for...",
            "What are the different..."
        ])
    
    if 'technical' in content_types or 'code' in content_types:
        suggestions.extend([
            "How does the ... function work?",
            "What is the syntax for...",
            "Explain the code that..."
        ])
    
    if 'faq' in content_types:
        suggestions.extend([
            "What is...",
            "How can I...",
            "Why does..."
        ])
    
    # Suggestions based on file types  
    if 'json' in file_types:
        suggestions.append("What data is stored in the JSON files?")
    
    if 'csv' in file_types:
        suggestions.append("What columns are in the CSV data?")
    
    if 'pdf' in file_types:
        suggestions.append("What information is in the PDF documents?")
        
    if 'code' in file_types:
        suggestions.extend([
            "What functions are available in the code?",
            "How do I use the API?",
            "What are the main classes and methods?"
        ])
    
    return suggestions[:8]  # Return top 8 suggestions

def analyze_query_intent(query):
    """
    Analyze the user's query to understand intent and optimize retrieval
    
    Returns:
        dict: Contains intent classification and optimization hints
    """
    query_lower = query.lower()
    
    intent_analysis = {
        'primary_intent': 'general',
        'requires_sequence': False,
        'requires_complete_data': False,
        'is_comparative': False,
        'is_troubleshooting': False,
        'expected_answer_length': 'medium'
    }
    
    # Detect if query requires sequential information
    sequence_indicators = ['steps', 'how to', 'procedure', 'process', 'guide', 'tutorial', 'first', 'then', 'next', 'finally']
    if any(indicator in query_lower for indicator in sequence_indicators):
        intent_analysis['requires_sequence'] = True
        intent_analysis['primary_intent'] = 'procedure'
        intent_analysis['expected_answer_length'] = 'long'
    
    # Detect if query requires complete data listing
    listing_indicators = ['list all', 'what are all', 'types of', 'all the', 'every', 'complete list']
    if any(indicator in query_lower for indicator in listing_indicators):
        intent_analysis['requires_complete_data'] = True
        intent_analysis['primary_intent'] = 'comprehensive_list'
        intent_analysis['expected_answer_length'] = 'long'
    
    # Detect comparative queries
    comparative_indicators = ['compare', 'difference', 'versus', 'vs', 'better', 'best', 'worst', 'pros and cons']
    if any(indicator in query_lower for indicator in comparative_indicators):
        intent_analysis['is_comparative'] = True
        intent_analysis['primary_intent'] = 'comparison'
        intent_analysis['expected_answer_length'] = 'long'
    
    # Detect troubleshooting queries
    trouble_indicators = ['error', 'problem', 'issue', 'not working', 'fails', 'broken', 'fix', 'solve', 'troubleshoot']
    if any(indicator in query_lower for indicator in trouble_indicators):
        intent_analysis['is_troubleshooting'] = True
        intent_analysis['primary_intent'] = 'troubleshooting'
        intent_analysis['expected_answer_length'] = 'long'
    
    # Simple definition queries
    simple_indicators = ['what is', 'define', 'meaning of', 'who is', 'when is', 'where is']
    if any(indicator in query_lower for indicator in simple_indicators):
        intent_analysis['primary_intent'] = 'definition'
        intent_analysis['expected_answer_length'] = 'short'
    
    return intent_analysis

def get_prompt_for_intent(intent_analysis):
    """
    Get specialized prompt additions based on query intent analysis
    
    Args:
        intent_analysis: Dictionary from analyze_query_intent()
    
    Returns:
        String with additional prompt instructions
    """
    
    intent_prompts = {
        'procedure': """
SPECIAL FOCUS FOR PROCEDURAL QUERIES:

MANDATORY: All step information is present in the retrieved chunks. Your task is to assemble it completely.

- Ensure ALL steps are included in sequential order with complete details
- Include any prerequisites or setup requirements  
- Mention expected outcomes or verification steps
- Include warnings or important notes
- ABSOLUTE REQUIREMENT: When you encounter "Follow the same steps outlined in sections X and Y above", you MUST search through ALL chunks to find those specific steps and include them with complete details. Never leave placeholder text.
- Extract exact UI element names: button names, tab names, field names, menu options
- Include specific role names, options, and selections mentioned
- NEVER write "[Missing Step]" or "follow steps above" - the information is in the chunks
- Every numbered step (Step 1, Step 2, Step 3, etc.) that appears in ANY chunk must be included in your final answer with full details

DEBUGGING: If you think information is missing, look again through ALL chunks - it's there.
        """,
        
        'comprehensive_list': """
SPECIAL FOCUS FOR COMPREHENSIVE LISTS:
- Include ALL items mentioned across all chunks
- Group related items logically
- Provide brief descriptions for each item when available
- Mention if the list appears to be complete or partial
        """,
        
        'comparison': """
SPECIAL FOCUS FOR COMPARATIVE QUERIES:
- Present information in a structured comparison format
- Highlight key differences and similarities
- Include pros/cons when mentioned in the source material
- Be objective and base comparisons only on provided information
        """,
        
        'troubleshooting': """
SPECIAL FOCUS FOR TROUBLESHOOTING:
- List potential causes mentioned in the source material
- Provide step-by-step diagnostic or solution steps
- Include prevention tips if mentioned
- Suggest when to seek additional help if indicated
        """,
        
        'definition': """
SPECIAL FOCUS FOR DEFINITIONS:
- Provide clear, concise definitions
- Include context and usage examples when available
- Mention related concepts if they appear in the source material
        """
    }
    
    return intent_prompts.get(intent_analysis['primary_intent'], "")

# Constants for easy configuration
DEFAULT_RETRIEVAL_COUNTS = {
    'simple': 4,
    'medium': 6,
    'complex': 10,
    'technical': 8
}

QUERY_COMPLEXITY_THRESHOLDS = {
    'technical_weight': 1.0,
    'complex_weight': 1.0,
    'simple_weight': 1.0
}
