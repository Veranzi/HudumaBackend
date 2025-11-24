# Frontend Integration Guide

This guide shows how to integrate the Huduma AI API with your frontend application.

**API Base URL:** `https://hudumabackend.onrender.com`

## API Endpoints

- `POST /upload` - Upload PDF document (file upload)
- `POST /upload-url` - Upload PDF document from URL
- `POST /query` - Query uploaded document OR ask general questions (no document needed)
- `GET /health` - Health check
- `DELETE /session/{session_id}` - Delete session

---

## New Features

### 1. Upload from URL
You can now upload PDFs directly from a URL without downloading them first.

### 2. General Q&A (No Document Required)
Users can ask general questions about Kenyan Government services without uploading a document. Just omit the `session_id` in the query request.

---

## React Integration

### 1. React Component Example

```jsx
import React, { useState } from 'react';
import './HudumaAI.css';

const API_URL = 'https://hudumabackend.onrender.com';

function HudumaAI() {
  const [sessionId, setSessionId] = useState(null);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);

  // Upload PDF file
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file || !file.type.includes('pdf')) {
      alert('Please upload a PDF file');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error('Upload failed');
      }

      const data = await res.json();
      setSessionId(data.session_id);
      setMessages([{
        role: 'assistant',
        content: 'Document uploaded successfully! How may I help you?'
      }]);
      alert('Document uploaded successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload document. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  // Upload from URL
  const handleUrlUpload = async (url) => {
    if (!url || !url.startsWith('http')) {
      alert('Please enter a valid URL');
      return;
    }

    setUploading(true);
    try {
      const res = await fetch(`${API_URL}/upload-url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!res.ok) {
        throw new Error('Upload failed');
      }

      const data = await res.json();
      setSessionId(data.session_id);
      setMessages([{
        role: 'assistant',
        content: 'Document uploaded successfully from URL! How may I help you?'
      }]);
      alert('Document uploaded successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Failed to upload document from URL. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  // Query the document OR ask general questions
  const handleQuery = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      return;
    }

    setLoading(true);
    
    // Add user message
    const userMessage = { role: 'user', content: query };
    setMessages(prev => [...prev, userMessage]);
    const currentQuery = query;
    setQuery('');

    try {
      // If no sessionId, this will be a general Q&A query
      const requestBody = {
        query: currentQuery,
      };
      
      // Only add session_id if we have one (document-based query)
      if (sessionId) {
        requestBody.session_id = sessionId;
      }

      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!res.ok) {
        throw new Error('Query failed');
      }

      const data = await res.json();
      setResponse(data.response);
      
      // Add assistant response
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response
      }]);
    } catch (error) {
      console.error('Query error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.'
      }]);
    } finally {
      setLoading(false);
    }
  };

  // Reset conversation
  const handleReset = () => {
    if (sessionId) {
      fetch(`${API_URL}/session/${sessionId}`, {
        method: 'DELETE',
      });
    }
    setSessionId(null);
    setMessages([]);
    setResponse('');
  };

  return (
    <div className="huduma-ai-container">
      <div className="header">
        <h1>🇰🇪 Huduma AI</h1>
        <p>Msaada Kwa Kila Mtu, Popote Ulipo</p>
      </div>

      <div className="upload-section">
        <p style={{ marginBottom: '15px', fontSize: '14px', color: '#666' }}>
          💡 <strong>Tip:</strong> You can ask questions immediately, or upload a PDF for document-specific answers
        </p>
        <div style={{ marginBottom: '15px' }}>
          <label htmlFor="pdf-upload" className="upload-btn">
            {uploading ? 'Uploading...' : '📄 Upload PDF Document (Optional)'}
          </label>
          <input
            id="pdf-upload"
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            style={{ display: 'none' }}
          />
          <span style={{ margin: '0 10px' }}>OR</span>
          <input
            type="text"
            placeholder="Paste PDF URL here"
            id="url-input"
            style={{ padding: '10px', marginRight: '10px', borderRadius: '8px', border: '1px solid #ddd' }}
          />
          <button
            onClick={() => {
              const url = document.getElementById('url-input').value;
              handleUrlUpload(url);
            }}
            disabled={uploading}
            className="upload-btn"
          >
            Upload from URL
          </button>
        </div>
        {sessionId && (
          <button onClick={handleReset} className="reset-btn">
            🔄 Reset Document
          </button>
        )}
      </div>

      {/* Chat section is always visible - users can ask questions immediately */}
      <div className="chat-section">
        <div className="messages">
          {messages.length === 0 && (
            <div className="empty-state">
              <h3>👋 Welcome!</h3>
              <p>Ask me anything about Kenyan Government services, or upload a PDF for document-specific questions</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className="message-content">{msg.content}</div>
            </div>
          ))}
          {loading && (
            <div className="message assistant">
              <div className="message-content">Thinking...</div>
            </div>
          )}
        </div>

        <form onSubmit={handleQuery} className="query-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder={sessionId ? "Ask about your document or general questions..." : "Ask about Kenyan Government services..."}
            disabled={loading}
          />
          <button type="submit" disabled={loading || !query.trim()}>
            Send
          </button>
        </form>
      </div>
      )}
    </div>
  );
}

