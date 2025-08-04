import chromadb
import requests
import json
import os

# setting the environment
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Get existing collection (should already be created by fill_db.py)
collection = chroma_client.get_collection(name="growing_vegetables")

user_query = input("What do you want to know about growing vegetables?\n\n")

results = collection.query(
    query_texts=[user_query],
    n_results=4
)

print(results['documents'])

# Create system prompt with retrieved documents
system_prompt = """You are a helpful assistant. You answer questions about growing vegetables in Florida. 
But you only answer based on knowledge I'm providing you. You don't use your internal 
knowledge and you don't make things up.
If you don't know the answer, just say: I don't know
--------------------
The data:
""" + str(results['documents']) + """
"""

# Use Ollama local API (completely free!)
def query_ollama(prompt, user_question):
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.2",
        "prompt": f"{prompt}\n\nUser: {user_question}\nAssistant:",
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

print("\n\n---------------------")
print("🌱 ASKING THE FREE AI MODEL...")
print("---------------------\n\n")

response = query_ollama(system_prompt, user_query)
print(response)