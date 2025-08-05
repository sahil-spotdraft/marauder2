"""
Simple Action Detection System
=============================

This module provides lightweight action detection that identifies action_ids
from user queries and returns them in a structured format.
"""

import json
import subprocess
import re
from typing import Dict, List, Optional, Tuple


class SimpleActionDetector:
    """
    Simple action detector that identifies action_ids from user queries
    """
    
    def __init__(self):
        self.actions = self._load_actions()
    
    def _load_actions(self) -> Dict:
        """Load available actions with their detection patterns"""
        return {
            "add_user_to_contract_type": {
                "name": "Add User to Contract Type",
                "description": "Add a user with specific roles to a contract type",
                "keywords": ["add", "user", "contract", "type", "assign", "role", "access", "permission"],
                "patterns": [
                    r"add.*user.*contract.*type",
                    r"assign.*user.*contract",
                    r"give.*user.*access.*contract",
                    r"user.*access.*contract.*type",
                    r"add.*someone.*contract",
                    r"how.*add.*user.*contract"
                ],
                "example_queries": [
                    "add user to contract type",
                    "how can I add user to contract type",
                    "assign user to contract",
                    "give user access to contract type"
                ]
            },
            "create_contract": {
                "name": "Create New Contract",
                "description": "Create a new contract from scratch or using templates",
                "keywords": ["create", "new", "contract", "make", "generate", "draft", "template"],
                "patterns": [
                    r"create.*new.*contract",
                    r"make.*contract",
                    r"generate.*contract",
                    r"draft.*contract",
                    r"new.*contract",
                    r"contract.*template"
                ],
                "example_queries": [
                    "create new contract",
                    "make a contract",
                    "how to create contract",
                    "generate contract from template"
                ]
            },
            "setup_workflow": {
                "name": "Setup Workflow",
                "description": "Configure and setup new workflows for contract processing",
                "keywords": ["setup", "workflow", "configure", "process", "approval", "create", "new"],
                "patterns": [
                    r"setup.*workflow",
                    r"create.*workflow",
                    r"configure.*workflow",
                    r"workflow.*setup",
                    r"new.*workflow",
                    r"approval.*workflow"
                ],
                "example_queries": [
                    "setup new workflow",
                    "create workflow",
                    "how to setup workflow",
                    "configure approval workflow"
                ]
            },
            "delete_contract": {
                "name": "Delete Contract",
                "description": "Delete or remove an existing contract",
                "keywords": ["delete", "remove", "contract", "cancel", "terminate"],
                "patterns": [
                    r"delete.*contract",
                    r"remove.*contract",
                    r"cancel.*contract",
                    r"terminate.*contract"
                ],
                "example_queries": [
                    "delete contract",
                    "remove contract",
                    "how to delete contract"
                ]
            },
            "manage_roles": {
                "name": "Manage User Roles",
                "description": "Manage user roles and permissions",
                "keywords": ["role", "permission", "manage", "user", "access", "rights"],
                "patterns": [
                    r"manage.*role",
                    r"user.*role",
                    r"permission",
                    r"access.*rights",
                    r"manage.*user.*access"
                ],
                "example_queries": [
                    "manage user roles",
                    "change user permissions",
                    "user access rights"
                ]
            }
        }
    
    def detect_action_with_ai(self, user_query: str) -> Optional[Tuple[str, float, str]]:
        """
        Use AI to detect the most appropriate action for the user query
        
        Args:
            user_query (str): The user's query
            
        Returns:
            Optional[Tuple[str, float, str]]: (action_id, confidence, reasoning) or None
        """
        
        # Prepare the AI prompt with available actions
        actions_context = self._format_actions_for_ai()
        
        ai_prompt = f"""You are an action detection system. Analyze the user query and determine which action_id best matches their intent.

AVAILABLE ACTIONS:
{actions_context}

USER QUERY: "{user_query}"

TASK: Determine which action_id best matches the user's intent. Consider:
1. Keywords and semantic meaning
2. User's goal and context
3. Action descriptions

RESPONSE FORMAT (JSON only):
{{
    "action_id": "most_appropriate_action_id_or_null",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this action was chosen"
}}

Rules:
- Only return action_ids that exist in the available actions
- Confidence should be 0.0 to 1.0 (1.0 = perfect match)
- If confidence < 0.7, set action_id to null
- Be precise - don't guess if unsure

Respond with JSON only:"""

        try:
            # Call Ollama AI for analysis
            result = self._query_ollama(ai_prompt)
            if result and 'action_id' in result:
                action_id = result.get('action_id')
                confidence = float(result.get('confidence', 0.0))
                reasoning = result.get('reasoning', '')
                
                # Validate the action exists and confidence is sufficient
                if action_id and action_id in self.actions and confidence >= 0.6:  # Lower threshold
                    return action_id, confidence, reasoning
                
        except Exception as e:
            print(f"AI detection error: {e}")
            
        return None
    
    def detect_action_with_patterns(self, user_query: str) -> Optional[str]:
        """
        Fallback method using pattern matching and keyword scoring
        """
        query_lower = user_query.lower()
        
        # Score each action based on patterns and keywords
        scores = {}
        
        for action_id, config in self.actions.items():
            score = 0
            
            # Check pattern matches
            for pattern in config["patterns"]:
                if re.search(pattern, query_lower, re.IGNORECASE):
                    score += 3  # High score for pattern matches
            
            # Check keyword matches
            for keyword in config["keywords"]:
                if keyword.lower() in query_lower:
                    score += 1
            
            # Check example query similarity
            for example in config["example_queries"]:
                if example.lower() in query_lower or query_lower in example.lower():
                    score += 2
            
            if score > 0:
                scores[action_id] = score
        
        # Return highest scoring action if it meets minimum threshold
        if scores:
            best_action = max(scores.keys(), key=lambda x: scores[x])
            if scores[best_action] >= 2:  # Minimum threshold
                return best_action
        
        return None
    
    def detect_action(self, user_query: str) -> Optional[Dict]:
        """
        Main method to detect action - tries AI first, then pattern matching
        
        Args:
            user_query (str): User's query
            
        Returns:
            Dict with action info or None
        """
        
        # Try AI detection first
        ai_result = self.detect_action_with_ai(user_query)
        if ai_result:
            action_id, confidence, reasoning = ai_result
            return {
                'action_id': action_id,
                'question_id': action_id,  # Initially same as action_id
                'confidence': confidence,
                'method': 'ai',
                'reasoning': reasoning,
                'action_info': self.actions[action_id]
            }
        
        # Fallback to pattern matching
        pattern_action = self.detect_action_with_patterns(user_query)
        if pattern_action:
            return {
                'action_id': pattern_action,
                'question_id': pattern_action,  # Initially same as action_id
                'confidence': 0.8,
                'method': 'pattern_match',
                'reasoning': 'Matched based on keywords and patterns',
                'action_info': self.actions[pattern_action]
            }
        
        return None
    
    def _format_actions_for_ai(self) -> str:
        """Format available actions for AI context"""
        formatted = ""
        for action_id, info in self.actions.items():
            formatted += f"""
ACTION_ID: {action_id}
NAME: {info['name']}
DESCRIPTION: {info['description']}
KEYWORDS: {', '.join(info['keywords'])}
EXAMPLES: {', '.join(info['example_queries'][:2])}
---
"""
        return formatted
    
    def _query_ollama(self, prompt: str) -> Optional[Dict]:
        """Query Ollama API for AI analysis"""
        try:
            data = {
                "model": "llama3.2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,
                    "num_predict": 150
                }
            }
            
            curl_command = [
                'curl', '-s', '-X', 'POST',
                'http://localhost:11434/api/generate',
                '-H', 'Content-Type: application/json',
                '-d', json.dumps(data)
            ]
            
            result = subprocess.run(curl_command, capture_output=True, text=True, timeout=20)
            
            if result.returncode == 0:
                response = json.loads(result.stdout)
                ai_response = response.get('response', '').strip()
                
                # Try to parse JSON from AI response
                try:
                    start_idx = ai_response.find('{')
                    end_idx = ai_response.rfind('}') + 1
                    if start_idx >= 0 and end_idx > start_idx:
                        json_str = ai_response[start_idx:end_idx]
                        return json.loads(json_str)
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            print(f"Ollama query error: {e}")
            
        return None
    
    def get_available_actions(self) -> List[Dict]:
        """Get list of all available actions"""
        actions = []
        for action_id, info in self.actions.items():
            actions.append({
                'action_id': action_id,
                'name': info['name'],
                'description': info['description'],
                'example_queries': info['example_queries'][:2]
            })
        return actions


# Global instance
detector = SimpleActionDetector()


def detect_action_from_query(user_query: str) -> Optional[Dict]:
    """
    Main function to detect action from user query
    
    Args:
        user_query (str): User's natural language query
        
    Returns:
        Dict with action_id, question_id, and other info or None
    """
    return detector.detect_action(user_query)


def get_all_actions() -> List[Dict]:
    """Get list of all available actions"""
    return detector.get_available_actions()


if __name__ == "__main__":
    # Test the detector
    test_queries = [
        "add user to contract type",
        "how can I add user to contract type",
        "create new contract", 
        "setup workflow",
        "delete contract",
        "manage user roles",
        "what is workflow manager"  # Should not detect
    ]
    
    print("🧪 Testing Simple Action Detector")
    print("=" * 50)
    
    for query in test_queries:
        result = detect_action_from_query(query)
        if result:
            print(f"✅ '{query}' → {result['action_id']} ({result['confidence']:.2f})")
        else:
            print(f"❌ '{query}' → No action detected")
    
    print(f"\n📋 Available Actions: {len(get_all_actions())}")
    for action in get_all_actions():
        print(f"   • {action['action_id']}: {action['name']}")