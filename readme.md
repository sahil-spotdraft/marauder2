# 🌍 Universal RAG System

A complete, free, and intelligent Retrieval-Augmented Generation system that works with **any file type** and automatically adapts to your content structure.

## 🚀 **Quick Start**

### **1. Add Your Files**
Put any supported files in these directories:
```
txt_data/     - Text files, markdown, code, etc.
md_data/      - Markdown files, documentation
data/         - PDFs, Word docs, JSON, CSV, etc.
```

### **2. Process All Content**
```bash
python fill_db.py
```
The system will automatically detect file types and optimize processing for each!

### **3. Ask Questions**
```bash
python ask.py
```
Query across all your content with intelligent AI responses!

## 🗂️ **Supported File Types**

| Category | Extensions | What It Handles |
|----------|------------|-----------------|
| **📄 Text** | `.txt`, `.md`, `.py`, `.js`, `.html`, `.css`, `.sql`, `.yml`, `.xml` | Code, docs, configs |
| **📊 Data** | `.json`, `.csv`, `.log`, `.ini`, `.cfg` | Structured data |
| **📖 Documents** | `.pdf`, `.docx` | PDFs, Word documents |
| **🔧 Any Text File** | Any extension | Universal text reader |

## 🧠 **Intelligent Features**

### **🎯 Automatic Content Detection**
The system analyzes your files and detects:
- **Procedures**: Step-by-step guides → Large chunks to keep steps together
- **Lists**: Options, types, categories → Medium chunks to preserve complete lists  
- **Technical**: Code, APIs, configs → Context-aware chunking
- **FAQ**: Questions & answers → Focused, precise chunks
- **Data**: JSON, CSV structures → Structure-aware processing

### **📏 Adaptive Chunking**
- **Small files** (< 1KB) → 300 char chunks
- **Medium files** (1-5KB) → 500 char chunks  
- **Large files** (5-20KB) → 800 char chunks
- **Huge files** (> 100KB) → 1600 char chunks
- **Plus content-type multipliers** for optimal results!

### **🔍 Smart Querying**
- **Simple questions** → 3 precise results
- **Complex questions** → 8 comprehensive results
- **Technical queries** → 6 context-rich results

## 📊 **Real Example**

Your original problem: *"How many workflows does workflow manager support?"*

**Old systems**: "Workflow Manager supports two types of workflows:" [CHUNK ENDS]

**Universal system**:
1. **Detects**: "lists" content type  
2. **Uses**: 700 character chunks (1.4x multiplier)
3. **Result**: Complete answer with both workflow types! ✅

## 🎪 **Advanced Features**

### **Mixed Content Handling**
- Process PDFs, Word docs, JSON, and text files together
- Single knowledge base for unified searching
- Intelligent result ranking across file types

### **Development Insights**
```
🗂️  File formats that matched your query:
   ⭐⭐⭐ TEXT: 4 chunks
   ⭐⭐ PDF: 2 chunks
   ⭐ JSON: 1 chunk

🎯 Content types that were relevant:
   ⭐⭐⭐ procedures: 5 chunks
   ⭐⭐ lists: 2 chunks
```

### **Query Suggestions**
The system provides intelligent suggestions based on your content:
- "What are the steps to..."
- "List all the options for..."
- "What data is stored in the JSON files?"

## 🔧 **Configuration Options**

### **Custom Directories**
```bash
python fill_db.py
# Choose option 2: Specific directories
# Enter: docs, manuals, code, data
```

### **Different Collection Names**
Edit `COLLECTION_NAME` in the files for multiple knowledge bases.

### **Model Selection**
Change the model in `ask.py`:
```python
"model": "llama3.2",  # or llama2, codellama, etc.
```

## 📁 **Project Structure**
```
├── fill_db.py          # 🌍 Universal content processor
├── ask.py              # 🌍 Universal query system  
├── helpers/            # 🛠️ Specific implementations
│   ├── fill_db.py      # Original PDF system
│   ├── ask_ollama.py   # Ollama-specific queries
│   └── README.md       # Helper documentation
├── txt_data/           # Text files directory
├── md_data/            # Markdown files directory  
├── data/               # Documents, PDFs, data files
└── chroma_db/          # Vector database
```

## 🆚 **Universal vs Specific Systems**

| Feature | Universal System | Specific Helpers |
|---------|------------------|------------------|
| **Supported Files** | All major formats | Single format |
| **Complexity** | Automatic adaptation | Manual tuning |
| **Maintenance** | One system | Multiple tools |
| **Results** | ✅ Best for most users | Specialized needs |

## 🛠️ **Dependencies**

### **Required**
```bash
pip install chromadb langchain-text-splitters requests
```

### **Optional (for specific file types)**
```bash
pip install PyPDF2          # PDF support
pip install python-docx     # Word document support  
pip install beautifulsoup4  # Web scraping (if using helpers)
```

### **AI Model**
- **Ollama** (free, local): [Download here](https://ollama.com)
- **Models**: `ollama pull llama3.2`

## 🎯 **Use Cases**

### **Perfect For:**
- **Documentation systems** - Mix of markdown, PDFs, and text files
- **Code projects** - Source code + documentation + configs
- **Research** - Papers (PDF) + notes (text) + data (JSON/CSV)
- **Knowledge bases** - Any combination of file types
- **Personal productivity** - Notes, documents, references

### **Example Workflows:**
1. **Software Project**: Code files + README + JSON configs + API docs
2. **Research Project**: PDF papers + CSV data + markdown notes
3. **Business Documentation**: Word docs + PDFs + text procedures
4. **Personal Knowledge**: Mixed notes, documents, and references

## 🚀 **Migration from Other Systems**

If you have an existing RAG system:

1. **Copy your files** to the appropriate directories
2. **Run**: `python fill_db.py`
3. **Test**: `python ask.py`
4. **Done!** Your universal system is ready

## 🎉 **Why This System Is Special**

### **🧠 Intelligence**
- Automatically adapts to each file type and content structure
- No manual parameter tuning required
- Learns from your content patterns

### **🌍 Universality**  
- Works with any text-based file format
- Handles mixed content collections
- Single interface for all your information

### **💰 Free & Private**
- Completely free to use
- Runs locally on your machine
- No API costs or data sharing

### **📈 Performance**
- Intelligent chunking prevents information loss
- Smart query complexity detection
- Optimized retrieval for different content types

---

**🎯 Ready to build your universal knowledge base?**

```bash
python fill_db.py  # Process your content
python ask.py      # Start asking questions!
```

Your days of incomplete RAG answers are over! 🚀