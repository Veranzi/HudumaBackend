"""
FastAPI server for HuduAssist KE RAG system
Deploy this to Render to get API endpoints for your custom UI
"""
import os
import sys
import tempfile
import uuid
import requests
from pathlib import Path
from typing import Optional

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Add modules to path - use absolute path for Render compatibility
current_dir = Path(__file__).parent
modules_dir = current_dir / 'modules'
sys.path.insert(0, str(modules_dir))

# Import with error handling
try:
    from upload_file_rag import get_qa_chain, query_system
except ImportError as e:
    import traceback
    print(f"Error importing upload_file_rag: {e}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    print(f"Traceback: {traceback.format_exc()}")
    raise

app = FastAPI(
    title="HuduAssist KE API",
    description="RAG-based Q&A API for Kenyan Government information",
    version="1.0.0"
)

# CORS middleware - adjust origins for your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis in production for scalability)
sessions = {}


@app.on_event("startup")
async def startup_event():
    """Check that everything is configured correctly on startup"""
    errors = []
    
    # Check API key
    if not os.environ.get("GOOGLE_API_KEY"):
        errors.append("GOOGLE_API_KEY environment variable is not set")
    
    # Check if modules can be imported
    try:
        from upload_file_rag import get_qa_chain, query_system
    except Exception as e:
        errors.append(f"Failed to import upload_file_rag: {str(e)}")
    
    if errors:
        print("=" * 50)
        print("STARTUP ERRORS:")
        for error in errors:
            print(f"  - {error}")
        print("=" * 50)
        # Don't raise - let the app start so health check can report the issue
    else:
        print("✓ API started successfully")
        print(f"✓ GOOGLE_API_KEY configured: {bool(os.environ.get('GOOGLE_API_KEY'))}")


class QueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None  # Optional for general Q&A


class QueryResponse(BaseModel):
    response: str
    session_id: Optional[str] = None


class UploadResponse(BaseModel):
    session_id: str
    message: str
    filename: str


class UploadUrlRequest(BaseModel):
    url: str
    session_id: Optional[str] = None


class GeneralQueryRequest(BaseModel):
    query: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "HuduAssist KE API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Try to import to verify modules are available
        from upload_file_rag import get_qa_chain, query_system
        modules_ok = True
        module_error = None
    except Exception as e:
        modules_ok = False
        module_error = str(e)
    
    api_key_configured = bool(os.environ.get("GOOGLE_API_KEY"))
    
    status = "healthy" if (modules_ok and api_key_configured) else "degraded"
    
    response = {
        "status": status,
        "api_key_configured": api_key_configured,
        "modules_loaded": modules_ok
    }
    
    if module_error:
        response["module_error"] = module_error
    
    return response


@app.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """
    Upload a PDF document and initialize the QA chain
    
    Returns a session_id that should be used for subsequent queries
    """
    try:
        # Generate or use provided session ID
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Save uploaded file temporarily
        suffix = Path(file.filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name
        
        # Initialize QA chain
        qa_chain = get_qa_chain(temp_path)
        
        if qa_chain is None:
            # Clean up temp file
            os.unlink(temp_path)
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize QA system. Check server logs for details."
            )
        
        # Store session
        sessions[session_id] = {
            "qa_chain": qa_chain,
            "temp_path": temp_path,
            "filename": file.filename
        }
        
        return UploadResponse(
            session_id=session_id,
            message="Document uploaded and processed successfully",
            filename=file.filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Error processing file: {str(e)}"
        )


@app.post("/upload-url", response_model=UploadResponse)
async def upload_from_url(request: UploadUrlRequest):
    """
    Upload a PDF document from a URL and initialize the QA chain
    
    Returns a session_id that should be used for subsequent queries
    """
    try:
        # Generate or use provided session ID
        if not request.session_id:
            session_id = str(uuid.uuid4())
        else:
            session_id = request.session_id
        
        # Validate URL
        if not request.url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="Invalid URL. Must start with http:// or https://"
            )
        
        # Download the file
        try:
            response = requests.get(request.url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not request.url.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=400,
                    detail="URL does not point to a PDF file"
                )
            
            # Save to temporary file
            suffix = '.pdf'
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            filename = request.url.split('/')[-1] or 'document.pdf'
            
        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download file from URL: {str(e)}"
            )
        
        # Initialize QA chain
        qa_chain = get_qa_chain(temp_path)
        
        if qa_chain is None:
            # Clean up temp file
            os.unlink(temp_path)
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize QA system. Check server logs for details."
            )
        
        # Store session
        sessions[session_id] = {
            "qa_chain": qa_chain,
            "temp_path": temp_path,
            "filename": filename
        }
        
        return UploadResponse(
            session_id=session_id,
            message="Document uploaded and processed successfully",
            filename=filename
        )
    
    except HTTPException:
        raise
    except Exception as e:
        # Clean up temp file if it exists
        if 'temp_path' in locals():
            try:
                os.unlink(temp_path)
            except:
                pass
        raise HTTPException(
            status_code=500,
            detail=f"Error processing URL: {str(e)}"
        )


@app.post("/query", response_model=QueryResponse)
async def query_document(request: QueryRequest):
    """
    Query the uploaded document using the session_id from upload,
    OR ask a general question without document context.
    
    If session_id is provided, queries the uploaded document.
    If session_id is None, provides general Q&A about Kenyan Government services.
    """
    try:
        # If no session_id, use general Q&A mode
        if not request.session_id:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from dotenv import load_dotenv
            
            load_dotenv()
            api_key = os.environ.get("GOOGLE_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=500,
                    detail="API key not configured"
                )
            
            # Use the prompt template from upload_file_rag for general queries
            from upload_file_rag import PROMPT_TEMPLATE
            from langchain_core.prompts import PromptTemplate
            
            llm = ChatGoogleGenerativeAI(
                model=os.environ.get("GEMINI_CHAT_MODEL", "models/gemini-2.5-flash"),
                google_api_key=api_key,
                temperature=0.4,
                convert_system_message_to_human=True
            )
            
            # Format prompt for general query (no document context)
            prompt = PromptTemplate(
                template=PROMPT_TEMPLATE.replace("{context}\n\n", ""),
                input_variables=["question"]
            )
            
            prompt_text = prompt.format(question=request.query)
            raw_response = llm.invoke(prompt_text)
            
            if hasattr(raw_response, "content"):
                answer = raw_response.content
            else:
                answer = str(raw_response)
            
            return QueryResponse(
                response=f"HuduAssist  🇰🇪: {answer}",
                session_id=None
            )
        
        # Document-based query mode
        if request.session_id not in sessions:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please upload a document first, or omit session_id for general questions."
            )
        
        session = sessions[request.session_id]
        qa_chain = session["qa_chain"]
        
        # Query the system
        response = query_system(request.query, qa_chain)
        
        return QueryResponse(
            response=response,
            session_id=request.session_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing query: {str(e)}"
        )


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a session and clean up resources
    """
    if session_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )
    
    session = sessions[session_id]
    
    # Clean up temp file
    try:
        if os.path.exists(session["temp_path"]):
            os.unlink(session["temp_path"])
    except Exception as e:
        print(f"Error deleting temp file: {e}")
    
    # Remove session
    del sessions[session_id]
    
    return {
        "message": "Session deleted successfully",
        "session_id": session_id
    }


@app.get("/sessions")
async def list_sessions():
    """
    List all active sessions (for debugging)
    """
    return {
        "active_sessions": len(sessions),
        "sessions": [
            {
                "session_id": sid,
                "filename": session["filename"]
            }
            for sid, session in sessions.items()
        ]
    }


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

