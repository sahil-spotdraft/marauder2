import chromadb
import requests
from bs4 import BeautifulSoup
import time
import random
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter

# setting the environment
CHROMA_PATH = r"chroma_db"
COLLECTION_NAME = "data_from_urls"

# Enhanced headers to avoid being blocked
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0'
}

# List of URLs to scrape - Try these public, scraping-friendly alternatives
URLS = [
    # Try some open gardening resources (more scraping-friendly)
    # "https://www.almanac.com/plant/onions",
    # "https://www.almanac.com/plant/tomatoes", 
    # "https://www.almanac.com/plant/potatoes",
    # "https://help.spotdraft.com/hc/en-us/articles/20195055646109-Getting-Started-With-The-Workflow-Manager"
    "https://en.wikipedia.org/wiki/Main_Page"
    
    # Or uncomment your original URL to try with enhanced headers:
    # "https://help.spotdraft.com/hc/en-us/articles/20195055646109-Getting-Started-With-The-Workflow-Manager"
]

def enhanced_scrape_url(url, max_retries=3):
    """Enhanced web scraping with better error handling and retry logic"""
    
    for attempt in range(max_retries):
        try:
            print(f"Scraping attempt {attempt + 1}/{max_retries}: {url}")
            
            # Add random delay to appear more human-like
            time.sleep(random.uniform(1, 3))
            
            # Create session for better connection handling
            session = requests.Session()
            session.headers.update(HEADERS)
            
            response = session.get(url, timeout=15)
            
            # Check if we got blocked
            if response.status_code == 403:
                print(f"❌ Access forbidden (403) - Website blocking scraping")
                return None, url
            elif response.status_code == 429:
                print(f"⏳ Rate limited (429) - Waiting longer...")
                time.sleep(10)
                continue
            elif response.status_code != 200:
                print(f"❌ HTTP {response.status_code} error")
                return None, url
            
            # Parse content with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if len(text) > 100:  # Only return if we got substantial content
                print(f"✅ Successfully scraped: {len(text)} characters")
                return text, url
            else:
                print(f"❌ Content too short: {len(text)} characters")
                return None, url
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request error: {str(e)}")
            if attempt < max_retries - 1:
                print(f"⏳ Retrying in {(attempt + 1) * 2} seconds...")
                time.sleep((attempt + 1) * 2)
            continue
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            return None, url
    
    return None, url

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

# Delete existing collection
try:
    chroma_client.delete_collection(name=COLLECTION_NAME)
    print("Deleted existing collection")
except:
    print("No existing collection to delete")

# Create new collection
collection = chroma_client.create_collection(
    name=COLLECTION_NAME,
    metadata={"hnsw:num_threads": 1}
)

# Scrape content
documents = []
metadata = []
ids = []
scraped_content = []

print("Starting enhanced web scraping...")
print(f"Will attempt to scrape {len(URLS)} URLs")

for i, url in enumerate(URLS, 1):
    print(f"\n[{i}/{len(URLS)}] Processing: {url}")
    content, source_url = enhanced_scrape_url(url)
    
    if content:
        scraped_content.append({
            'content': content,
            'source': source_url
        })
        print(f"✅ Added to collection")
    else:
        print(f"❌ Skipped due to errors")

print(f"\nSuccessfully scraped {len(scraped_content)} URLs")

if not scraped_content:
    print("\n⚠️  No content was scraped successfully!")
    print("This might be because:")
    print("1. Websites are blocking automated access")
    print("2. URLs are not accessible")
    print("3. Content is loaded dynamically with JavaScript")
    print("\nTry the manual content input option instead!")
else:
    # Split content into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        is_separator_regex=False,
    )

    print("Splitting content into chunks...")

    chunk_id = 0
    for item in scraped_content:
        # Create document object
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
    
    collection.upsert(
        documents=documents,
        metadatas=metadata,
        ids=ids
    )
    print(f"✅ Successfully added {len(documents)} chunks to the database!")

print("\nDone! You can now use ask_url_data.py to query the knowledge base.")