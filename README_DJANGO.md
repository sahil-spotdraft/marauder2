# 🌐 Universal RAG System - Django Web Application

A modern, responsive web interface for the Universal RAG (Retrieval-Augmented Generation) system, built with Django and featuring real-time chat, conversation history, and intelligent document querying.

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.9+
- Ollama installed and running (`ollama serve`)
- Knowledge base created (`python fill_db.py`)

### **Installation & Setup**

1. **Install Dependencies**
   ```bash
   pip install django djangorestframework
   ```

2. **Initialize Database**
   ```bash
   python manage.py migrate
   ```

3. **Start the Server**
   ```bash
   python manage.py runserver
   ```

4. **Access the Application**
   - Open your browser to: `http://127.0.0.1:8000/`
   - The chat interface will load with your knowledge base

## 🏗️ **Architecture**

### **Project Structure**
```
rag_web/                    # Django project
├── settings.py            # Project configuration
├── urls.py               # Main URL routing
└── wsgi.py               # WSGI configuration

chat/                      # Main application
├── views.py              # Web views and API endpoints
├── urls.py               # App URL routing
├── rag_service.py        # RAG functionality service
├── templates/chat/       # HTML templates
│   └── index.html        # Main chat interface
└── static/chat/          # Static files
    ├── css/style.css     # Styles
    └── js/app.js         # JavaScript functionality

manage.py                 # Django management script
```

### **Key Components**

#### **🔧 RAG Service (`chat/rag_service.py`)**
- **Purpose**: Encapsulates all RAG functionality from `ask.py`
- **Features**: 
  - ChromaDB connection management
  - Query processing with conversation history
  - Ollama integration for AI responses
  - Knowledge base statistics and suggestions

#### **🌐 Django Views (`chat/views.py`)**
- **`home`**: Main chat interface
- **`ChatAPI`**: REST API for chat functionality  
- **`suggestions_api`**: Dynamic query suggestions
- **`health_check`**: System status monitoring
- **`debug_api`**: Development debugging tools

#### **🎨 Frontend (`templates/` & `static/`)**
- **Modern UI**: Responsive design with dark/light themes
- **Real-time Chat**: Instant messaging with typing indicators
- **Conversation History**: Persistent chat history with context
- **Debug Mode**: Developer tools for query analysis

## 🔗 **API Endpoints**

### **Main Endpoints**
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Main chat interface |
| `/api/` | POST | Send chat messages |
| `/api/` | GET | Get knowledge base info |
| `/suggestions/` | GET | Get query suggestions |
| `/health/` | GET | Health check |
| `/debug/` | POST | Debug information |

### **Chat API Usage**
```javascript
// Send a message
POST /api/
{
    "query": "What is workflow manager?",
    "history": [
        ["previous question", "previous answer"]
    ]
}

// Response
{
    "success": true,
    "query": "What is workflow manager?",
    "complexity": "simple",
    "chunks_found": 4,
    "ai_response": "Workflow Manager is...",
    "retrieved_sources": ["file1.txt", "file2.md"]
}
```

## 🎯 **Features**

### **💬 Interactive Chat Interface**
- **Real-time messaging** with instant responses
- **Conversation memory** - AI remembers context
- **Smart suggestions** based on your content
- **Character count** and input validation
- **Export functionality** for chat history

### **🧠 Intelligent RAG Integration**
- **Query complexity analysis** (simple/medium/complex/technical)
- **Adaptive retrieval** - more chunks for complex queries
- **Content-aware responses** - considers file types and content structure
- **Source attribution** - shows which files contributed to answers

### **📊 Knowledge Base Dashboard**
- **Real-time statistics** - total chunks, files, types
- **Content breakdown** by file format and content type
- **Health monitoring** with status indicators
- **Suggestion engine** with contextual recommendations

### **🔧 Developer Tools**
- **Debug mode** with detailed query analysis
- **Chunk inspection** - see what content was retrieved
- **Performance metrics** - response times and complexity
- **Error handling** with user-friendly messages

### **📱 Responsive Design**
- **Mobile-friendly** interface that works on all devices
- **Modern UI** with smooth animations and transitions
- **Accessibility** features for screen readers
- **Dark/light theme** support (auto-detected)

## ⚙️ **Configuration**

### **Django Settings (`rag_web/settings.py`)**
```python
# Key configurations
INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'rest_framework',
    'chat',  # Our RAG chat app
]

# REST API settings
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
}

# Logging for debugging
LOGGING = {
    'loggers': {
        'chat': {
            'level': 'DEBUG',
        },
    },
}
```

