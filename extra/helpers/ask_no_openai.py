import chromadb
from dotenv import load_dotenv
import os

load_dotenv()

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

print("\n" + "="*50)
print("RETRIEVED INFORMATION FROM YOUR DOCUMENTS:")
print("="*50)

# Display the retrieved documents in a readable format
for i, doc in enumerate(results['documents'][0], 1):
    print(f"\n📄 Document {i}:")
    print("-" * 30)
    print(doc.strip())

print("\n" + "="*50)
print("SIMPLE ANSWER BASED ON RETRIEVED INFORMATION:")
print("="*50)

# Create a simple formatted response from the retrieved documents
all_text = " ".join(results['documents'][0])

# Simple keyword-based responses for common vegetables
if "potato" in user_query.lower():
    print("\n🥔 POTATO GROWING TIPS:")
    print("Based on your documents:")
    if "potato" in all_text.lower():
        # Extract potato-specific information
        sentences = all_text.split('.')
        potato_info = [s.strip() for s in sentences if 'potato' in s.lower() and len(s.strip()) > 10]
        for info in potato_info:
            if info:
                print(f"• {info.strip()}")
    else:
        print("• No specific potato information found in your documents.")

elif "cabbage" in user_query.lower():
    print("\n🥬 CABBAGE GROWING TIPS:")
    print("Based on your documents:")
    if "cabbage" in all_text.lower():
        sentences = all_text.split('.')
        cabbage_info = [s.strip() for s in sentences if 'cabbage' in s.lower() and len(s.strip()) > 10]
        for info in cabbage_info:
            if info:
                print(f"• {info.strip()}")
    else:
        print("• No specific cabbage information found in your documents.")

else:
    print(f"\n🌱 INFORMATION ABOUT '{user_query.upper()}':")
    print("Here's what I found in your documents:")
    
    # Extract relevant sentences based on query keywords
    query_words = user_query.lower().split()
    sentences = all_text.split('.')
    relevant_sentences = []
    
    for sentence in sentences:
        if any(word in sentence.lower() for word in query_words) and len(sentence.strip()) > 15:
            relevant_sentences.append(sentence.strip())
    
    if relevant_sentences:
        for sentence in relevant_sentences[:3]:  # Show top 3 relevant sentences
            print(f"• {sentence}")
    else:
        print("• Check the retrieved documents above for relevant information.")

print(f"\n💡 TIP: Your RAG system successfully found {len(results['documents'][0])} relevant document chunks!")
print("To get AI-generated answers, you'll need to resolve your OpenAI quota issue.")