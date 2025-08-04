import chromadb
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "data_from_urls"

print("📝 Manual Content Input for RAG System")
print("=" * 50)
print("Since some websites block automated scraping,")
print("you can manually paste content here!")
print()

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Ask if user wants to replace existing data
replace_data = input("Replace existing data in the collection? (y/n): ").strip().lower()

if replace_data in ['y', 'yes']:
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
        print("✅ Deleted existing collection")
    except:
        print("No existing collection to delete")

# Create or get collection
try:
    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:num_threads": 1}
    )
    print("✅ Created new collection")
except:
    collection = chroma_client.get_collection(name=COLLECTION_NAME)
    print("✅ Using existing collection")

# Collect content manually
content_pieces = []

print("\n📋 Instructions:")
print("1. Copy content from the website you want to use")
print("2. Paste it below (you can paste multiple sections)")
print("3. Type 'DONE' on a new line when finished")
print("4. Leave empty and press Enter to skip a section")
print()

section_number = 1
while True:
    print(f"\n--- Section {section_number} ---")
    source_url = input(f"Source URL for this content (optional): ").strip()
    if not source_url:
        source_url = f"Manual Input Section {section_number}"
    
    print("Paste your content below (press Enter twice when done with this section):")
    
    content_lines = []
    empty_line_count = 0
    
    while True:
        line = input()
        if line.strip() == "DONE":
            break
        elif line.strip() == "":
            empty_line_count += 1
            if empty_line_count >= 2:
                break
            content_lines.append(line)
        else:
            empty_line_count = 0
            content_lines.append(line)
    
    if line.strip() == "DONE":
        break
        
    content = "\n".join(content_lines).strip()
    
    if content:
        content_pieces.append({
            'content': content,
            'source': source_url
        })
        print(f"✅ Added section {section_number} ({len(content)} characters)")
        section_number += 1
    else:
        print("❌ Empty section, skipping")
    
    continue_adding = input("\nAdd another section? (y/n): ").strip().lower()
    if continue_adding not in ['y', 'yes']:
        break

if not content_pieces:
    print("❌ No content was added!")
    exit(1)

print(f"\n📊 Processing {len(content_pieces)} content sections...")

# Split content into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

documents = []
metadata = []
ids = []

# Get existing chunk count to continue numbering
existing_chunks = collection.get()
chunk_id = len(existing_chunks['ids']) if existing_chunks['ids'] else 0

for i, item in enumerate(content_pieces, 1):
    print(f"Processing section {i}...")
    
    # Create document object for text splitter
    class Document:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata
    
    doc = Document(item['content'], {'source': item['source']})
    chunks = text_splitter.split_documents([doc])
    
    for chunk in chunks:
        documents.append(chunk.page_content)
        ids.append(f"MANUAL_CHUNK_{chunk_id}")
        metadata.append({
            'source': item['source'],
            'chunk_id': chunk_id,
            'type': 'manual_input'
        })
        chunk_id += 1

print(f"✂️  Created {len(documents)} chunks from manual content")

# Add to ChromaDB
print("💾 Adding content to ChromaDB...")

if documents:
    collection.upsert(
        documents=documents,
        metadatas=metadata,
        ids=ids
    )
    
    total_chunks = len(collection.get()['ids'])
    print(f"✅ Successfully added {len(documents)} chunks to the database!")
    print(f"📊 Total chunks in database: {total_chunks}")
    
    print(f"\n📋 Sample chunks:")
    for i, doc in enumerate(documents[:3]):
        source = metadata[i]['source']
        print(f"{i+1}. [{source}] {doc[:100]}...")
    
else:
    print("❌ No content was processed")

print("\n🚀 Done! Your knowledge base now contains your manual content!")
print("Run this command to ask questions:")
print("python ask_url_data.py")