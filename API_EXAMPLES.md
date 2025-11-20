# API Usage Examples

## 1. Upload PDF from File

```bash
curl -X POST https://hudumabackend.onrender.com/upload \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Document uploaded and processed successfully",
  "filename": "document.pdf"
}
```

---

## 2. Upload PDF from URL

```bash
curl -X POST https://hudumabackend.onrender.com/upload-url \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/document.pdf"
  }'
```

**Response:**
```json
{
  "session_id": "uuid-here",
  "message": "Document uploaded and processed successfully",
  "filename": "document.pdf"
}
```

**JavaScript Example:**
```javascript
const response = await fetch('https://hudumabackend.onrender.com/upload-url', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://example.com/document.pdf'
  })
});

const data = await response.json();
console.log('Session ID:', data.session_id);
```

---

## 3. Query with Document (RAG Mode)

When you have a `session_id` from upload, queries will search the uploaded document.

```bash
curl -X POST https://hudumabackend.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What information is needed to fill this form?",
    "session_id": "your-session-id-here"
  }'
```

**JavaScript Example:**
```javascript
const response = await fetch('https://hudumabackend.onrender.com/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'What information is needed to fill this form?',
    session_id: 'your-session-id-here'
  })
});

const data = await response.json();
console.log('Response:', data.response);
```

---

## 4. General Q&A (No Document Required)

You can ask general questions about Kenyan Government services without uploading a document. Just omit the `session_id`.

```bash
curl -X POST https://hudumabackend.onrender.com/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do I apply for a passport in Kenya?"
  }'
```

**JavaScript Example:**
```javascript
// General question - no document needed
const response = await fetch('https://hudumabackend.onrender.com/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    query: 'How do I apply for a passport in Kenya?'
    // No session_id needed!
  })
});

const data = await response.json();
console.log('Response:', data.response);
```

**React Example:**
```jsx
const handleGeneralQuery = async (question) => {
  const response = await fetch('https://hudumabackend.onrender.com/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query: question
      // No session_id = general Q&A mode
    })
  });
  
  const data = await response.json();
  return data.response;
};

// Usage
const answer = await handleGeneralQuery('What are the requirements for a Kenyan ID?');
```

---

## 5. Complete Workflow Examples

### Example A: Document-Based Q&A

```javascript
// Step 1: Upload document
const uploadResponse = await fetch('https://hudumabackend.onrender.com/upload', {
  method: 'POST',
  body: formData // FormData with PDF file
});
const { session_id } = await uploadResponse.json();

// Step 2: Query the document
const queryResponse = await fetch('https://hudumabackend.onrender.com/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What is this document about?',
    session_id: session_id
  })
});
const { response } = await queryResponse.json();
console.log(response);
```

### Example B: URL-Based Upload + Query

```javascript
// Step 1: Upload from URL
const uploadResponse = await fetch('https://hudumabackend.onrender.com/upload-url', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com/government-form.pdf'
  })
});
const { session_id } = await uploadResponse.json();

// Step 2: Query
const queryResponse = await fetch('https://hudumabackend.onrender.com/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'What are the required fields?',
    session_id: session_id
  })
});
const { response } = await queryResponse.json();
```

### Example C: General Q&A Only

```javascript
// No upload needed - just ask questions
const response = await fetch('https://hudumabackend.onrender.com/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'How do I register a business in Kenya?'
    // No session_id = general Q&A
  })
});

const { response: answer } = await response.json();
console.log(answer);
```

---

## 6. Frontend Integration Pattern

Here's a pattern you can use in your frontend:

```javascript
class HudumaAIClient {
  constructor(apiUrl = 'https://hudumabackend.onrender.com') {
    this.apiUrl = apiUrl;
    this.sessionId = null;
  }

  // Upload from file
  async uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch(`${this.apiUrl}/upload`, {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    this.sessionId = data.session_id;
    return data;
  }

  // Upload from URL
  async uploadFromUrl(url) {
    const response = await fetch(`${this.apiUrl}/upload-url`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    
    const data = await response.json();
    this.sessionId = data.session_id;
    return data;
  }

  // Query (works with or without document)
  async query(question, useDocument = true) {
    const body = { query: question };
    
    // Only add session_id if we want document-based query
    if (useDocument && this.sessionId) {
      body.session_id = this.sessionId;
    }
    
    const response = await fetch(`${this.apiUrl}/query`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    
    return await response.json();
  }

  // Reset session
  async reset() {
    if (this.sessionId) {
      await fetch(`${this.apiUrl}/session/${this.sessionId}`, {
        method: 'DELETE'
      });
    }
    this.sessionId = null;
  }
}

// Usage
const client = new HudumaAIClient();

// Option 1: Upload and query document
await client.uploadFile(pdfFile);
const docAnswer = await client.query('What is this about?', true);

// Option 2: General question (no document)
const generalAnswer = await client.query('How do I get a passport?', false);

// Option 3: Upload from URL
await client.uploadFromUrl('https://example.com/form.pdf');
const urlAnswer = await client.query('What fields are required?', true);
```

---

## 7. Error Handling

```javascript
async function safeQuery(query, sessionId = null) {
  try {
    const body = { query };
    if (sessionId) body.session_id = sessionId;
    
    const response = await fetch('https://hudumabackend.onrender.com/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
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

// Usage
try {
  const result = await safeQuery('Your question', sessionId);
  console.log(result.response);
} catch (error) {
  console.error('Error:', error.message);
  // Show user-friendly error message
}
```

---

## Summary

- **With Document**: Include `session_id` in query → RAG-based answers from your document
- **Without Document**: Omit `session_id` in query → General Q&A about Kenyan Government services
- **Upload Options**: File upload OR URL upload
- **Flexible**: Users can switch between document-based and general Q&A modes

