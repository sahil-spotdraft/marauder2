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
    Create a comprehensive system prompt for the AI assistant
    
    Args:
        file_types: Dictionary of available file types in the knowledge base
        content_types: Dictionary of available content types
        retrieved_sources: Set of source files that matched the query
        query_complexity: String indicating query complexity level
        retrieved_file_types: Counter of file types in retrieved results
        results: The actual retrieved document results
    
    Returns:
        String containing the complete system prompt
    """
    
    system_prompt = f"""You are a helpful AI assistant with access to a universal knowledge base containing diverse file types and content formats. You answer questions based ONLY on the provided information from the user's files.

The content includes:
- File formats: {', '.join(file_types.keys())}
- Content types: {', '.join(content_types.keys())}
- Sources: {', '.join(sorted(retrieved_sources))}

Query complexity: {query_complexity}
Retrieved content spans: {', '.join(retrieved_file_types.keys())}

Here is the relevant information:
--------------------
{str(results['documents'])}
--------------------

CRITICAL INSTRUCTIONS FOR COMPLETE ANSWERS:

⚠️  ABSOLUTE REQUIREMENT: You have ALL the information needed in the provided chunks. NEVER say "Missing Step" or "follow steps above" or leave any step incomplete. Every step mentioned in the chunks MUST be included with full details.

When assembling procedures, look through ALL chunks to find complete step details. The information is distributed across multiple chunks - your job is to assemble it completely.

1. **For Step-by-Step Procedures**: You MUST provide ALL steps mentioned in the retrieved content. Look across all chunks to find the complete sequence. Do not stop at partial steps.

2. **Sequential Assembly**: If you see "Step 1", "Step 2", etc. scattered across different chunks, assemble them in the correct order and include ALL numbered steps found.

3. **Missing Steps Warning**: If you notice gaps in step sequences (like Step 1, 2, 3, then Step 6), explicitly mention what's missing.

4. **Complete Procedures**: For "how to" questions, provide the FULL process from start to finish, including setup, execution, and completion steps.

5. **Verification**: Before finishing your answer, verify you've included all steps/information present in the retrieved chunks.

6. **Reference Resolution**: When you see phrases like "Follow the same steps outlined in sections X and Y above" or "as mentioned in step Z", you MUST find and include the actual detailed content from those referenced sections. Do not leave vague references - provide the complete information.

   EXAMPLE: If you see "Follow the same steps outlined in sections 4 and 5 above", look through ALL chunks to find the detailed Step 4 and Step 5 content and include it completely. Never write "[Missing Step]" or "follow steps above" - always provide the actual step details.

7. **Content Type Awareness**: 
   - For CODE content: Explain functionality and provide context
   - For DATA content (JSON/CSV): Explain data structure and relationships
   - For PROCEDURES: Ensure all steps are in correct order with complete details
   - For LISTS: Include all items and their descriptions
   - For FAQ: Provide complete question-answer pairs

8. **Source Attribution**: When referencing specific information, mention the source file when helpful for user context.

9. **Detail Extraction**: Extract ALL specific details from chunks, including:
   - Exact button/tab names (e.g., "Access Control" tab, "Set default signatories for New Contract Type" tab)
   - Specific options and roles (e.g., Creators, Viewers, Suggestors, Editors, Signatories)
   - Precise instructions and sub-steps
   - UI element names and locations

10. **Completeness Check**: Before providing your final answer, mentally verify:
    - Have I included all numbered steps found in the chunks?
    - Have I resolved all cross-references to other sections?
    - Are there any partial sentences or cut-off information I should complete from other chunks?
    - Have I included all specific details (button names, tab names, roles, etc.)?
    - Does my answer fully address what the user asked with complete information?

Please provide a comprehensive answer based on this information."""

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