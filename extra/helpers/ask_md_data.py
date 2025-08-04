import chromadb
import requests
import json
import os

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "data_from_md_files"  # Match the collection name from fill_db_from_md_files.py

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

print("📄 Markdown Knowledge Base Q&A System")
print("=" * 50)

# Get the markdown-based collection
try:
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    
    # Get some stats about the collection
    all_data = collection.get()
    total_chunks = len(all_data['ids'])
    
    # Count unique files
    unique_files = set()
    for meta in all_data['metadatas']:
        if meta and 'source' in meta:
            unique_files.add(meta['source'])
    
    print(f"✅ Connected to collection: {COLLECTION_NAME}")
    print(f"📊 Database contains {total_chunks} chunks from {len(unique_files)} markdown files")
    
    if unique_files:
        print("📁 Available files:")
        for i, filename in enumerate(sorted(unique_files), 1):
            print(f"  {i}. {filename}")
    print()
    
except Exception as e:
    print(f"❌ Error: Could not find collection '{COLLECTION_NAME}'")
    print("Make sure you've run 'python fill_db_from_md_files.py' first!")
    print("Or check that your markdown files are in the 'md_data' directory.")
    exit(1)

user_query = input("What would you like to know from your markdown files?\n\n")

# Query the collection
print("🔍 Searching through your markdown files...")
results = collection.query(
    query_texts=[user_query],
    n_results=4
)

if not results['documents'][0]:
    print("❌ No relevant information found in your markdown files.")
    print("Try rephrasing your question or add more content to your markdown files.")
    exit(1)

print(f"\n📄 Found {len(results['documents'][0])} relevant chunks:")
print("="*70)

for i, doc in enumerate(results['documents'][0], 1):
    # Get metadata for this chunk
    meta = results['metadatas'][0][i-1] if results['metadatas'][0] else {}
    source = meta.get('source', 'Unknown file')
    title = meta.get('title', 'No title')
    
    print(f"\n📋 Chunk {i}")
    print(f"📁 File: {source}")
    print(f"📝 Title: {title}")
    print("-" * 50)
    
    # Show preview of chunk
    preview = doc[:250] + "..." if len(doc) > 250 else doc
    print(preview)

# Create system prompt with retrieved documents
system_prompt = f"""You are a helpful AI assistant. You answer questions based ONLY on the provided information from markdown files. 
You don't use your internal knowledge and you don't make things up.
If you don't know the answer based on the provided information, just say: "I don't have enough information to answer that question based on the provided markdown files."

The information comes from these markdown files:
{', '.join(sorted(unique_files))}

Here is the relevant information from the markdown files:
--------------------
{str(results['documents'])}
--------------------

Please provide a helpful answer based on this information. If you reference specific information, you can mention which file it came from."""

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
        return "Error: Could not connect to Ollama. Make sure Ollama is running.\n\nYou can start it with: ollama serve"
    except Exception as e:
        return f"Error: {str(e)}"

print("\n" + "="*70)
print("🤖 AI ASSISTANT RESPONSE:")
print("="*70)

response = query_ollama(system_prompt, user_query)
print(f"\n{response}")

print(f"\n" + "="*70)
print("💡 This response is based on content from your markdown files:")
for filename in sorted(unique_files):
    print(f"   📄 {filename}")
print("="*70)

# Optional: Show which files were most relevant
print(f"\n🎯 Most relevant files for your query:")
file_relevance = {}
for i, meta in enumerate(results['metadatas'][0]):
    if meta and 'source' in meta:
        filename = meta['source']
        file_relevance[filename] = file_relevance.get(filename, 0) + 1

for filename, count in sorted(file_relevance.items(), key=lambda x: x[1], reverse=True):
    print(f"   📊 {filename}: {count} relevant chunks")