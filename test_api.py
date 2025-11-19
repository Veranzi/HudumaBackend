"""
Simple test script for the API
Run this after starting the API server to test endpoints
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{API_URL}/health")
    print("Health Check:", response.json())
    return response.status_code == 200

def test_upload(file_path: str):
    """Test document upload"""
    with open(file_path, 'rb') as f:
        files = {'file': (file_path.split('/')[-1], f, 'application/pdf')}
        response = requests.post(f"{API_URL}/upload", files=files)
    
    if response.status_code == 200:
        data = response.json()
        print("Upload successful:", data)
        return data['session_id']
    else:
        print("Upload failed:", response.text)
        return None

def test_query(session_id: str, query: str):
    """Test query endpoint"""
    payload = {
        "query": query,
        "session_id": session_id
    }
    response = requests.post(
        f"{API_URL}/query",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print("Query response:", data['response'])
        return data
    else:
        print("Query failed:", response.text)
        return None

if __name__ == "__main__":
    print("Testing Huduma AI API...")
    print("=" * 50)
    
    # Test health
    if not test_health():
        print("Health check failed. Is the server running?")
        exit(1)
    
    # Test upload (you need to provide a PDF file path)
    print("\nTesting upload...")
    pdf_path = input("Enter path to a PDF file (or press Enter to skip): ").strip()
    
    if pdf_path:
        session_id = test_upload(pdf_path)
        
        if session_id:
            # Test query
            print("\nTesting query...")
            query = input("Enter a question to test: ").strip()
            if query:
                test_query(session_id, query)
            
            # Clean up
            print("\nCleaning up session...")
            requests.delete(f"{API_URL}/session/{session_id}")
            print("Session deleted")
    else:
        print("Skipping upload test")

