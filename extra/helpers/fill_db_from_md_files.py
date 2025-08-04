import chromadb
import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "data_from_md_files"

# Directory containing your markdown files
MD_FILES_DIRECTORY = "md_data"  # Change this to your markdown files directory

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

print("📄 Markdown Files RAG System")
print("=" * 50)

# Create the markdown directory if it doesn't exist
if not os.path.exists(MD_FILES_DIRECTORY):
    os.makedirs(MD_FILES_DIRECTORY)
    print(f"✅ Created directory: {MD_FILES_DIRECTORY}")
    print(f"📋 Please add your .md files to the '{MD_FILES_DIRECTORY}' directory and run this script again.")
    exit(1)

# Find all markdown files
md_files = glob.glob(os.path.join(MD_FILES_DIRECTORY, "*.md"))

if not md_files:
    print(f"❌ No .md files found in '{MD_FILES_DIRECTORY}' directory!")
    print(f"📋 Please add your markdown files to the '{MD_FILES_DIRECTORY}' directory.")
    print("Example markdown files you can create:")
    print("  - documentation.md")
    print("  - faq.md") 
    print("  - guide.md")
    print("  - any-content.md")
    exit(1)

print(f"📁 Found {len(md_files)} markdown files:")
for i, file in enumerate(md_files, 1):
    filename = os.path.basename(file)
    file_size = os.path.getsize(file)
    print(f"  {i}. {filename} ({file_size} bytes)")

# Ask if user wants to replace existing data
replace_data = input(f"\nReplace existing data in collection '{COLLECTION_NAME}'? (y/n): ").strip().lower()

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

def read_markdown_file(file_path):
    """Read and process a markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Basic markdown processing
        filename = os.path.basename(file_path)
        
        # Extract title from first # heading if exists
        lines = content.split('\n')
        title = filename
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        return {
            'content': content,
            'filename': filename,
            'title': title,
            'file_path': file_path
        }
        
    except Exception as e:
        print(f"❌ Error reading {file_path}: {str(e)}")
        return None

# Read all markdown files
print(f"\n📖 Reading markdown files...")
markdown_data = []

for md_file in md_files:
    print(f"Processing: {os.path.basename(md_file)}")
    data = read_markdown_file(md_file)
    if data:
        markdown_data.append(data)
        print(f"✅ Read {len(data['content'])} characters")
    else:
        print(f"❌ Failed to read file")

if not markdown_data:
    print("❌ No markdown files were successfully read!")
    exit(1)

print(f"\n📊 Successfully read {len(markdown_data)} markdown files")

# Split content into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,  # Slightly larger chunks for markdown
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

print("✂️  Splitting content into chunks...")

documents = []
metadata = []
ids = []

# Get existing chunk count to continue numbering
existing_chunks = collection.get()
chunk_id = len(existing_chunks['ids']) if existing_chunks['ids'] else 0

for md_data in markdown_data:
    # Create document object for text splitter
    class Document:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata
    
    doc = Document(md_data['content'], {
        'source': md_data['filename'],
        'title': md_data['title'],
        'file_path': md_data['file_path']
    })
    
    chunks = text_splitter.split_documents([doc])
    
    for chunk in chunks:
        documents.append(chunk.page_content)
        ids.append(f"MD_CHUNK_{chunk_id}")
        metadata.append({
            'source': md_data['filename'],
            'title': md_data['title'],
            'file_path': md_data['file_path'],
            'chunk_id': chunk_id,
            'type': 'markdown_file'
        })
        chunk_id += 1

print(f"📝 Created {len(documents)} chunks from markdown files")

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
        title = metadata[i]['title']
        print(f"{i+1}. [{source}] {title}")
        print(f"   {doc[:100]}...")
    
    # Show file breakdown
    print(f"\n📁 Files processed breakdown:")
    file_count = {}
    for meta in metadata:
        filename = meta['source']
        file_count[filename] = file_count.get(filename, 0) + 1
    
    for filename, count in file_count.items():
        print(f"  📄 {filename}: {count} chunks")
    
else:
    print("❌ No content was processed")

print(f"\n🚀 Done! Your markdown knowledge base is ready!")
print(f"📁 Collection name: {COLLECTION_NAME}")
print("Run this command to ask questions:")
print("python ask_md_data.py")