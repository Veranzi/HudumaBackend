# Troubleshooting Render Deployment

## Common 500 Error Causes

### 1. Missing Environment Variables

**Symptom**: 500 error on all endpoints, health check shows `api_key_configured: false`

**Solution**: 
- Go to Render Dashboard → Your Service → Environment
- Add `GOOGLE_API_KEY` with your API key
- Add `GEMINI_CHAT_MODEL` = `models/gemini-2.5-flash`
- Add `GEMINI_EMBED_MODEL` = `models/text-embedding-004`
- Redeploy the service

### 2. Module Import Errors

**Symptom**: 500 error, health check shows `modules_loaded: false`

**Check Render Logs**:
1. Go to Render Dashboard → Your Service → Logs
2. Look for import errors or path issues
3. Common errors:
   - `ModuleNotFoundError: No module named 'upload_file_rag'`
   - `ValueError: GOOGLE_API_KEY is not set`

**Solution**: 
- Ensure `modules/upload_file_rag.py` exists in your repository
- Check that the file structure matches:
  ```
  .
  ├── api.py
  ├── modules/
  │   └── upload_file_rag.py
  ├── requirements.txt
  └── render.yaml
  ```

### 3. Build Failures

**Symptom**: Deployment fails during build phase

**Check**:
- Render Dashboard → Your Service → Events
- Look for pip install errors

**Common Issues**:
- Missing dependencies in `requirements.txt`
- Version conflicts
- Platform-specific packages (e.g., `faiss-cpu` should work, but `faiss` might not)

**Solution**: 
- Ensure `requirements.txt` includes all dependencies
- Use `faiss-cpu` instead of `faiss` for Render compatibility
- Check that Python version matches (Render usually uses Python 3.11 or 3.12)

### 4. Path Issues

**Symptom**: Works locally but fails on Render

**Solution**: The updated `api.py` now uses absolute paths. If you still see path errors:
- Check Render logs for the actual working directory
- Verify file structure matches what's in your repo

### 5. Memory/Timeout Issues

**Symptom**: 500 error when processing large PDFs

**Solution**:
- Render free tier has limited memory
- Try smaller PDF files
- Consider upgrading to a paid plan
- Add error handling for large files

## Debugging Steps

### Step 1: Check Health Endpoint

```bash
curl https://your-service.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "api_key_configured": true,
  "modules_loaded": true
}
```

If `status` is `"degraded"`, check the other fields for issues.

### Step 2: Check Render Logs

1. Go to Render Dashboard
2. Click on your service
3. Go to "Logs" tab
4. Look for:
   - Import errors
   - Environment variable warnings
   - Startup messages
   - Error tracebacks

### Step 3: Test Locally First

Before deploying, test locally:
```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn api:app --host 0.0.0.0 --port 8000

# Test health
curl http://localhost:8000/health
```

### Step 4: Verify Environment Variables

In Render Dashboard → Environment, ensure:
- ✅ `GOOGLE_API_KEY` is set (not empty)
- ✅ `GEMINI_CHAT_MODEL` = `models/gemini-2.5-flash`
- ✅ `GEMINI_EMBED_MODEL` = `models/text-embedding-004`

## Quick Fixes

### If health check fails:
1. Check Render logs for startup errors
2. Verify `GOOGLE_API_KEY` is set in environment variables
3. Ensure `modules/upload_file_rag.py` exists in your repo

### If upload fails:
1. Check that the file is a valid PDF
2. Check Render logs for processing errors
3. Verify API key has access to Gemini models

### If query fails:
1. Ensure you uploaded a document first (have a valid session_id)
2. Check that the document was processed successfully
3. Check Render logs for query processing errors

## Getting Help

If issues persist:
1. Check Render logs for detailed error messages
2. Test the `/health` endpoint to see what's failing
3. Verify your local setup works first
4. Check that all files are committed to your repository

## Common Error Messages

### "GOOGLE_API_KEY is not set"
- **Fix**: Add `GOOGLE_API_KEY` in Render environment variables

### "ModuleNotFoundError: No module named 'upload_file_rag'"
- **Fix**: Ensure `modules/upload_file_rag.py` exists and is committed to your repo

### "404 models/gemini-2.5-flash is not found"
- **Fix**: Your API key might not have access. Check available models or use a different model

### "Failed to initialize QA system"
- **Fix**: Check Render logs for the specific error. Usually:
  - Document has no readable text (scanned PDF)
  - API key issues
  - Model access issues