export default HudumaAI;
```

### 2. React with Hooks (Custom Hook)

```jsx
// useHudumaAI.js
import { useState, useCallback } from 'react';

const API_URL = 'https://hudumabackend.onrender.com';

export function useHudumaAI() {
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const uploadDocument = useCallback(async (file) => {
    if (!file || !file.type.includes('pdf')) {
      throw new Error('Please upload a PDF file');
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error('Upload failed');
      }

      const data = await res.json();
      setSessionId(data.session_id);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  const queryDocument = useCallback(async (query) => {
    if (!sessionId) {
      throw new Error('Please upload a document first');
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query,
          session_id: sessionId,
        }),
      });

      if (!res.ok) {
        throw new Error('Query failed');
      }

      const data = await res.json();
      return data.response;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [sessionId]);

  const resetSession = useCallback(async () => {
    if (sessionId) {
      try {
        await fetch(`${API_URL}/session/${sessionId}`, {
          method: 'DELETE',
        });
      } catch (err) {
        console.error('Failed to delete session:', err);
      }
    }
    setSessionId(null);
    setError(null);
  }, [sessionId]);

  return {
    sessionId,
    loading,
    error,
    uploadDocument,
    queryDocument,
    resetSession,
  };
}
```

---

## Vue.js Integration

### Vue 3 Composition API

```vue
<template>
  <div class="huduma-ai">
    <div class="header">
      <h1>🇰🇪 Huduma AI</h1>
      <p>Msaada Kwa Kila Mtu, Popote Ulipo</p>
    </div>

    <div class="upload-section">
      <label for="pdf-upload" class="upload-btn">
        {{ uploading ? 'Uploading...' : 'Upload PDF Document' }}
      </label>
      <input
        id="pdf-upload"
        type="file"
        accept=".pdf"
        @change="handleUpload"
        :disabled="uploading"
        style="display: none"
      />
      <button v-if="sessionId" @click="reset" class="reset-btn">
        Reset
      </button>
    </div>

    <div v-if="sessionId" class="chat-section">
      <div class="messages">
        <div
          v-for="(msg, idx) in messages"
          :key="idx"
          :class="['message', msg.role]"
        >
          <div class="message-content">{{ msg.content }}</div>
        </div>
        <div v-if="loading" class="message assistant">
          <div class="message-content">Thinking...</div>
        </div>
      </div>

      <form @submit.prevent="handleQuery" class="query-form">
        <input
          v-model="query"
          type="text"
          placeholder="How may I help you?"
          :disabled="loading"
        />
        <button type="submit" :disabled="loading || !query.trim()">
          Send
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const API_URL = 'https://hudumabackend.onrender.com';

const sessionId = ref(null);
const query = ref('');
const messages = ref([]);
const loading = ref(false);
const uploading = ref(false);

const handleUpload = async (event) => {
  const file = event.target.files[0];
  if (!file || !file.type.includes('pdf')) {
    alert('Please upload a PDF file');
    return;
  }

  uploading.value = true;
  const formData = new FormData();
  formData.append('file', file);

  try {
    const res = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await res.json();
    sessionId.value = data.session_id;
    messages.value = [{
      role: 'assistant',
      content: 'Document uploaded successfully! How may I help you?'
    }];
  } catch (error) {
    console.error('Upload error:', error);
    alert('Failed to upload document');
  } finally {
    uploading.value = false;
  }
};

