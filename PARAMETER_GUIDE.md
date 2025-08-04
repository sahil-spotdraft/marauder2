# 🎯 RAG Parameter Tuning Guide

## 🤔 **The Problem You Experienced**

Your question: "how many workflows is supported by workflow manager"
Your text had: "Workflow Manager supports two types of workflows: 1. Template Workflow... 2. Third-Party Paper Workflow..."

But the chunk ended right after "two types of workflows:" without the actual list!

## 📊 **Key Parameters to Tune**

### 1. **Chunk Size** (`chunk_size`)
**What it does**: How many characters to include in each chunk
**Your issue**: 400 chars was too small, cutting off the workflow list

#### Decision Framework:
```
Content Type          | Recommended Size | Why
---------------------|------------------|------------------------
Technical docs       | 600-800 chars   | Complex context needed
FAQ/Simple answers   | 300-500 chars   | Quick, focused answers  
Reference material   | 500-700 chars   | Balanced approach
Lists & procedures   | 600-800 chars   | Keep items together
Conversational       | 200-400 chars   | Brief, specific responses
```

#### How to Decide:
- **Check your content structure**:
  - Short paragraphs → Smaller chunks (300-400)
  - Long paragraphs → Larger chunks (600-800)
  - Lists/procedures → Larger chunks (600+)

- **Test with your specific content**:
  - Too small: Important info gets cut off
  - Too large: Irrelevant info dilutes answers

### 2. **Chunk Overlap** (`chunk_overlap`) 
**What it does**: How many characters to repeat between chunks
**Why needed**: Prevents important info from being split

#### Decision Rules:
```
Chunk Size | Recommended Overlap | Percentage
-----------|-------------------|------------
300        | 60-90             | 20-30%
400        | 80-120            | 20-30%  
500        | 100-150           | 20-30%
600        | 120-180           | 20-30%
800        | 160-240           | 20-30%
```

#### Sweet Spot:
- **Too little overlap** (<15%): Risk losing context
- **Too much overlap** (>35%): Redundant, slower processing
- **Just right** (20-30%): Preserves context without redundancy

### 3. **Number of Results** (`n_results`)
**What it does**: How many chunks to retrieve for each question
**Your issue**: 4 chunks might not capture complete information

#### Decision Framework:
```
Question Type        | Recommended Results | Why
--------------------|-------------------|------------------
Simple facts        | 3-4               | Precise, focused
Complex questions    | 6-8               | Multiple perspectives  
"How many/what are"  | 4-6               | Complete lists
Troubleshooting      | 5-7               | Multiple solutions
Comparison           | 6-8               | Different aspects
```

## 🧪 **Testing Your Parameters**

### Quick Test Method:
1. **Look at your content** - identify important sections that should stay together
2. **Test chunk size** - make sure complete thoughts aren't split
3. **Check overlaps** - ensure context flows between chunks
4. **Try different n_results** - see if you get complete answers

### Example for Your Workflow Case:
```
Original problem:
"Workflow Manager supports two types of workflows:" [CHUNK ENDS]
"1. Template Workflow: ..." [NEW CHUNK STARTS]

Fixed with larger chunks:
"Workflow Manager supports two types of workflows:
1. Template Workflow: Ideal for creating contracts...  
2. Third-Party Paper Workflow: Designed for managing..." [COMPLETE INFO IN ONE CHUNK]
```

## 🎯 **Recommended Settings by Use Case**

### **For Your SpotDraft Content:**
```python
# Technical documentation with lists and procedures
chunk_size = 600      # Large enough for complete lists
chunk_overlap = 150   # 25% overlap for context
n_results = 6         # Ensure complete information
```

### **For General Documentation:**
```python
chunk_size = 500      # Balanced approach
chunk_overlap = 125   # 25% overlap
n_results = 4         # Standard retrieval
```

### **For FAQ/Simple Q&A:**
```python
chunk_size = 400      # Focused answers
chunk_overlap = 100   # 25% overlap  
n_results = 3         # Precise results
```

### **For Complex Technical Content:**
```python
chunk_size = 800      # Preserve complex context
chunk_overlap = 200   # 25% overlap
n_results = 6         # Comprehensive coverage
```

## 🔧 **Practical Steps to Optimize**

### Step 1: Analyze Your Content
- Average paragraph length?
- Lists and procedures?
- Complex relationships?
- Question types you'll ask?

### Step 2: Start with These Defaults:
```python
chunk_size = 600      # Good for most content
chunk_overlap = 150   # 25% rule
n_results = 5         # Balanced retrieval
```

### Step 3: Test and Adjust:
- Ask your typical questions
- Check if answers are complete
- Look for cut-off information
- Adjust parameters incrementally

### Step 4: Monitor Performance:
- **Incomplete answers** → Increase chunk_size or n_results
- **Too much irrelevant info** → Decrease chunk_size or n_results  
- **Lost context** → Increase chunk_overlap
- **Slow responses** → Decrease n_results or chunk_size

## 🎪 **Advanced Tips**

### Content-Specific Optimization:
- **Lists/numbered items**: Ensure chunk_size captures complete lists
- **Step-by-step procedures**: Larger chunks to keep steps together
- **Technical definitions**: Medium chunks with good overlap
- **FAQ format**: Smaller chunks for precise Q&A matching

### Query-Specific Optimization:
- **"What are the X types of Y"** → Need larger chunks + more results
- **"How do I do X"** → Medium chunks focused on procedures  
- **"What is X"** → Smaller chunks for definitions
- **Comparison questions** → More results to capture all aspects

## 🚀 **Quick Fix for Your Issue**

Your specific problem (workflow types getting cut off):

```python
# In fill_db_from_txt_files.py
chunk_size = 600      # Larger to capture complete lists
chunk_overlap = 150   # More overlap for context

# In ask_txt_data.py  
n_results = 6         # More results to ensure completeness
```

This should capture "Workflow Manager supports two types: 1. Template... 2. Third-Party..." in a single chunk!

---

💡 **Remember**: These are starting points. The best parameters depend on your specific content and use cases. Start with the recommendations, then adjust based on your results!