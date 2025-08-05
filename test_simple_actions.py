#!/usr/bin/env python
"""
Test Script for Simple Action Detection System
==============================================

This script demonstrates the simplified action detection that returns
action_id, question_id, and response in the requested format.
"""

import requests
import json
import time

def test_action_detection_only(query):
    """Test the action detection API directly"""
    url = "http://localhost:8001/actions/test/"
    
    payload = {"query": query}
    
    try:
        response = requests.post(url, json=payload, timeout=20)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def test_full_chat_with_action_detection(query, user_email="demo@example.com"):
    """Test the main chat API with action detection"""
    url = "http://localhost:8001/api/"
    
    payload = {
        "user_query": query,
        "user_email": user_email,
        "use_db_history": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": str(e)}

def print_detection_result(query, result):
    """Pretty print detection results"""
    print(f"\n{'='*80}")
    print(f"🔍 QUERY: '{query}'")
    print(f"{'='*80}")
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    action_id = result.get('action_id')
    question_id = result.get('question_id')
    confidence = result.get('confidence', 0.0)
    
    if action_id:
        print(f"✅ ACTION DETECTED!")
        print(f"📝 Action ID: {action_id}")
        print(f"❓ Question ID: {question_id}")
        print(f"📊 Confidence: {confidence:.2%}")
        print(f"🔧 Method: {result.get('method', 'unknown')}")
        if result.get('reasoning'):
            print(f"💭 Reasoning: {result['reasoning']}")
        if result.get('action_info'):
            info = result['action_info']
            print(f"📋 Action: {info.get('name', 'Unknown')}")
            print(f"📄 Description: {info.get('description', 'No description')}")
    else:
        print(f"❌ NO ACTION DETECTED")
        print(f"📊 Confidence: {confidence:.2%}")

def print_chat_result(query, result):
    """Pretty print chat results with action info"""
    print(f"\n{'='*80}")
    print(f"💬 CHAT: '{query}'")
    print(f"{'='*80}")
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        return
    
    if not result.get('success'):
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        return
    
    # Check if action was detected
    if result.get('action_detected'):
        print(f"🎯 ACTION DETECTED IN CHAT!")
        print(f"📝 Action ID: {result.get('action_id')}")
        print(f"❓ Question ID: {result.get('question_id')}")
        print(f"📊 Confidence: {result.get('action_confidence', 0):.2%}")
        print(f"🔧 Method: {result.get('action_method', 'unknown')}")
        if result.get('action_reasoning'):
            print(f"💭 Reasoning: {result['action_reasoning']}")
        if result.get('action_info'):
            info = result['action_info']
            print(f"📋 Action: {info.get('name', 'Unknown')}")
        print(f"{'─'*80}")
    
    # Show response
    response_text = result.get('response', '')
    if response_text:
        print(f"🤖 RESPONSE:")
        print(response_text[:300] + "..." if len(response_text) > 300 else response_text)
    
    # Show additional info
    if result.get('complexity'):
        print(f"📊 Complexity: {result['complexity']}")
    if result.get('chunks_found'):
        print(f"📦 Chunks: {result['chunks_found']}")

def test_user_requested_format():
    """Test the specific format requested by the user"""
    print("🎯 Testing User-Requested Response Format")
    print("=" * 70)
    
    test_queries = [
        "add user to contract type",
        "how can I add user to contract type",
        "create new contract",
        "setup workflow",
        "what is workflow manager?"  # Should not detect action
    ]
    
    for query in test_queries:
        print(f"\n🔍 Testing: '{query}'")
        
        # Test full chat API to get the requested format
        result = test_full_chat_with_action_detection(query)
        
        if result.get('success') and result.get('action_detected'):
            # Extract in user's requested format
            user_format = {
                "action_id": result.get('action_id'),
                "question_id": result.get('question_id'),
                "response": result.get('response', '')
            }
            
            print("✅ USER REQUESTED FORMAT:")
            print(json.dumps(user_format, indent=2))
        elif result.get('success'):
            print("💬 Regular response (no action detected)")
            response = result.get('response', '')
            print(f"Response: {response[:150]}...")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        time.sleep(1)

def test_detection_accuracy():
    """Test detection accuracy with various queries"""
    print("\n🧪 Testing Detection Accuracy")
    print("=" * 50)
    
    test_cases = [
        # Should detect actions
        ("add user to contract type", "add_user_to_contract_type"),
        ("I want to assign someone to a contract", "add_user_to_contract_type"),
        ("create new contract", "create_contract"),
        ("make a contract", "create_contract"),
        ("setup workflow", "setup_workflow"),
        ("delete contract", "delete_contract"),
        ("manage user roles", "manage_roles"),
        
        # Should NOT detect actions
        ("what is a contract?", None),
        ("how do workflows work?", None),
        ("explain contract types", None),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for query, expected_action in test_cases:
        result = test_action_detection_only(query)
        detected_action = result.get('action_id')
        
        is_correct = detected_action == expected_action
        status = "✅" if is_correct else "❌"
        
        print(f"{status} '{query}'")
        print(f"   Expected: {expected_action or 'None'}")
        print(f"   Detected: {detected_action or 'None'}")
        
        if is_correct:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\n📊 ACCURACY: {correct}/{total} ({accuracy:.1f}%)")

def interactive_demo():
    """Interactive demo for testing"""
    print("🚀 Interactive Simple Action Detection Demo")
    print("=" * 60)
    print("Try queries like:")
    print("• 'add user to contract type'")
    print("• 'create new contract'")
    print("• 'setup workflow'")
    print("• 'delete contract'")
    print("• 'manage user roles'")
    print("\nType 'quit' to exit")
    print("=" * 60)
    
    while True:
        query = input(f"\n💭 Your query: ").strip()
        
        if query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if not query:
            continue
        
        print("⏳ Processing...")
        
        # Test both detection and full chat
        print("\n1️⃣ DETECTION ONLY:")
        detection_result = test_action_detection_only(query)
        print_detection_result(query, detection_result)
        
        print("\n2️⃣ FULL CHAT WITH ACTION:")
        chat_result = test_full_chat_with_action_detection(query)
        print_chat_result(query, chat_result)

if __name__ == "__main__":
    import sys
    
    print("🤖 Simple Action Detection Test Suite")
    print("=" * 60)
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "format":
            test_user_requested_format()
        elif mode == "accuracy":
            test_detection_accuracy()
        elif mode == "interactive":
            interactive_demo()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python test_simple_actions.py [format|accuracy|interactive]")
    else:
        print("Choose a mode:")
        print("1. format - Test user-requested response format")
        print("2. accuracy - Test detection accuracy") 
        print("3. interactive - Interactive demo")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            test_user_requested_format()
        elif choice == "2":
            test_detection_accuracy()
        elif choice == "3":
            interactive_demo()
        else:
            print("Invalid choice!")