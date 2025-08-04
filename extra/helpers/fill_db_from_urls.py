import chromadb
import requests
from bs4 import BeautifulSoup
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import time

# setting the environment
CHROMA_PATH = r"chroma_db"

# collection name
COLLECTION_NAME = "data_from_urls"

# List of URLs to scrape (you can modify this list)
URLS = [
    # "https://training.spotdraft.com/f3c6Oa85Rn8p39SRei2Upw/CfVlglsm8i0i0LlV44j6Gg"
    # "https://extension.ufl.edu/publication/vegetable-gardening-in-florida",
    # "https://edis.ifas.ufl.edu/topic_vegetable_gardening", 
    # "https://gardeningsolutions.ifas.ufl.edu/plants/edibles/vegetables/",
    # Add more URLs here as needed
    "https://help.spotdraft.com/hc/en-us/articles/20195055646109-Getting-Started-With-The-Workflow-Manager"
]

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Try to delete existing collection first to avoid configuration conflicts
try:
    chroma_client.delete_collection(name=COLLECTION_NAME)
    print("Deleted existing collection")
except:
    print("No existing collection to delete")

# Create collection with single thread configuration to avoid thread count issues
collection = chroma_client.create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:num_threads": 1}
)

def scrape_url(url):
    """Scrape content from a single URL"""
    try:
        print(f"Scraping: {url}")
        
        # Add headers to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up text - remove extra whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text, url
        
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return None, url

# Scrape all URLs
documents = []
metadata = []
ids = []
scraped_content = []

print("Starting web scraping...")

for url in URLS:
    content, source_url = scrape_url(url)
    if content:
        scraped_content.append({
            'content': content,
            'source': source_url
        })
        print(f"✅ Successfully scraped: {source_url}")
    else:
        print(f"❌ Failed to scrape: {source_url}")
    
    # Be respectful - wait between requests
    time.sleep(1)

print(f"\nSuccessfully scraped {len(scraped_content)} URLs")

# Split the scraped content into chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=100,
    length_function=len,
    is_separator_regex=False,
)

print("Splitting content into chunks...")

chunk_id = 0
for item in scraped_content:
    # Create a document-like object for the text splitter
    class Document:
        def __init__(self, page_content, metadata):
            self.page_content = page_content
            self.metadata = metadata
    
    doc = Document(item['content'], {'source': item['source']})
    chunks = text_splitter.split_documents([doc])
    
    for chunk in chunks:
        documents.append(chunk.page_content)
        ids.append(f"URL_CHUNK_{chunk_id}")
        metadata.append({
            'source': item['source'],
            'chunk_id': chunk_id
        })
        chunk_id += 1

print(f"Created {len(documents)} chunks from web content")

# Add to ChromaDB
print("Adding content to ChromaDB...")

if documents:
    collection.upsert(
        documents=documents,
        metadatas=metadata,
        ids=ids
    )
    print(f"✅ Successfully added {len(documents)} chunks to the database!")
else:
    print("❌ No content was scraped successfully")

print("\nDone! You can now use ask_ollama.py to query the web-based knowledge base.")