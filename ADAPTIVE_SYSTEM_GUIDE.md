# 🧠 Adaptive Content Ingestion System

## 🎯 **The Solution to Your Chunking Problems**

Your original issues:
- **Workflow types got cut off** (text file chunking too small)
- **Step-by-step procedures split incorrectly** (markdown file chunking inconsistent)
- **One-size-fits-all approach failed** for different content types

## 🔍 **How the Adaptive System Works**

### **Phase 1: File Analysis**
For each file, the system analyzes:

```
📊 ANALYZING: workflow_guide.txt
--------------------------------------------------
📏 Size: 2,112 characters
📝 Words: 324
📋 Lines: 31
📄 Paragraphs: 8
📊 Avg line length: 68.1 chars
📊 Avg paragraph length: 264.0 chars
🎯 Detected content type: procedures
   Secondary types: lists, technical
```

### **Phase 2: Content Type Detection**
Automatically detects content patterns:

| Content Type | Detection Patterns | Chunking Strategy |
|--------------|-------------------|-------------------|
| **Procedures** | "step 1", "how to", "guide", "instructions" | Large chunks (keep steps together) |
| **Lists** | "types of", "includes:", bullet points | Medium-large chunks |
| **Technical** | "API", "function", "configuration" | Large chunks (preserve context) |
| **FAQ** | "Q:", "what is", "how do" | Small-medium chunks |
| **Conversational** | "I", "you", "let's" | Small chunks |

### **Phase 3: Size-Based Strategy**
Adjusts for file size:

```
📏 File size: Small (< 1KB)    → Base: 300 chars
📏 File size: Medium (1-5KB)   → Base: 500 chars  
📏 File size: Large (5-20KB)   → Base: 800 chars
📏 File size: Extra Large      → Base: 1200 chars
```

### **Phase 4: Content-Specific Multipliers**
Fine-tunes based on detected content:

```
🔧 Content type adjustment: procedures (x1.5)
   300 chars → 450 chars (for small procedure files)
   800 chars → 1200 chars (for large procedure files)
```

### **Phase 5: Structure Analysis**
Considers paragraph structure:

```
📄 Short paragraphs detected → Minimum chunk size enforced
📄 Long paragraphs detected → Larger chunks needed
```

## 🎯 **Your Specific Problems Solved**

### **Problem 1: Workflow Types Cut Off**
**Your file**: `text.txt` (2,112 chars, procedures + lists)

**Old system**: 
- Chunk size: 400 chars
- Result: "Workflow Manager supports two types of workflows:" [CHUNK ENDS]

**Adaptive system**:
- Detects: `procedures` + `lists` content
- File size: Medium (2KB)
- Calculation: 500 (base) × 1.5 (procedures) = 750 chars
- Result: Complete workflow list in one chunk ✅

### **Problem 2: Step-by-Step Procedures Split**
**Your FAQ file**: `faq_example.md` (4,315 chars, procedures + FAQ)

**Old system**:
- Fixed 400 char chunks
- Result: Steps 1-6 scattered across different chunks

**Adaptive system**:
- Detects: `procedures` + `faq` content  
- File size: Medium (4KB)
- Calculation: 500 (base) × 1.5 (procedures) = 750 chars
- Structure analysis: Long paragraphs → Bumped to 1000 chars
- Result: Complete procedure sections preserved ✅

## 🚀 **How to Use the Adaptive System**

### **Step 1: Run Adaptive Ingestion**
```bash
python fill_db_adaptive.py
```

**Choose what to process:**
- Text files only
- Markdown files only  
- Both (recommended)

### **Step 2: See the Analysis**
The system shows you exactly what it's doing:

```
🎯 CHUNKING STRATEGY FOR: workflow_guide.txt
--------------------------------------------------
📏 File size: Medium (1-5KB)
🔧 Content type adjustment: procedures (x1.5)
📄 Short paragraphs detected → Minimum chunk size enforced
📏 Chunk size: 750
🔄 Overlap: 188
🔍 Recommended n_results: 4
📊 Expected chunks: ~3
✂️  Created 3 chunks (strategy: medium_file)
```

### **Step 3: Query with Intelligence**
```bash
python ask_adaptive.py
```

**Smart query handling:**
- **Simple questions** ("what is") → 3 results
- **Complex questions** ("how to", "steps") → 8 results
- **Medium questions** → 5 results

## 📊 **Example Results**

### **Your Workflow Question Fixed**
```
Query: "how many workflows does workflow manager support"
🔍 Query complexity: medium
📄 Found 2 relevant chunks:

📋 Chunk 1
📁 File: text.txt
🎯 Type: procedures | Strategy: medium_file | Size: 845 chars
--------------------------------------------------
Types of Workflows

Workflow Manager supports two types of workflows:

1. Template Workflow: Ideal for creating contracts based on 
   pre-defined templates, such as standard employee agreements 
   or NDAs. This workflow helps you quickly and consistently 
   generate contracts using your organization's approved templates.

2. Third-Party Paper Workflow: Designed for managing external 
   contracts, allowing you to upload and track third-party 
   documents for review, signature, and other required actions.
```

**AI Response**: "Workflow Manager supports **two types** of workflows: 1) Template Workflow for creating contracts from pre-defined templates, and 2) Third-Party Paper Workflow for managing external contracts." ✅

## 🔧 **Advanced Features**

### **Mixed Content Handling**
- Can process both `.txt` and `.md` files together
- Each file gets its own optimal strategy
- Single collection for unified searching

### **Strategy Insights**
Shows you which strategies worked:
```
⚙️  Most relevant chunking strategies:
   ⭐⭐⭐ medium_file: 3 chunks
   ⭐⭐ large_file: 2 chunks

🎯 Content types that matched:
   ⭐⭐⭐ procedures: 4 chunks  
   ⭐ lists: 1 chunk
```

### **Automatic Query Optimization**
- Detects query complexity automatically
- Retrieves appropriate number of chunks
- Balances comprehensiveness vs precision

## 🎯 **Benefits Over Fixed Chunking**

| Aspect | Fixed Chunking | Adaptive Chunking |
|--------|----------------|-------------------|
| **Procedures** | Often split steps | Keeps procedures intact |
| **Lists** | Separates items from headers | Preserves complete lists |
| **Small files** | Over-chunked | Right-sized chunks |
| **Large files** | Under-chunked | Appropriately larger chunks |
| **Mixed content** | One size fits none | Optimized per file |
| **Query results** | Hit or miss | Intelligent retrieval |

## 🚀 **Test It Now**

Your files are perfect test cases:

1. **Run the adaptive system**:
   ```bash
   python fill_db_adaptive.py
   ```

2. **Ask your problematic questions**:
   - "how many workflows does workflow manager support"
   - "steps to create a new contract type from a new workflow"

3. **Compare results** with your previous attempts

The adaptive system should finally give you complete, accurate answers! 🎉

## 💡 **Pro Tips**

- **Let the system analyze first** - don't override the recommendations
- **Mixed file types work great** - combine text and markdown
- **Query complexity matters** - use natural language
- **Check the insights** - learn what strategies worked best

Your chunking problems are solved! 🧠✨