const handleQuery = async () => {
  if (!sessionId.value || !query.value.trim()) return;

  loading.value = true;
  messages.value.push({ role: 'user', content: query.value });
  const currentQuery = query.value;
  query.value = '';

  try {
    const res = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        query: currentQuery,
        session_id: sessionId.value,
      }),
    });

    const data = await res.json();
    messages.value.push({ role: 'assistant', content: data.response });
  } catch (error) {
    console.error('Query error:', error);
    messages.value.push({
      role: 'assistant',
      content: 'Sorry, I encountered an error. Please try again.'
    });
  } finally {
    loading.value = false;
  }
};

const reset = async () => {
  if (sessionId.value) {
    await fetch(`${API_URL}/session/${sessionId.value}`, {
      method: 'DELETE',
    });
  }
  sessionId.value = null;
  messages.value = [];
};
</script>
```

---

## Vanilla JavaScript / HTML

### Complete HTML Example

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Huduma AI</title>
  <style>
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      min-height: 100vh;
      padding: 20px;
    }

    .container {
      max-width: 800px;
      margin: 0 auto;
      background: white;
      border-radius: 20px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      overflow: hidden;
    }

    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 30px;
      text-align: center;
    }

    .header h1 {
      font-size: 2.5em;
      margin-bottom: 10px;
    }

    .upload-section {
      padding: 30px;
      text-align: center;
      border-bottom: 1px solid #eee;
    }

    .upload-btn {
      display: inline-block;
      padding: 12px 30px;
      background: #667eea;
      color: white;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      transition: background 0.3s;
    }

    .upload-btn:hover {
      background: #5568d3;
    }

    #file-input {
      display: none;
    }

    .reset-btn {
      margin-left: 10px;
      padding: 12px 20px;
      background: #e74c3c;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
    }

    .chat-section {
      display: none;
      height: 500px;
      flex-direction: column;
    }

    .chat-section.active {
      display: flex;
    }

    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      background: #f8f9fa;
    }

    .message {
      margin-bottom: 15px;
      display: flex;
    }

    .message.user {
      justify-content: flex-end;
    }

    .message-content {
      max-width: 70%;
      padding: 12px 16px;
      border-radius: 12px;
      word-wrap: break-word;
    }

    .message.user .message-content {
      background: #667eea;
      color: white;
    }

    .message.assistant .message-content {
      background: white;
      color: #333;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .query-form {
      display: flex;
      padding: 20px;
      border-top: 1px solid #eee;
      background: white;
    }

    .query-form input {
      flex: 1;
      padding: 12px;
      border: 2px solid #ddd;
      border-radius: 8px;
      font-size: 16px;
    }

    .query-form button {
      margin-left: 10px;
      padding: 12px 30px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
    }

    .query-form button:disabled {
      background: #ccc;
      cursor: not-allowed;
    }

    .loading {
      text-align: center;
      padding: 20px;
      color: #667eea;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🇰🇪 Huduma AI</h1>
      <p>Msaada Kwa Kila Mtu, Popote Ulipo</p>
    </div>

    <div class="upload-section">
      <label for="file-input" class="upload-btn" id="upload-label">
        Upload PDF Document
      </label>
      <input type="file" id="file-input" accept=".pdf">
      <button id="reset-btn" class="reset-btn" style="display: none;">
        Reset
      </button>
    </div>

    <div class="chat-section" id="chat-section">
      <div class="messages" id="messages"></div>
      <form class="query-form" id="query-form">
        <input
          type="text"
          id="query-input"
          placeholder="How may I help you?"
          required
        >
        <button type="submit" id="send-btn">Send</button>
      </form>
    </div>
  </div>

  <script>
    const API_URL = 'https://hudumabackend.onrender.com';
    let sessionId = null;

    const fileInput = document.getElementById('file-input');
    const uploadLabel = document.getElementById('upload-label');
    const resetBtn = document.getElementById('reset-btn');
    const chatSection = document.getElementById('chat-section');
    const messagesDiv = document.getElementById('messages');
    const queryForm = document.getElementById('query-form');
    const queryInput = document.getElementById('query-input');
    const sendBtn = document.getElementById('send-btn');

    // Upload handler
    fileInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file || !file.type !== 'application/pdf') {
        alert('Please upload a PDF file');
        return;
      }

      uploadLabel.textContent = 'Uploading...';
      uploadLabel.style.pointerEvents = 'none';

      const formData = new FormData();
      formData.append('file', file);

      try {
        const res = await fetch(`${API_URL}/upload`, {
          method: 'POST',
          body: formData,
        });

        if (!res.ok) throw new Error('Upload failed');

        const data = await res.json();
        sessionId = data.session_id;
        
        uploadLabel.textContent = 'Upload PDF Document';
        resetBtn.style.display = 'inline-block';
        chatSection.classList.add('active');
        addMessage('assistant', 'Document uploaded successfully! How may I help you?');
      } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload document');
        uploadLabel.textContent = 'Upload PDF Document';
      } finally {
        uploadLabel.style.pointerEvents = 'auto';
      }
    });

    // Query handler
    queryForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      if (!sessionId || !queryInput.value.trim()) return;

      const query = queryInput.value;
      queryInput.value = '';
      sendBtn.disabled = true;
      sendBtn.textContent = 'Sending...';

      addMessage('user', query);

      try {
        const res = await fetch(`${API_URL}/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: query,
            session_id: sessionId,
          }),
        });

        if (!res.ok) throw new Error('Query failed');

        const data = await res.json();
        addMessage('assistant', data.response);
      } catch (error) {
        console.error('Query error:', error);
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
      } finally {
        sendBtn.disabled = false;
        sendBtn.textContent = 'Send';
      }
    });

    // Reset handler
    resetBtn.addEventListener('click', async () => {
      if (sessionId) {
        await fetch(`${API_URL}/session/${sessionId}`, {
          method: 'DELETE',
        });
      }
      sessionId = null;
      resetBtn.style.display = 'none';
      chatSection.classList.remove('active');
      messagesDiv.innerHTML = '';
      fileInput.value = '';
    });

    // Add message to chat
    function addMessage(role, content) {
      const messageDiv = document.createElement('div');
      messageDiv.className = `message ${role}`;
      messageDiv.innerHTML = `<div class="message-content">${content}</div>`;
      messagesDiv.appendChild(messageDiv);
      messagesDiv.scrollTop = messagesDiv.scrollHeight;
    }
  </script>
