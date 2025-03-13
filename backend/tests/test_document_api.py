import os
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI
import tempfile

from app.main import app
from utils.database import get_db
from utils.db_verification import verify_document_persistence

# Test data
TEST_USER_ID = "default-user"

client = TestClient(app)

def test_list_documents():
    """Test listing documents via API."""
    # Call the API
    response = client.get(f"/api/documents?user_id={TEST_USER_ID}")
    
    # Verify response status code
    assert response.status_code == 200
    
    # Verify response content
    data = response.json()
    assert isinstance(data, list)

def test_upload_document():
    """Test uploading a document via API."""
    # Create a temporary PDF file
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_file.write(b"%PDF-1.5\n%Test PDF file for API testing")
        temp_file_path = temp_file.name
    
    try:
        # Prepare the file for upload
        with open(temp_file_path, "rb") as f:
            files = {"file": ("test_document.pdf", f, "application/pdf")}
            data = {"user_id": TEST_USER_ID}
            
            # Call the API
            response = client.post(
                "/api/documents/upload",
                files=files,
                data=data
            )
        
        # Verify response status code
        assert response.status_code == 200
        
        # Verify response content
        data = response.json()
        assert "document_id" in data
        assert "status" in data
        assert data["status"] == "pending"
        
        # Store document ID for later cleanup
        document_id = data["document_id"]
        
        # Test getting the document
        response = client.get(f"/api/documents/{document_id}")
        assert response.status_code == 200
        get_data = response.json()
        assert get_data["metadata"]["id"] == document_id
        
        # Clean up - delete the document
        response = client.delete(f"/api/documents/{document_id}")
        assert response.status_code == 200
        
    finally:
        # Delete the temporary file
        os.unlink(temp_file_path)

def test_get_nonexistent_document():
    """Test getting a nonexistent document."""
    # Call the API with a random UUID
    response = client.get("/api/documents/00000000-0000-0000-0000-000000000000")
    
    # Verify response status code
    assert response.status_code == 404
    
    # Verify response content
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Document not found"

def test_document_count():
    """Test getting document count."""
    # Call the API
    response = client.get(f"/api/documents/count?user_id={TEST_USER_ID}")
    
    # Verify response status code
    assert response.status_code == 200
    
    # Verify response content
    data = response.json()
    assert "count" in data
    assert isinstance(data["count"], int) 