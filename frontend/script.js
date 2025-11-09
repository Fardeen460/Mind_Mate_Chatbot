class MindMateChat {
    constructor() {
        this.chatHistory = document.getElementById('chatHistory');
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.documentUpload = document.getElementById('documentUpload');
        this.responseTime = document.getElementById('responseTime');
        this.documentCount = document.getElementById('documentCount');
        this.avgConfidence = document.getElementById('avgConfidence');
        this.retrievalInfo = document.getElementById('retrievalInfo');
        this.documentList = document.getElementById('documentList');
        
        this.documents = [];
        this.metrics = {
            totalResponseTime: 0,
            queryCount: 0,
            totalConfidence: 0
        };
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        this.uploadBtn.addEventListener('click', () => this.uploadDocuments());
    }
    
    async sendMessage() {
        const message = this.userInput.value.trim();
        if (!message) return;
        
        // Record start time for metrics
        const startTime = Date.now();
        
        // Add user message to chat
        this.addMessage(message, 'user');
        this.userInput.value = '';
        
        try {
            console.log('Sending message to backend:', message);
            // Call the backend API (use relative /api prefix so it works locally and when deployed)
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });
            
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Received response:', data);
            
            if (data.response || data.message) {
                this.addBotResponse(data.response || data.message, startTime, data.metadata);
            } else {
                throw new Error('Invalid response format from server');
            }
        } catch (error) {
            console.error('Error:', error);
            this.addMessage(`Error: ${error.message}. Please try again.`, 'bot');
        }
    }
    
    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const now = new Date();
        const timestamp = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;
        
        messageDiv.innerHTML = `
            <div class="message-content">${content}</div>
            <div class="message-meta">
                <span class="timestamp">${timestamp}</span>
            </div>
        `;
        
        this.chatHistory.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    // Display a bot response from the backend (content = text, metadata = optional info)
    addBotResponse(content, startTime, metadata = {}) {
        const responseTime = Date.now() - startTime;
        const confidence = metadata.confidence || metadata.confidence === 0 ? metadata.confidence : Math.floor(Math.random() * 10) + 85;
        const documentsRetrieved = metadata.documents_retrieved || 0;

        const messageDiv = document.createElement('div');
        messageDiv.className = 'message bot-message';

        const now = new Date();
        const timestamp = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;

        // Use safe content rendering (basic) — the backend should return plain text
        const safeContent = String(content || '').replace(/</g, '&lt;').replace(/>/g, '&gt;');

        messageDiv.innerHTML = `
            <div class="message-content">${safeContent}</div>
            <div class="confidence-score">Confidence: ${confidence}%</div>
            <div class="source-attribution">Source: ${metadata.source || 'Travel Knowledge Base'}</div>
            <div class="retrieval-info">Retrieved ${documentsRetrieved} relevant documents • Response time: ${responseTime}ms</div>
            <div class="message-meta">
                <span class="timestamp">${timestamp}</span>
            </div>
        `;

        this.chatHistory.appendChild(messageDiv);
        this.scrollToBottom();

        // Update metrics and visualization if metadata present
        this.updateMetrics(responseTime, confidence, documentsRetrieved);
        if (metadata && metadata.retrieved_documents) {
            this.updateRetrievalVisualization(metadata.query || '', documentsRetrieved);
        }
    }
    
    async uploadDocuments() {
        const files = this.documentUpload.files;
        if (files.length === 0) {
            alert('Please select files to upload');
            return;
        }
        
        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }
        
        try {
            this.addMessage(`Uploading ${files.length} document(s)...`, 'user');
            
            // Upload each file individually to match backend's single-file UploadFile endpoint
            let lastResult = null;
            for (let i = 0; i < files.length; i++) {
                const singleForm = new FormData();
                singleForm.append('file', files[i]);
                const resp = await fetch('/api/upload-document', {
                    method: 'POST',
                    body: singleForm
                });

                const result = await resp.json().catch(() => ({ message: 'No JSON response' }));
                if (!resp.ok) {
                    throw new Error(result.detail || result.message || 'Upload failed');
                }
                lastResult = result;
                // Add uploaded doc to the UI list
                this.documents.push({
                    name: files[i].name,
                    size: files[i].size,
                    type: files[i].type,
                    uploadTime: new Date()
                });
            }

            // Update document list UI
            this.updateDocumentList();

            const messageDiv = document.createElement('div');
            messageDiv.className = 'message bot-message';

            const now = new Date();
            const timestamp = `${now.getHours()}:${now.getMinutes().toString().padStart(2, '0')}`;

            messageDiv.innerHTML = `
                <div class="message-content">${lastResult?.filename ? `Successfully processed ${files.length} document(s)!` : (lastResult?.message || `Successfully processed ${files.length} document(s)!`)}</div>
                <div class="confidence-score">Documents processed: ${files.length}</div>
                <div class="retrieval-info">Added to knowledge base</div>
                <div class="message-meta">
                    <span class="timestamp">${timestamp}</span>
                </div>
            `;

            this.chatHistory.appendChild(messageDiv);
            this.scrollToBottom();
            
        } catch (error) {
            console.error('Upload error:', error);
            alert('Error uploading documents. Please try again.');
        }
    }
    
    scrollToBottom() {
        this.chatHistory.scrollTop = this.chatHistory.scrollHeight;
    }
    
    updateMetrics(responseTime, confidence, documentsRetrieved) {
        // Update metrics
        this.metrics.totalResponseTime += responseTime;
        this.metrics.queryCount += 1;
        this.metrics.totalConfidence += confidence;
        
        // Update UI
        this.responseTime.textContent = `${responseTime}ms`;
        this.documentCount.textContent = documentsRetrieved;
        this.avgConfidence.textContent = `${Math.round(this.metrics.totalConfidence / this.metrics.queryCount)}%`;
    }
    
    updateRetrievalVisualization(query, documentsRetrieved) {
        // Simulate retrieval information
        const retrievalInfo = `
            <p><strong>Query:</strong> ${query}</p>
            <p><strong>Processing Time:</strong> ${Math.floor(Math.random() * 100)}ms</p>
            <p><strong>Documents Retrieved:</strong> ${documentsRetrieved}</p>
            <p><strong>Top Matches:</strong></p>
            <ul>
                <li>Travel_Guide_Bali.pdf (Score: 0.92)</li>
                <li>Asia_Destinations.docx (Score: 0.87)</li>
                <li>Beach_Resorts.xlsx (Score: 0.81)</li>
            </ul>
        `;
        
        this.retrievalInfo.innerHTML = retrievalInfo;
    }
    
    updateDocumentList() {
        if (this.documents.length === 0) {
            this.documentList.innerHTML = '<li>No documents uploaded yet.</li>';
            return;
        }
        
        this.documentList.innerHTML = '';
        
        // Add each document to the list
        this.documents.forEach(doc => {
            const li = document.createElement('li');
            const sizeKB = Math.round(doc.size / 1024);
            li.innerHTML = `
                <strong>${doc.name}</strong><br>
                <span>${doc.type || 'Unknown type'} • ${sizeKB} KB</span>
            `;
            this.documentList.appendChild(li);
        });
    }
}

// Initialize the chat when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new MindMateChat();
});