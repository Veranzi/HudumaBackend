# Deployment Guide for Render

This guide will help you deploy the Huduma AI API to Render.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your Google Gemini API key
3. A GitHub repository (optional, but recommended)

## Deployment Steps

### Option 1: Deploy via Render Dashboard

1. **Create a New Web Service**
   - Go to your Render dashboard
   - Click "New +" → "Web Service"
   - Connect your GitHub repository (or use "Public Git repository" and paste your repo URL)

2. **Configure the Service**
   - **Name**: `huduma-ai-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   - Go to "Environment" tab
   - Add the following variables:
     - `GOOGLE_API_KEY`: Your Google Gemini API key
     - `GEMINI_CHAT_MODEL`: `models/gemini-2.5-flash`
     - `GEMINI_EMBED_MODEL`: `models/text-embedding-004`

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your service
   - Wait for the deployment to complete (usually 2-5 minutes)

### Option 2: Deploy via render.yaml (Recommended)

1. **Push to GitHub**
   - Ensure your code is in a GitHub repository
   - Make sure `render.yaml` is in the root directory

2. **Connect to Render**
   - Go to Render dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`

3. **Set Environment Variables**
   - In the service settings, add:
     - `GOOGLE_API_KEY`: Your Google Gemini API key
   - Other variables are set in `render.yaml`

4. **Deploy**
   - Render will automatically deploy using the configuration

## API Endpoints

Once deployed, your API will be available at:
`https://your-service-name.onrender.com`

### Available Endpoints:

- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `POST /upload` - Upload a PDF document
  ```json
  Form data:
  - file: (PDF file)
  - session_id: (optional, string)
  
  Response:
  {
    "session_id": "uuid",
    "message": "Document uploaded and processed successfully",
    "filename": "document.pdf"
  }
  ```

- `POST /query` - Query the uploaded document
  ```json
  Request body:
  {
    "query": "Your question here",
    "session_id": "uuid-from-upload"
  }
  
  Response:
  {
    "response": "Huduma AI 🇰🇪: Answer here",
    "session_id": "uuid"
  }
  ```

- `DELETE /session/{session_id}` - Delete a session
- `GET /sessions` - List all active sessions (debugging)

## Frontend Integration Example

### JavaScript/TypeScript

```typescript
const API_URL = 'https://your-service-name.onrender.com';

// Upload document
async function uploadDocument(file: File) {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  
  const data = await response.json();
  return data.session_id;
}

// Query document
async function queryDocument(sessionId: string, query: string) {
  const response = await fetch(`${API_URL}/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query: query,
      session_id: sessionId
    })
  });
  
  const data = await response.json();
  return data.response;
}
```

### React Example

```jsx
import { useState } from 'react';

function HudumaAI() {
  const [sessionId, setSessionId] = useState(null);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  
  const handleUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    const res = await fetch('https://your-service-name.onrender.com/upload', {
      method: 'POST',
      body: formData
    });
    
    const data = await res.json();
    setSessionId(data.session_id);
  };
  
  const handleQuery = async () => {
    const res = await fetch('https://your-service-name.onrender.com/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, session_id: sessionId })
    });
    
    const data = await res.json();
    setResponse(data.response);
  };
  
  return (
    <div>
      <input type="file" accept=".pdf" onChange={handleUpload} />
      <input value={query} onChange={(e) => setQuery(e.target.value)} />
      <button onClick={handleQuery}>Ask</button>
      <p>{response}</p>
    </div>
  );
}
```

## CORS Configuration

The API currently allows all origins (`allow_origins=["*"]`). For production, update `api.py` to restrict CORS to your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

1. **Build fails**: Check that all dependencies in `requirements.txt` are correct
2. **API key error**: Verify `GOOGLE_API_KEY` is set correctly in Render environment variables
3. **502 Bad Gateway**: Check Render logs for errors, ensure the service is running
4. **CORS errors**: Update CORS settings in `api.py` to match your frontend URL

## Notes

- Render free tier services spin down after 15 minutes of inactivity
- Consider upgrading to a paid plan for always-on service
- For production, consider using Redis for session storage instead of in-memory
- File uploads are stored temporarily - consider using cloud storage (S3, etc.) for production

