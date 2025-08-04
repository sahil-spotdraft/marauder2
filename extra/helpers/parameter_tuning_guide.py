#!/usr/bin/env python3
"""
RAG System Parameter Tuning Guide

This script helps you understand and test different parameters for optimal RAG performance.
"""

import chromadb
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

def analyze_content_characteristics(file_path):
    """Analyze your content to help decide optimal parameters"""
    
    print("📊 CONTENT ANALYSIS")
    print("=" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Basic statistics
    total_chars = len(content)
    total_words = len(content.split())
    lines = content.split('\n')
    paragraphs = [p for p in content.split('\n\n') if p.strip()]
    
    print(f"📄 File: {os.path.basename(file_path)}")
    print(f"📏 Total characters: {total_chars:,}")
    print(f"📝 Total words: {total_words:,}")
    print(f"📋 Total lines: {len(lines)}")
    print(f"📄 Paragraphs: {len(paragraphs)}")
    print(f"📊 Average chars per line: {total_chars / len(lines):.1f}")
    print(f"📊 Average chars per paragraph: {total_chars / len(paragraphs):.1f}" if paragraphs else "No paragraphs detected")
    
    # Analyze structure
    headers = [line for line in lines if line.strip() and (
        line.startswith('#') or 
        line.isupper() or 
        ':' in line and len(line.split(':')[0]) < 50
    )]
    
    lists = [line for line in lines if line.strip().startswith(('- ', '* ', '1. ', '2. '))]
    
    print(f"🏷️  Headers/Titles: {len(headers)}")
    print(f"📋 List items: {len(lists)}")
    
    return {
        'total_chars': total_chars,
        'total_words': total_words,
        'avg_chars_per_line': total_chars / len(lines),
        'avg_chars_per_paragraph': total_chars / len(paragraphs) if paragraphs else 0,
        'headers': len(headers),
        'lists': len(lists)
    }

def recommend_chunk_size(content_stats, content_type="general"):
    """Recommend chunk size based on content analysis"""
    
    print(f"\n🎯 CHUNK SIZE RECOMMENDATIONS")
    print("=" * 50)
    
    avg_para = content_stats['avg_chars_per_paragraph']
    
    if content_type == "technical":
        base_size = 800
        print("📋 Content Type: Technical Documentation")
        print("💡 Recommendation: Larger chunks to preserve technical context")
        
    elif content_type == "conversational":
        base_size = 300
        print("📋 Content Type: Conversational/Chat")
        print("💡 Recommendation: Smaller chunks for quick, precise answers")
        
    elif content_type == "reference":
        base_size = 600
        print("📋 Content Type: Reference Material")
        print("💡 Recommendation: Medium chunks for balanced context")
        
    else:
        base_size = 500
        print("📋 Content Type: General")
        print("💡 Recommendation: Medium chunks for general purpose")
    
    # Adjust based on content structure
    if avg_para > 0:
        if avg_para < 200:
            recommended = min(base_size, 400)
            print(f"📏 Short paragraphs detected ({avg_para:.0f} chars) → Use smaller chunks")
        elif avg_para > 800:
            recommended = max(base_size, 700)
            print(f"📏 Long paragraphs detected ({avg_para:.0f} chars) → Use larger chunks")
        else:
            recommended = base_size
            print(f"📏 Medium paragraphs detected ({avg_para:.0f} chars) → Standard size")
    else:
        recommended = base_size
    
    print(f"🎯 RECOMMENDED CHUNK SIZE: {recommended}")
    
    return recommended

def recommend_overlap(chunk_size):
    """Recommend overlap based on chunk size"""
    
    print(f"\n🔄 OVERLAP RECOMMENDATIONS")
    print("=" * 50)
    
    # Rule of thumb: 20-30% of chunk size
    min_overlap = int(chunk_size * 0.2)
    max_overlap = int(chunk_size * 0.3)
    recommended = int(chunk_size * 0.25)  # 25% is usually good
    
    print(f"📊 For chunk size {chunk_size}:")
    print(f"   Minimum overlap: {min_overlap} (20%)")
    print(f"   Maximum overlap: {max_overlap} (30%)")
    print(f"🎯 RECOMMENDED OVERLAP: {recommended} (25%)")
    
    print(f"\n💡 Overlap Guidelines:")
    print(f"   • Too little overlap (<15%): Risk losing context")
    print(f"   • Too much overlap (>35%): Redundant information")
    print(f"   • Sweet spot (20-30%): Balanced context preservation")
    
    return recommended

def recommend_n_results(content_stats, query_complexity="medium"):
    """Recommend number of results to retrieve"""
    
    print(f"\n🔍 RETRIEVAL RESULTS RECOMMENDATIONS")
    print("=" * 50)
    
    total_chunks_estimate = content_stats['total_chars'] // 500  # Rough estimate
    
    if query_complexity == "simple":
        recommended = min(3, max(2, total_chunks_estimate // 5))
        print("❓ Query Type: Simple factual questions")
        print("💡 Need fewer, more precise results")
        
    elif query_complexity == "complex":
        recommended = min(8, max(4, total_chunks_estimate // 3))
        print("❓ Query Type: Complex, multi-part questions")
        print("💡 Need more results to capture full context")
        
    else:  # medium
        recommended = min(6, max(3, total_chunks_estimate // 4))
        print("❓ Query Type: Medium complexity")
        print("💡 Balanced approach")
    
    print(f"📊 Estimated total chunks: {total_chunks_estimate}")
    print(f"🎯 RECOMMENDED N_RESULTS: {recommended}")
    
    print(f"\n💡 Results Guidelines:")
    print(f"   • Too few results (<3): May miss relevant info")
    print(f"   • Too many results (>8): Noise and slower processing")
    print(f"   • Sweet spot: 4-6 for most use cases")
    
    return recommended

def test_chunking_parameters(file_path, chunk_size, overlap):
    """Test how your content gets chunked with given parameters"""
    
    print(f"\n🧪 CHUNKING TEST")
    print("=" * 50)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create splitter with test parameters
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
        is_separator_regex=False,
    )
    
    # Create a simple document object
    class TestDoc:
        def __init__(self, content):
            self.page_content = content
            self.metadata = {}
    
    doc = TestDoc(content)
    chunks = splitter.split_documents([doc])
    
    print(f"📄 Original content: {len(content)} characters")
    print(f"✂️  Created chunks: {len(chunks)}")
    print(f"📊 Average chunk size: {sum(len(c.page_content) for c in chunks) / len(chunks):.1f} chars")
    
    print(f"\n📋 First 3 chunks preview:")
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i+1} ({len(chunk.page_content)} chars) ---")
        preview = chunk.page_content[:200] + "..." if len(chunk.page_content) > 200 else chunk.page_content
        print(preview)
    
    return len(chunks)

def main():
    """Main parameter tuning guide"""
    
    print("🎯 RAG SYSTEM PARAMETER TUNING GUIDE")
    print("=" * 60)
    
    # Get file to analyze
    txt_files = [f for f in os.listdir('txt_data') if f.endswith('.txt')]
    
    if not txt_files:
        print("❌ No .txt files found in txt_data directory!")
        print("Please add some text files first.")
        return
    
    print("📁 Available files:")
    for i, file in enumerate(txt_files):
        print(f"  {i+1}. {file}")
    
    try:
        choice = int(input(f"\nSelect file to analyze (1-{len(txt_files)}): ")) - 1
        selected_file = os.path.join('txt_data', txt_files[choice])
    except (ValueError, IndexError):
        selected_file = os.path.join('txt_data', txt_files[0])
        print(f"Using first file: {txt_files[0]}")
    
    # Analyze content
    stats = analyze_content_characteristics(selected_file)
    
    # Get content type
    print(f"\n❓ What type of content is this?")
    print("1. Technical documentation")
    print("2. Conversational/FAQ")
    print("3. Reference material")
    print("4. General content")
    
    try:
        content_type_choice = int(input("Enter choice (1-4): "))
        content_types = ["technical", "conversational", "reference", "general"]
        content_type = content_types[content_type_choice - 1]
    except (ValueError, IndexError):
        content_type = "general"
    
    # Get recommendations
    recommended_chunk_size = recommend_chunk_size(stats, content_type)
    recommended_overlap = recommend_overlap(recommended_chunk_size)
    recommended_n_results = recommend_n_results(stats)
    
    # Test the recommendations
    print(f"\n🧪 Testing recommended parameters...")
    chunk_count = test_chunking_parameters(selected_file, recommended_chunk_size, recommended_overlap)
    
    # Final recommendations
    print(f"\n🎯 FINAL RECOMMENDATIONS")
    print("=" * 60)
    print(f"📏 Chunk Size: {recommended_chunk_size}")
    print(f"🔄 Overlap: {recommended_overlap}")
    print(f"🔍 N Results: {recommended_n_results}")
    print(f"📊 Expected chunks: {chunk_count}")
    
    print(f"\n📝 UPDATE YOUR CONFIG:")
    print(f"In fill_db_from_txt_files.py:")
    print(f"   chunk_size={recommended_chunk_size}")
    print(f"   chunk_overlap={recommended_overlap}")
    print(f"")
    print(f"In ask_txt_data.py:")
    print(f"   n_results={recommended_n_results}")

if __name__ == "__main__":
    main()