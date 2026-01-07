class CustomerSupportChat {
    constructor() {
        this.API_BASE_URL = 'http://localhost:8000';
        this.currentSessionId = null;
        this.isTyping = false;
        
        this.initializeElements();
        this.attachEventListeners();
        this.loadExistingSession();
    }

    initializeElements() {
        // Form elements
        this.customerNameInput = document.getElementById('customerName');
        this.customerEmailInput = document.getElementById('customerEmail');
        this.issueTypeSelect = document.getElementById('issueType');
        this.startSessionBtn = document.getElementById('startSessionBtn');
        this.newSessionBtn = document.getElementById('newSessionBtn');
        
        // Chat elements
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.exportBtn = document.getElementById('exportBtn');
        
        // Info elements
        this.sessionIdText = document.getElementById('sessionIdText');
        this.messageCount = document.getElementById('messageCount');
        this.responseTime = document.getElementById('responseTime');
    }

    attachEventListeners() {
        // Session management
        this.startSessionBtn.addEventListener('click', () => this.startNewSession());
        this.newSessionBtn.addEventListener('click', () => this.resetToWelcome());
        
        // Chat input
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.clearBtn.addEventListener('click', () => this.clearChat());
        this.exportBtn.addEventListener('click', () => this.exportChat());
        
        // Quick actions
        document.querySelectorAll('.quick-btn, .hint-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const prompt = e.currentTarget.dataset.prompt;
                if (this.currentSessionId) {
                    this.messageInput.value = prompt;
                    this.sendMessage();
                } else {
                    alert('Please start a session first!');
                }
            });
        });
    }

    async loadExistingSession() {
        // Try to load session from localStorage
        const savedSession = localStorage.getItem('lastSessionId');
        if (savedSession) {
            try {
                const response = await fetch(`${this.API_BASE_URL}/api/sessions/${savedSession}`);
                if (response.ok) {
                    const data = await response.json();
                    this.currentSessionId = savedSession;
                    this.setupChat();
                    this.loadMessages(data.messages);
                }
            } catch (error) {
                console.log('No previous session found');
            }
        }
    }

    async startNewSession() {
        const customerName = this.customerNameInput.value.trim() || 'Guest';
        const email = this.customerEmailInput.value.trim();
        const issueType = this.issueTypeSelect.value;
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/sessions/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    customer_name: customerName,
                    email: email || null,
                    issue_type: issueType
                })
            });
            
            if (!response.ok) throw new Error('Failed to create session');
            
            const session = await response.json();
            this.currentSessionId = session.session_id;
            
            // Save to localStorage
            localStorage.setItem('lastSessionId', this.currentSessionId);
            
            // Update UI
            this.sessionIdText.textContent = this.currentSessionId.substring(0, 8) + '...';
            this.setupChat();
            
            // Show success message
            this.showNotification('Session started successfully!', 'success');
            
        } catch (error) {
            console.error('Error creating session:', error);
            this.showNotification('Failed to start session. Please try again.', 'error');
        }
    }

    setupChat() {
        // Hide welcome screen
        this.welcomeScreen.style.display = 'none';
        this.chatMessages.style.display = 'flex';
        
        // Enable input
        this.messageInput.disabled = false;
        this.sendBtn.disabled = false;
        this.clearBtn.disabled = false;
        this.messageInput.focus();
        
        // Update message count
        this.updateMessageCount(0);
    }

    resetToWelcome() {
        this.currentSessionId = null;
        this.welcomeScreen.style.display = 'flex';
        this.chatMessages.style.display = 'none';
        this.chatMessages.innerHTML = '';
        
        // Disable input
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
        this.clearBtn.disabled = true;
        this.messageInput.value = '';
        
        // Reset info
        this.sessionIdText.textContent = 'Not started';
        this.updateMessageCount(0);
        this.responseTime.textContent = 'Response time: --';
        
        // Clear localStorage
        localStorage.removeItem('lastSessionId');
        
        this.showNotification('Ready to start new session', 'info');
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || !this.currentSessionId) return;
        
        // Clear input
        this.messageInput.value = '';
        
        // Add user message to chat
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        const startTime = Date.now();
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    session_id: this.currentSessionId
                })
            });
            
            if (!response.ok) throw new Error('Failed to get response');
            
            const data = await response.json();
            
            // Hide typing indicator
            this.hideTypingIndicator();
            
            // Calculate response time
            const responseTime = Date.now() - startTime;
            this.responseTime.textContent = `Response time: ${responseTime}ms`;
            
            // Add assistant response
            this.addMessage('assistant', data.response);
            
            // Update message count
            this.updateMessageCount(data.messages.length);
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
            this.showNotification('Failed to send message', 'error');
        }
    }

    addMessage(role, content) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${role}`;
        
        const timestamp = new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        const avatar = role === 'user' ? 
            '<i class="fas fa-user"></i>' : 
            '<i class="fas fa-robot"></i>';
        
        const sender = role === 'user' ? 'You' : 'Support Agent';
        
        // Parse markdown for assistant messages
        const formattedContent = role === 'assistant' ? 
            marked.parse(content) : 
            content.replace(/\n/g, '<br>');
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <div class="message-avatar">${avatar}</div>
                <div class="message-sender">${sender}</div>
                <div class="message-time">${timestamp}</div>
            </div>
            <div class="message-content">${formattedContent}</div>
        `;
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }

    loadMessages(messages) {
        this.chatMessages.innerHTML = '';
        messages.forEach(msg => {
            this.addMessage(msg.role, msg.content);
        });
        this.updateMessageCount(messages.length);
        this.scrollToBottom();
    }

    showTypingIndicator() {
        if (this.isTyping) return;
        
        this.isTyping = true;
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message-typing';
        typingDiv.id = 'typingIndicator';
        typingDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas fa-robot"></i>
            </div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
            <div style="color: var(--gray-500); font-size: 0.875rem;">
                AI is typing...
            </div>
        `;
        
        this.chatMessages.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        const indicator = document.getElementById('typingIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    scrollToBottom() {
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
    }

    updateMessageCount(count) {
        this.messageCount.textContent = `Messages: ${count}`;
    }

    clearChat() {
        if (confirm('Are you sure you want to clear the chat? This will remove all messages from view.')) {
            this.chatMessages.innerHTML = '';
            this.updateMessageCount(0);
            this.showNotification('Chat cleared', 'info');
        }
    }

    async exportChat() {
        if (!this.currentSessionId) {
            this.showNotification('No active session to export', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`${this.API_BASE_URL}/api/sessions/${this.currentSessionId}`);
            if (!response.ok) throw new Error('Failed to fetch chat data');
            
            const data = await response.json();
            
            // Format chat for export
            let exportText = `TechGadgets Support Chat Export\n`;
            exportText += `Session ID: ${this.currentSessionId}\n`;
            exportText += `Customer: ${data.session_info.customer_name}\n`;
            exportText += `Date: ${new Date().toLocaleString()}\n\n`;
            exportText += `Chat History:\n${'='.repeat(50)}\n\n`;
            
            data.messages.forEach(msg => {
                const sender = msg.role === 'user' ? 'Customer' : 'Support Agent';
                const time = new Date(msg.timestamp).toLocaleTimeString();
                exportText += `[${time}] ${sender}:\n${msg.content}\n\n`;
            });
            
            // Create and download file
            const blob = new Blob([exportText], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `techgadgets-chat-${this.currentSessionId.substring(0, 8)}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            
            this.showNotification('Chat exported successfully', 'success');
            
        } catch (error) {
            console.error('Error exporting chat:', error);
            this.showNotification('Failed to export chat', 'error');
        }
    }

    showNotification(message, type = 'info') {
        // Remove existing notification
        const existingNotification = document.querySelector('.notification');
        if (existingNotification) {
            existingNotification.remove();
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 
                              type === 'error' ? 'exclamation-circle' : 
                              type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: var(--radius);
            background: ${type === 'success' ? 'var(--success-color)' :
                         type === 'error' ? 'var(--danger-color)' :
                         type === 'warning' ? 'var(--warning-color)' : 'var(--gray-600)'};
            color: white;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            z-index: 1000;
            animation: slideIn 0.3s ease;
            box-shadow: var(--shadow);
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.style.animation = 'slideOut 0.3s ease';
                setTimeout(() => notification.remove(), 300);
            }
        }, 3000);
        
        // Add slideOut animation
        if (!document.querySelector('#notification-styles')) {
            const style = document.createElement('style');
            style.id = 'notification-styles';
            style.textContent = `
                @keyframes slideOut {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(100%); opacity: 0; }
                }
            `;
            document.head.appendChild(style);
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new CustomerSupportChat();
});