### **RAG Service Configuration**
The RAG service automatically connects to:
- **ChromaDB**: `chroma_db/` directory
- **Collection**: `universal_content`
- **Ollama**: `http://localhost:11434/api/generate`
- **Model**: `llama3.2`

## 🎮 **Usage Examples**

### **Basic Chat**
1. Type your question in the input field
2. Press Enter or click the send button
3. Watch the AI response appear with sources
4. Ask follow-up questions that build on context

### **Using Suggestions**
- Click any suggestion in the sidebar
- Suggestions update based on conversation context
- Get contextual follow-ups after each response

### **Debug Mode**
1. Click "Enable Debug" in the sidebar
2. Send a query to see detailed analysis
3. View chunk details, complexity analysis, and retrieval info
4. Use for development and troubleshooting

### **Export Chat History**
1. Click "Export Chat" in the sidebar
2. Downloads a text file with your conversation history
3. Includes timestamps and full context

## 🔍 **Troubleshooting**

### **Common Issues**

#### **"Knowledge Base Unavailable"**
- **Cause**: ChromaDB collection not found
- **Solution**: Run `python fill_db.py` to create knowledge base
- **Check**: Ensure `chroma_db/` directory exists

#### **"Could not connect to Ollama"**
- **Cause**: Ollama service not running
- **Solution**: Start Ollama with `ollama serve`
- **Check**: Visit `http://localhost:11434` in browser

#### **Static Files Not Loading**
- **Cause**: Static files directory missing
- **Solution**: Django will create it automatically
- **Check**: Ensure `STATICFILES_DIRS` is configured

#### **API Errors**
- **500 Error**: Check Django logs for detailed error messages
- **503 Error**: RAG service initialization failed
- **400 Error**: Invalid request format

### **Debug Commands**
```bash
# Check Django status
python manage.py check

# View Django logs
python manage.py runserver --verbosity=2

# Test RAG service manually
python -c "from chat.rag_service import RAGService; r=RAGService(); print(r.get_knowledge_base_info())"

# Health check via API
curl http://localhost:8000/health/
```

## 🚀 **Production Deployment**

### **Environment Setup**
```bash
# Install production dependencies
pip install gunicorn

# Set production settings
export DJANGO_SETTINGS_MODULE=rag_web.settings_production

# Collect static files
python manage.py collectstatic
```

### **Security Settings**
```python
# settings_production.py
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-production-secret-key'

# Add security middleware
SECURE_SSL_REDIRECT = True
SECURE_BROWSER_XSS_FILTER = True
```

### **Performance Optimization**
- **Caching**: Add Redis/Memcached for query caching
- **Database**: Use PostgreSQL for better performance
- **Static Files**: Use CDN for static file serving
- **Load Balancing**: Use multiple Ollama instances

## 📈 **Monitoring & Analytics**

### **Health Monitoring**
- **Endpoint**: `/health/` for automated monitoring
- **Metrics**: Response times, error rates, knowledge base status
- **Alerts**: Set up monitoring for Ollama and ChromaDB availability

### **Usage Analytics**
- **Query Patterns**: Most common questions and complexity
- **Performance**: Average response times and chunk retrieval
- **User Behavior**: Conversation lengths and follow-up patterns

## 🔗 **Integration Options**

### **Embed in Existing Applications**
```html
<!-- Embed chat widget -->
<iframe src="http://localhost:8000/" 
        width="100%" height="600px" 
        style="border: none; border-radius: 8px;">
</iframe>
```

### **API Integration**
```python
import requests

def query_rag(question, history=[]):
    response = requests.post('http://localhost:8000/api/', json={
        'query': question,
        'history': history
    })
    return response.json()
```

### **Webhook Integration**
```python
# Add webhook support for external notifications
# Notify Slack/Teams when queries are processed
# Log queries to external analytics systems
```

## 📚 **Related Documentation**
- [Universal RAG System](README.md) - Main system documentation
- [AI Prompts Guide](ai_prompts.py) - Prompt engineering details
- [Parameter Tuning](PARAMETER_GUIDE.md) - RAG optimization
- [Django Documentation](https://docs.djangoproject.com/) - Django framework

---

**🎉 Your Universal RAG System is now available as a modern web application!**

Access it at `http://127.0.0.1:8000/` and start chatting with your documents through an intuitive web interface.