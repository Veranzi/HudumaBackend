"""Test script to upload PDF to the API"""
import requests
import json

API_URL = "https://hudumabackend.onrender.com"
PDF_PATH = r"C:\Users\SEPIA\Downloads\Kenya_Birth_ApplicationBirthCertificate_Form-B4.pdf"

print("Testing API upload...")
print(f"API URL: {API_URL}")
print(f"PDF Path: {PDF_PATH}")

# Test health first
print("\n1. Testing health endpoint...")
response = requests.get(f"{API_URL}/health")
print(f"Health Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Upload PDF
print("\n2. Uploading PDF...")
with open(PDF_PATH, 'rb') as f:
    files = {'file': (PDF_PATH.split('\\')[-1], f, 'application/pdf')}
    response = requests.post(f"{API_URL}/upload", files=files)

print(f"Upload Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    session_id = data['session_id']
    
    # Test query
    print("\n3. Testing query...")
    query_response = requests.post(
        f"{API_URL}/query",
        json={
            "query": "What information is needed to fill this form?",
            "session_id": session_id
        },
        headers={"Content-Type": "application/json"}
    )
    print(f"Query Status: {query_response.status_code}")
    if query_response.status_code == 200:
        print(f"Response: {json.dumps(query_response.json(), indent=2)}")
    else:
        print(f"Error: {query_response.text}")
else:
    print(f"Error: {response.text}")

