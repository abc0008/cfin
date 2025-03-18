"""
Integration tests for standardized error handling across the API.
"""
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from utils.error_handling import StandardHTTPException, http_exception_handler


# Create a simple test app for isolated error handling tests
app = FastAPI()

# Register our custom exception handler
app.add_exception_handler(HTTPException, http_exception_handler)


class TestItem(BaseModel):
    """Test model for validation."""
    name: str = Field(..., min_length=3)
    value: int = Field(..., gt=0)


# Test endpoints that raise different errors
@app.get("/test/not-found")
async def test_not_found():
    """Test 404 error."""
    raise StandardHTTPException(
        status_code=404,
        detail="Resource not found",
        error_type="not_found"
    )


@app.get("/test/validation-error")
async def test_validation_error(item_id: int):
    """Test validation error."""
    if item_id <= 0:
        raise StandardHTTPException(
            status_code=422,
            detail=[{
                "loc": ["item_id"],
                "msg": "Value must be greater than 0",
                "type": "value_error"
            }],
            error_type="validation_error"
        )
    return {"item_id": item_id}


@app.get("/test/server-error")
async def test_server_error():
    """Test 500 error."""
    raise StandardHTTPException(
        status_code=500,
        detail="Internal server error",
        error_type="server_error"
    )


@app.get("/test/http-exception")
async def test_http_exception():
    """Test standard HTTPException conversion."""
    raise HTTPException(status_code=403, detail="Forbidden access")


# Create test client
client = TestClient(app)


class TestErrorHandling:
    """Test error handling across the API."""

    def test_not_found_error(self):
        """Test that 404 errors are properly formatted."""
        response = client.get("/test/not-found")
        assert response.status_code == 404
        data = response.json()
        assert data["status_code"] == 404
        assert data["detail"] == "Resource not found"
        assert data["error_type"] == "not_found"

    def test_validation_error(self):
        """Test that validation errors are properly formatted."""
        response = client.get("/test/validation-error?item_id=-1")
        assert response.status_code == 422
        data = response.json()
        assert data["status_code"] == 422
        assert isinstance(data["detail"], list)
        assert len(data["detail"]) == 1
        assert data["detail"][0]["loc"] == ["item_id"]
        assert "must be greater than 0" in data["detail"][0]["msg"]
        assert data["error_type"] == "validation_error"

    def test_server_error(self):
        """Test that server errors are properly formatted."""
        response = client.get("/test/server-error")
        assert response.status_code == 500
        data = response.json()
        assert data["status_code"] == 500
        assert data["detail"] == "Internal server error"
        assert data["error_type"] == "server_error"

    def test_standard_http_exception(self):
        """Test that regular HTTPExceptions are properly converted."""
        response = client.get("/test/http-exception")
        assert response.status_code == 403
        data = response.json()
        assert data["status_code"] == 403
        assert data["detail"] == "Forbidden access"
        assert data["error_type"] == "forbidden"
