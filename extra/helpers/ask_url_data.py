import chromadb
import requests
import json
import os

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "data_from_urls"  # Match the collection name from fill_db_from_urls.py

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Get the URL-based collection
try:
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    print(f"✅ Connected to collection: {COLLECTION_NAME}")
except Exception as e:
    print(f"❌ Error: Could not find collection '{COLLECTION_NAME}'")
    print("Make sure you've run 'python fill_db_from_urls.py' first!")
    exit(1)

user_query = input("What would you like to know from the web content?\n\n")

# Query the collection
results = collection.query(
    query_texts=[user_query],
    n_results=4
)

print(f"\n📄 Found {len(results['documents'][0])} relevant chunks:")
print("="*60)
for i, doc in enumerate(results['documents'][0], 1):
    source = results['metadatas'][0][i-1].get('source', 'Unknown')
    print(f"\n📋 Chunk {i} (from: {source}):")
    print("-" * 40)
    print(doc[:200] + "..." if len(doc) > 200 else doc)

# Create system prompt with retrieved documents
system_prompt = f"""You are a helpful AI assistant. You answer questions based ONLY on the provided information from web content. 
You don't use your internal knowledge and you don't make things up.
If you don't know the answer based on the provided information, just say: "I don't have enough information to answer that question."

Here is the information from the web sources:
--------------------
{str(results['documents'])}
--------------------

Please provide a helpful answer based on this information."""

# Use Ollama local API (completely free!)
def query_ollama(prompt, user_question):
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.2",
        "prompt": f"{prompt}\n\nUser Question: {user_question}\n\nAssistant:",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running with 'ollama serve'"
    except Exception as e:
        return f"Error: {str(e)}"

print("\n" + "="*60)
print("\033[92m🤖 AI ASSISTANT RESPONSE:\033[0m")
print("="*60)

response = query_ollama(system_prompt, user_query)
print(f"\n{response}")

print(f"\n" + "="*60)
print("💡 TIP: This response is based on content from your web sources!")
print("="*60)