</body>
</html>
```

---

## Next.js Integration

### API Route (Optional - for server-side)

```typescript
// pages/api/huduma/upload.ts
import type { NextApiRequest, NextApiResponse } from 'next';

const API_URL = 'https://hudumabackend.onrender.com';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    const formData = new FormData();
    // Handle file upload from request
    // Forward to Render API
    
    const response = await fetch(`${API_URL}/upload`, {
      method: 'POST',
      body: formData,
    });

    const data = await response.json();
    res.status(200).json(data);
  } catch (error) {
    res.status(500).json({ error: 'Upload failed' });
  }
}
```

---

## TypeScript Types

```typescript
// types/huduma.ts
export interface UploadResponse {
  session_id: string;
  message: string;
  filename: string;
}

export interface QueryRequest {
  query: string;
  session_id: string;
}

export interface QueryResponse {
  response: string;
  session_id: string;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  api_key_configured: boolean;
  modules_loaded: boolean;
  module_error?: string;
}
```

---

## Error Handling Best Practices

```javascript
async function safeQuery(query, sessionId) {
  try {
    const response = await fetch(`${API_URL}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Query failed');
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError' && error.message.includes('fetch')) {
      throw new Error('Network error. Please check your connection.');
    }
    throw error;
  }
}
```

---

## CORS Configuration

The API already has CORS enabled for all origins. For production, you may want to restrict it to your domain by updating `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing Your Integration

1. **Test Health Endpoint:**
   ```javascript
   fetch('https://hudumabackend.onrender.com/health')
     .then(r => r.json())
     .then(console.log);
   ```

2. **Test Upload:**
   ```javascript
   const formData = new FormData();
   formData.append('file', pdfFile);
   fetch('https://hudumabackend.onrender.com/upload', {
     method: 'POST',
     body: formData
   }).then(r => r.json()).then(console.log);
   ```

3. **Test Query:**
   ```javascript
   fetch('https://hudumabackend.onrender.com/query', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({
       query: 'Test question',
       session_id: 'your-session-id'
     })
   }).then(r => r.json()).then(console.log);
   ```

---

## Additional Resources

- **API Documentation:** Visit `https://hudumabackend.onrender.com/docs` for interactive Swagger UI
- **Health Check:** `https://hudumabackend.onrender.com/health`
- **Source Code:** Your API code is in `api.py`

