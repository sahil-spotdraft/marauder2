import chromadb
import requests
import json
import os

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "data_from_txt_files"  # Match the collection name from fill_db_from_txt_files.py

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

print("📄 Text Files Knowledge Base Q&A System")
print("=" * 55)

# Get the text-based collection
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
    print(f"📊 Database contains {total_chunks} chunks from {len(unique_files)} text files")
    
    if unique_files:
        print("📁 Available files:")
        for i, filename in enumerate(sorted(unique_files), 1):
            print(f"  {i}. {filename}")
    print()
    
except Exception as e:
    print(f"❌ Error: Could not find collection '{COLLECTION_NAME}'")
    print("Make sure you've run 'python fill_db_from_txt_files.py' first!")
    print("Or check that your text files are in the 'txt_data' directory.")
    exit(1)

user_query = input("What would you like to know from your text files?\n\n")

# Query the collection
print("🔍 Searching through your text files...")
results = collection.query(
    query_texts=[user_query],
    n_results=10  # Get more chunks to ensure we capture complete information
)

if not results['documents'][0]:
    print("❌ No relevant information found in your text files.")
    print("Try rephrasing your question or add more content to your text files.")
    exit(1)

print(f"\n📄 Found {len(results['documents'][0])} relevant chunks:")
print("="*75)

for i, doc in enumerate(results['documents'][0], 1):
    # Get metadata for this chunk
    meta = results['metadatas'][0][i-1] if results['metadatas'][0] else {}
    source = meta.get('source', 'Unknown file')
    title = meta.get('title', 'No title')
    
    print(f"\n📋 Chunk {i}")
    print(f"📁 File: {source}")
    print(f"📝 Title: {title}")
    print("-" * 55)
    
    # Show preview of chunk
    preview = doc[:300] + "..." if len(doc) > 300 else doc
    print(preview)

# Create system prompt with retrieved documents
system_prompt = f"""You are a helpful AI assistant. You answer questions based ONLY on the provided information from text files. 
You don't use your internal knowledge and you don't make things up.
If you don't know the answer based on the provided information, just say: "I don't have enough information to answer that question based on the provided text files."

The information comes from these text files:
{', '.join(sorted(unique_files))}

Here is the relevant information from the text files:
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
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()['response']
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to Ollama. Make sure Ollama is running.\n\nYou can start it with: ollama serve"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The AI model might be processing a large response."
    except Exception as e:
        return f"Error: {str(e)}"

print("\n" + "="*75)
print("\033[92m🤖 AI ASSISTANT RESPONSE:\033[0m")
print("="*75)

response = query_ollama(system_prompt, user_query)
print(f"\n{response}")

# print(f"\n" + "="*75)
# print("💡 This response is based on content from your text files:")
# for filename in sorted(unique_files):
#     print(f"   📄 {filename}")
# print("="*75)

# # Optional: Show which files were most relevant
# print(f"\n🎯 Most relevant files for your query:")
# file_relevance = {}
# for i, meta in enumerate(results['metadatas'][0]):
#     if meta and 'source' in meta:
#         filename = meta['source']
#         file_relevance[filename] = file_relevance.get(filename, 0) + 1

# if file_relevance:
#     for filename, count in sorted(file_relevance.items(), key=lambda x: x[1], reverse=True):
#         stars = "⭐" * min(count, 3)  # Show up to 3 stars for relevance
#         print(f"   {stars} {filename}: {count} relevant chunks")
# else:
#     print("   No specific file relevance data available")

# # Show content statistics
# print(f"\n📊 Search Statistics:")
# print(f"   🔍 Query: '{user_query}'")
# print(f"   📄 Files searched: {len(unique_files)}")
# print(f"   📝 Total chunks in database: {total_chunks}")
# print(f"   ✅ Relevant chunks found: {len(results['documents'][0])}")
