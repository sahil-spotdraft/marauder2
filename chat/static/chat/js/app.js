/**
 * Universal RAG System - Chat Interface JavaScript
 * ===============================================
 */

class ChatApp {
    constructor() {
        this.conversationHistory = [];
        this.isDebugMode = false;
        this.isProcessing = false;
        this.userEmail = null;
        this.sessionId = null;
        this.useDbHistory = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadFromStorage();
        this.initializeUser();
    }
    
    initializeElements() {
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.chatForm = document.getElementById('chatForm');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.debugPanel = document.getElementById('debugPanel');
        this.debugContent = document.getElementById('debugContent');
        this.contextInfo = document.getElementById('contextInfo');
        this.debugText = document.getElementById('debug-text');
        
        // User setup elements
        this.userSetup = document.getElementById('userSetup');
        this.userEmailInput = document.getElementById('userEmailInput');
        this.saveEmailButton = document.getElementById('saveEmailButton');
        this.rememberEmailCheckbox = document.getElementById('rememberEmail');
        this.continueAnonymousButton = document.getElementById('continueAnonymous');
        this.userInfo = document.getElementById('userInfo');
    }
    
    bindEvents() {
        // Form submission
        if (this.chatForm) {
            this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        }
        
        // Input character count
        if (this.messageInput) {
            this.messageInput.addEventListener('input', () => this.updateCharCount());
            this.messageInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSubmit(e);
                }
            });
        }
        
        // Auto-resize textarea
        this.messageInput?.addEventListener('input', () => this.autoResizeInput());
        
        // User setup events
        if (this.saveEmailButton) {
            this.saveEmailButton.addEventListener('click', () => this.saveUserEmail());
        }
        
        if (this.continueAnonymousButton) {
            this.continueAnonymousButton.addEventListener('click', () => this.continueAnonymous());
        }
        
        if (this.userEmailInput) {
            this.userEmailInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.saveUserEmail();
                }
            });
        }
        
        // Update context info
        this.updateContextInfo();
    }
    
    initializeUser() {
        // Check if user email is saved
        const savedEmail = localStorage.getItem('userEmail');
        const rememberEmail = localStorage.getItem('rememberEmail') === 'true';
        
        if (savedEmail && rememberEmail) {
            this.userEmail = savedEmail;
            this.useDbHistory = true;
            this.sessionId = this.generateSessionId();
            this.hideUserSetup();
            this.showUserInfo();
            this.loadUserHistory();
        } else {
            this.showUserSetup();
        }
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
    }
    
    saveUserEmail() {
        const email = this.userEmailInput?.value.trim();
        const remember = this.rememberEmailCheckbox?.checked;
        
        if (!email) {
            alert('Please enter your email address');
            return;
        }
        
        if (!this.isValidEmail(email)) {
            alert('Please enter a valid email address');
            return;
        }
        
        this.userEmail = email;
        this.useDbHistory = true;
        this.sessionId = this.generateSessionId();
        
        if (remember) {
            localStorage.setItem('userEmail', email);
            localStorage.setItem('rememberEmail', 'true');
        }
        
        this.hideUserSetup();
        this.showUserInfo();
        this.loadUserHistory();
    }
    
    continueAnonymous() {
        this.userEmail = null;
        this.useDbHistory = false;
        this.sessionId = null;
        this.hideUserSetup();
        this.loadFromStorage(); // Load local storage history
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    showUserSetup() {
        if (this.userSetup) {
            this.userSetup.style.display = 'block';
        }
        if (this.chatForm) {
            this.chatForm.style.opacity = '0.5';
            this.chatForm.style.pointerEvents = 'none';
        }
    }
    
    hideUserSetup() {
        if (this.userSetup) {
            this.userSetup.style.display = 'none';
        }
        if (this.chatForm) {
            this.chatForm.style.opacity = '1';
            this.chatForm.style.pointerEvents = 'auto';
        }
    }
    
    showUserInfo() {
        if (this.userInfo && this.userEmail) {
            this.userInfo.textContent = `💾 Saved as: ${this.userEmail}`;
            this.userInfo.style.display = 'inline';
        }
    }
    
    async loadUserHistory() {
        if (!this.userEmail) return;
        
        try {
            const response = await fetch(`/user/history/?user_email=${encodeURIComponent(this.userEmail)}&limit=10`);
            const data = await response.json();
            
            if (data.success && data.history.length > 0) {
                this.conversationHistory = data.history;
                this.updateContextInfo();
                
                // Display last few exchanges in chat
                const lastExchanges = data.detailed_history.slice(-3);
                for (const exchange of lastExchanges) {
                    this.addMessage('user', exchange.user_query, { 
                        fromHistory: true,
                        timestamp: new Date(exchange.created_at)
                    });
                    this.addMessage('ai', exchange.ai_response, { 
                        fromHistory: true,
                        complexity: exchange.complexity,
                        chunks: exchange.chunks_found,
                        sources: exchange.retrieved_sources,
                        timestamp: new Date(exchange.created_at)
                    });
                }
                
                // Show welcome back message
                this.addSystemMessage(`Welcome back! Loaded ${data.history.length} previous conversations.`);
            }
        } catch (error) {
            console.warn('Could not load user history:', error);
        }
    }
    
    addSystemMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message system';
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-bubble" style="background: var(--success-color); color: white; text-align: center;">
                    <i class="fas fa-info-circle"></i> ${message}
                </div>
            </div>
        `;
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    

    
    updateCharCount() {
        const charCountElement = document.querySelector('.char-count');
        if (charCountElement && this.messageInput) {
            const count = this.messageInput.value.length;
            charCountElement.textContent = `${count}/500`;
            
            if (count > 450) {
                charCountElement.style.color = 'var(--error-color)';
            } else if (count > 400) {
                charCountElement.style.color = 'var(--warning-color)';
            } else {
                charCountElement.style.color = 'var(--text-muted)';
            }
        }
    }
    
    autoResizeInput() {
        if (this.messageInput) {
            this.messageInput.style.height = 'auto';
            this.messageInput.style.height = Math.min(this.messageInput.scrollHeight, 120) + 'px';
        }
    }
    
    updateContextInfo() {
        if (this.contextInfo) {
            const historyCount = this.conversationHistory.length;
            if (historyCount > 0) {
                this.contextInfo.textContent = `Context: ${historyCount} previous exchanges`;
                this.contextInfo.style.display = 'inline';
            } else {
                this.contextInfo.style.display = 'none';
            }
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.isProcessing) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        this.isProcessing = true;
        this.updateUI(true);
        
        // Add user message to UI
        this.addMessage('user', message);
        
        // Clear input
        this.messageInput.value = '';
        this.updateCharCount();
        this.autoResizeInput();
        
        try {
            // Send to API
            const response = await this.sendMessage(message);
            console.log(response);
            if (response.success) {
                // Add AI response to UI (same for both regular and action-detected responses)
                const aiResponse = response.response;
                this.addMessage('ai', aiResponse, {
                    complexity: response.complexity,
                    chunks: response.chunks_found,
                    sources: response.retrieved_sources,
                    action_id: response.action_id,
                    question_id: response.question_id,
                    action_detected: response.action_detected
                });
                
                // Update conversation history (only for non-DB users)
                if (!this.useDbHistory) {
                    this.conversationHistory.push([message, response.response]);
                    this.saveToStorage();
                }
                this.updateContextInfo();
                
                // Update debug panel if active
                if (this.isDebugMode) {
                    this.updateDebugPanel(response);
                }
                
            } else {
                this.addMessage('ai', `❌ Error: ${response.error}`, { isError: true });
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('ai', '❌ Failed to get response. Please check your connection and try again.', { isError: true });
        }
        
        this.isProcessing = false;
        this.updateUI(false);
    }
    
    async sendMessage(message) {
        const requestData = {
            query: message,
            user_email: this.userEmail,
            session_id: this.sessionId,
            use_db_history: this.useDbHistory
        };
        
        // Include local history if not using database
        if (!this.useDbHistory) {
            requestData.history = this.conversationHistory.slice(-3); // Send last 3 exchanges
        }
        
        const response = await fetch('/api', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    addMessage(sender, content, metadata = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'You' : 'AI';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        const bubble = document.createElement('div');
        bubble.className = 'message-bubble';
        
        if (metadata.isError) {
            bubble.style.background = 'var(--error-color)';
            bubble.style.color = 'white';
        }
        
        // Format content (basic markdown support)
        bubble.innerHTML = this.formatMessage(content);
        
        const meta = document.createElement('div');
        meta.className = 'message-meta';
        
        // Use provided timestamp or current time
        const timestamp = metadata.timestamp || new Date();
        const timeString = timestamp.toLocaleTimeString();
        
        if (sender === 'user') {
            meta.textContent = metadata.fromHistory ? 
                `${timeString} (from history)` : 
                timeString;
        } else {
            let metaText = metadata.fromHistory ? 
                `${timeString} (from history)` : 
                timeString;
            
            if (metadata.complexity) {
                metaText += ` • ${metadata.complexity} query`;
            }
            if (metadata.chunks) {
                metaText += ` • ${metadata.chunks} chunks`;
            }
            if (metadata.sources && metadata.sources.length > 0) {
                metaText += ` • from ${metadata.sources.length} files`;
            }
            meta.textContent = metaText;
        }
        
        messageContent.appendChild(bubble);
        messageContent.appendChild(meta);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessage(content) {
        // Basic markdown formatting with anchor tag support
        return content
            // Handle markdown links first [text](url)
            .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
            // Handle plain URLs (http/https)
            .replace(/(https?:\/\/[^\s<>"']+)/g, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>')
            // Handle email addresses
            .replace(/([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})/g, '<a href="mailto:$1">$1</a>')
            // Fix existing anchor tags to open in new tab if they don't already
            .replace(/<a href="([^"]+)"(?![^>]*target=)/g, '<a href="$1" target="_blank" rel="noopener noreferrer"')
            // Basic markdown formatting
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>')
            .replace(/### (.*?)(?:\n|$)/g, '<h4>$1</h4>')
            .replace(/## (.*?)(?:\n|$)/g, '<h3>$1</h3>')
            .replace(/# (.*?)(?:\n|$)/g, '<h2>$1</h2>');
    }
    
    updateUI(isLoading) {
        if (this.sendButton) {
            this.sendButton.disabled = isLoading;
            this.sendButton.innerHTML = isLoading ? 
                '<i class="fas fa-spinner fa-spin"></i>' : 
                '<i class="fas fa-paper-plane"></i>';
        }
        
        if (this.messageInput) {
            this.messageInput.disabled = isLoading;
        }
        
        if (this.typingIndicator) {
            this.typingIndicator.style.display = isLoading ? 'flex' : 'none';
        }
        
        if (isLoading) {
            this.scrollToBottom();
        }
    }
    
    scrollToBottom() {
        if (this.chatMessages) {
            setTimeout(() => {
                this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
            }, 100);
        }
    }
    
    updateDebugPanel(response) {
        if (!this.debugContent) return;
        
        const debugInfo = `
            <div class="debug-section">
                <h4>Query Analysis</h4>
                <div class="debug-info">
                    <strong>Query:</strong> ${response.query}<br>
                    <strong>Complexity:</strong> ${response.complexity}<br>
                    <strong>Chunks Found:</strong> ${response.chunks_found}
                </div>
            </div>
            
            <div class="debug-section">
                <h4>Retrieved Content</h4>
                <div class="debug-info">
                    <strong>File Types:</strong> ${JSON.stringify(response.retrieved_file_types, null, 2)}<br>
                    <strong>Content Types:</strong> ${JSON.stringify(response.retrieved_content_types, null, 2)}<br>
                    <strong>Sources:</strong> ${response.retrieved_sources.join(', ')}
                </div>
            </div>
            
            ${response.chunks_info ? `
                <div class="debug-section">
                    <h4>Chunk Details</h4>
                    <div class="debug-info">
                        ${response.chunks_info.map(chunk => `
                            <div style="margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--border-color);">
                                <strong>Chunk ${chunk.index}:</strong> ${chunk.source}<br>
                                <strong>Type:</strong> ${chunk.content_type} | <strong>Size:</strong> ${chunk.chunk_size} chars<br>
                                <strong>Preview:</strong> ${chunk.content.substring(0, 100)}...
                            </div>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
        `;
        
        this.debugContent.innerHTML = debugInfo;
    }
    
    saveToStorage() {
        try {
            localStorage.setItem('chatHistory', JSON.stringify(this.conversationHistory));
        } catch (error) {
            console.warn('Could not save chat history to localStorage:', error);
        }
    }
    
    loadFromStorage() {
        try {
            const saved = localStorage.getItem('chatHistory');
            if (saved) {
                this.conversationHistory = JSON.parse(saved);
                this.updateContextInfo();
            }
        } catch (error) {
            console.warn('Could not load chat history from localStorage:', error);
        }
    }
}

// Global functions for template
function sendSuggestion(suggestion) {
    if (window.chatApp && window.chatApp.messageInput) {
        window.chatApp.messageInput.value = suggestion;
        window.chatApp.messageInput.focus();
        window.chatApp.updateCharCount();
        window.chatApp.autoResizeInput();
    }
}

function clearConversation() {
    const message = window.chatApp?.useDbHistory ? 
        'Are you sure you want to clear the conversation history?\n\nNote: This will only clear the current display. Your chat history in the database will remain intact.' :
        'Are you sure you want to clear the conversation history?';
        
    if (confirm(message)) {
        if (window.chatApp) {
            if (!window.chatApp.useDbHistory) {
                window.chatApp.conversationHistory = [];
                window.chatApp.saveToStorage();
            }
            window.chatApp.updateContextInfo();
            
            // Clear chat messages except welcome message
            const messages = document.querySelectorAll('.message:not(.welcome-message)');
            messages.forEach(msg => msg.remove());
            
            // Show cleared message
            if (window.chatApp.useDbHistory) {
                window.chatApp.addSystemMessage('Display cleared. Your conversation history is still saved in the database.');
            }
        }
    }
}

function toggleDebug() {
    const debugPanel = document.getElementById('debugPanel');
    const debugText = document.getElementById('debug-text');
    
    if (window.chatApp) {
        window.chatApp.isDebugMode = !window.chatApp.isDebugMode;
        
        if (window.chatApp.isDebugMode) {
            debugPanel?.classList.add('active');
            if (debugText) debugText.textContent = 'Disable Debug';
        } else {
            debugPanel?.classList.remove('active');
            if (debugText) debugText.textContent = 'Enable Debug';
        }
    }
}

function downloadHistory() {
    if (window.chatApp && window.chatApp.conversationHistory.length > 0) {
        const history = window.chatApp.conversationHistory;
        const text = history.map((exchange, i) => 
            `Q${i + 1}: ${exchange[0]}\nA${i + 1}: ${exchange[1]}\n\n`
        ).join('');
        
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat-history-${new Date().toISOString().split('T')[0]}.txt`;
        a.click();
        URL.revokeObjectURL(url);
    } else {
        alert('No conversation history to export.');
    }
}

// Auto-refresh suggestions based on conversation
async function refreshSuggestions() {
    if (!window.chatApp) return;
    
    try {
        const response = await fetch(`/chat/suggestions/?history=${encodeURIComponent(JSON.stringify(window.chatApp.conversationHistory.slice(-2)))}`);
        const data = await response.json();
        
        if (data.success && data.suggestions) {
            const suggestionsList = document.querySelector('.suggestions-list');
            if (suggestionsList) {
                suggestionsList.innerHTML = data.suggestions.map(suggestion => 
                    `<button class="suggestion-btn" onclick="sendSuggestion('${suggestion.replace(/'/g, "\\'")}')">
                        ${suggestion}
                    </button>`
                ).join('');
            }
        }
    } catch (error) {
        console.warn('Could not refresh suggestions:', error);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatApp();
    
    // Refresh suggestions after each conversation
    const originalAddMessage = window.chatApp.addMessage;
    window.chatApp.addMessage = function(...args) {
        originalAddMessage.apply(this, args);
        if (args[0] === 'ai' && !args[2]?.isError) {
            setTimeout(refreshSuggestions, 1000);
        }
    };
});