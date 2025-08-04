import chromadb
import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "data_from_txt_files"

# Directory containing your text files
TXT_FILES_DIRECTORY = "txt_data"  # Change this to your text files directory

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

print("📄 Text Files RAG System")
print("=" * 50)

# Create the text directory if it doesn't exist
if not os.path.exists(TXT_FILES_DIRECTORY):
    os.makedirs(TXT_FILES_DIRECTORY)
    print(f"✅ Created directory: {TXT_FILES_DIRECTORY}")
    print(f"📋 Please add your .txt files to the '{TXT_FILES_DIRECTORY}' directory and run this script again.")
    exit(1)

# Find all text files
txt_files = glob.glob(os.path.join(TXT_FILES_DIRECTORY, "*.txt"))

if not txt_files:
    print(f"❌ No .txt files found in '{TXT_FILES_DIRECTORY}' directory!")
    print(f"📋 Please add your text files to the '{TXT_FILES_DIRECTORY}' directory.")
    print("Example text files you can create:")
    print("  - notes.txt")
    print("  - documentation.txt") 
    print("  - faq.txt")
    print("  - procedures.txt")
    print("  - knowledge_base.txt")
    exit(1)

print(f"📁 Found {len(txt_files)} text files:")
for i, file in enumerate(txt_files, 1):
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

def read_text_file(file_path):
    """Read and process a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read().strip()
        
        if not content:
            print(f"⚠️  Warning: {os.path.basename(file_path)} is empty")
            return None
        
        filename = os.path.basename(file_path)
        
        # Try to extract a title from the first line
        lines = content.split('\n')
        first_line = lines[0].strip()
        
        # Use first line as title if it's short and looks like a title
        if len(first_line) < 100 and len(first_line) > 0:
            # Check if first line looks like a title (no periods, reasonable length)
            if first_line.count('.') <= 1 and not first_line.endswith('.'):
                title = first_line
            else:
                title = filename.replace('.txt', '').replace('_', ' ').title()
        else:
            title = filename.replace('.txt', '').replace('_', ' ').title()
        
        return {
            'content': content,
            'filename': filename,
            'title': title,
            'file_path': file_path
        }
        
    except UnicodeDecodeError:
        try:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                content = file.read().strip()
            print(f"⚠️  Used latin-1 encoding for {os.path.basename(file_path)}")
            return {
                'content': content,
                'filename': os.path.basename(file_path),
                'title': os.path.basename(file_path).replace('.txt', '').replace('_', ' ').title(),
                'file_path': file_path
            }
        except Exception as e:
            print(f"❌ Encoding error reading {file_path}: {str(e)}")
            return None
    except Exception as e:
        print(f"❌ Error reading {file_path}: {str(e)}")
        return None

# Read all text files
print(f"\n📖 Reading text files...")
text_data = []

for txt_file in txt_files:
    print(f"Processing: {os.path.basename(txt_file)}")
    data = read_text_file(txt_file)
    if data:
        text_data.append(data)
        print(f"✅ Read {len(data['content'])} characters")
        print(f"   Title: {data['title']}")
    else:
        print(f"❌ Failed to read file")

if not text_data:
    print("❌ No text files were successfully read!")
    exit(1)

print(f"\n📊 Successfully read {len(text_data)} text files")

# Split content into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600,  # Larger chunks to keep related info together
    chunk_overlap=150,  # More overlap to prevent information separation
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

for txt_data in text_data:
    # Create document object for text splitter
    class Document:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata
    
    doc = Document(txt_data['content'], {
        'source': txt_data['filename'],
        'title': txt_data['title'],
        'file_path': txt_data['file_path']
    })
    
    chunks = text_splitter.split_documents([doc])
    
    for chunk in chunks:
        documents.append(chunk.page_content)
        ids.append(f"TXT_CHUNK_{chunk_id}")
        metadata.append({
            'source': txt_data['filename'],
            'title': txt_data['title'],
            'file_path': txt_data['file_path'],
            'chunk_id': chunk_id,
            'type': 'text_file'
        })
        chunk_id += 1

print(f"📝 Created {len(documents)} chunks from text files")

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

print(f"\n🚀 Done! Your text file knowledge base is ready!")
print(f"📁 Collection name: {COLLECTION_NAME}")
print("Run this command to ask questions:")
print("python ask_txt_data.py")