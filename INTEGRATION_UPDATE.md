# Frontend Integration Update

## 🎯 Key Change: Document Upload is Now Optional

The API now supports **two query modes**:

1. **General Q&A Mode** (No document required)
   - Users can ask questions immediately without uploading
   - Answers general questions about Kenyan Government services
   - Simply omit `session_id` in the query request

2. **Document-Based RAG Mode** (With document)
   - Upload a PDF document first
   - Queries search within the uploaded document
   - Include `session_id` in the query request

## 📝 Updated Integration Pattern

### Before (Required Document Upload):
```javascript
// ❌ Old way - required document upload
if (!sessionId) {
  alert('Please upload a document first');
  return;
}

const response = await fetch(`${API_URL}/query`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: question,
    session_id: sessionId  // Required
  })
});
```

### After (Optional Document Upload):
```javascript
// ✅ New way - document is optional
const requestBody = {
  query: question
};

// Only add session_id if document was uploaded
if (sessionId) {
  requestBody.session_id = sessionId;
}

const response = await fetch(`${API_URL}/query`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(requestBody)
});
```

## 🎨 UI/UX Changes Needed

### 1. Make Chat Section Always Visible
- **Before**: Chat section hidden until document upload
- **After**: Chat section visible from the start

### 2. Update Placeholder Text
- **Before**: "Ask a question about your document..."
- **After**: "Ask about Kenyan Government services..." or "Ask about your document or general questions..."

### 3. Update Welcome Message
- **Before**: "Upload a PDF document to start asking questions"
- **After**: "Ask me anything about Kenyan Government services, or upload a PDF for document-specific questions"

### 4. Update Upload Button Label
- **Before**: "Upload PDF Document"
- **After**: "Upload PDF Document (Optional)"

### 5. Add Helpful Tip
- Add a tip: "💡 You can ask questions immediately, or upload a PDF for document-specific answers"

## 📋 Complete Updated Example

```javascript
// Query handler - works with or without document
const handleQuery = async (question) => {
  if (!question.trim()) return;

  // Build request - session_id is optional
  const requestBody = { query: question };
  
  // Only include session_id if document was uploaded
  if (sessionId) {
    requestBody.session_id = sessionId;
  }

  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody)
  });

  const data = await response.json();
  return data.response;
};
```

## 🔄 User Flow

### Flow 1: General Q&A (No Document)
1. User opens app
2. Chat interface is immediately available
3. User asks: "How do I apply for a passport?"
4. API responds with general information
5. User can continue asking general questions

### Flow 2: Document-Based Q&A
1. User opens app
2. Chat interface is immediately available
3. User can ask general questions OR upload a document
4. User uploads PDF: "government-form.pdf"
5. User asks: "What information is needed to fill this form?"
6. API searches within the uploaded document
7. User can ask more document-specific questions
8. User can also still ask general questions (mixed mode)

### Flow 3: Mixed Mode
1. User asks general question: "How do I get a Kenyan ID?"
2. API responds with general information
3. User uploads a document
4. User asks: "What fields are required in this form?"
5. API searches the document
6. User asks: "Where can I submit this form?"
7. API responds with general information (no document context)

## ✅ Benefits

1. **Better UX**: Users can start immediately without barriers
2. **Flexible**: Supports both general and document-specific queries
3. **Seamless**: Users can switch between modes naturally
4. **No Breaking Changes**: Existing integrations still work

## 🚀 Migration Guide

If you have an existing integration:

1. **Remove document requirement check**:
   ```javascript
   // Remove this:
   if (!sessionId) {
     alert('Please upload a document first');
     return;
   }
   ```

2. **Make session_id optional**:
   ```javascript
   // Change from:
   body: JSON.stringify({ query, session_id: sessionId })
   
   // To:
   const body = { query };
   if (sessionId) body.session_id = sessionId;
   body: JSON.stringify(body)
   ```

3. **Update UI messaging**:
   - Make chat visible from start
   - Update placeholders and help text
   - Mark upload as "Optional"

4. **Test both modes**:
   - Test general Q&A without document
   - Test document-based Q&A with document
   - Test switching between modes

## 📚 Updated Files

- ✅ `frontend-example.html` - Updated to support both modes
- ✅ `FRONTEND_INTEGRATION.md` - React examples already support both modes
- ✅ `API_EXAMPLES.md` - Contains examples for both modes

Your frontend integration is now more flexible and user-friendly! 🎉

