"""
Utilities for standardized response handling across API endpoints.
"""
import logging
from typing import Dict, Any, Optional, List, Union, Type
from fastapi import HTTPException
from fastapi.responses import JSONResponse
import os

logger = logging.getLogger(__name__)

# Get allowed origins from environment
def get_allowed_origins():
    return os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://127.0.0.1:3000,http://127.0.0.1:3001,http://127.0.0.1:3002,http://127.0.0.1:3003"
    ).split(",")

# Add CORS headers to any response
def add_cors_headers(response: JSONResponse) -> JSONResponse:
    origins = get_allowed_origins()
    
    # If the response already has CORS headers, don't modify it
    if "access-control-allow-origin" in response.headers:
        return response
    
    # Add CORS headers - use the first origin as default, or * for development
    response.headers["Access-Control-Allow-Origin"] = origins[0] if origins else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response

# Create standardized error response
def create_error_response(
    status_code: int, 
    detail: Union[str, List[Dict[str, Any]], Dict[str, Any]],
    error_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a standardized error response.
    
    Args:
        status_code: HTTP status code
        detail: Error details
        error_type: Error type
        
    Returns:
        Dictionary with standardized error format
    """
    return {
        "error": {
            "status_code": status_code,
            "type": error_type or get_error_type_from_status(status_code),
            "detail": detail
        }
    }

def get_error_type_from_status(status_code: int) -> str:
    """
    Map HTTP status code to an error type string.
    
    Args:
        status_code: HTTP status code
        
    Returns:
        String representing the error type
    """
    error_types = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        409: "conflict",
        422: "validation_error",
        429: "too_many_requests",
        500: "server_error",
        503: "service_unavailable"
    }
    
    return error_types.get(status_code, "unknown_error")

def handle_exception(
    exc: Exception, 
    default_status: int = 500,
    default_message: str = "An unexpected error occurred"
) -> HTTPException:
    """
    Convert any exception to an HTTPException with appropriate status and message.
    
    Args:
        exc: The exception to handle
        default_status: Default HTTP status code
        default_message: Default error message
        
    Returns:
        HTTPException with appropriate error details
    """
    # Handle ValueError specially
    if isinstance(exc, ValueError):
        error_message = str(exc)
        
        # Check for common patterns in error messages
        if "not found" in error_message.lower() or "does not exist" in error_message.lower():
            return HTTPException(
                status_code=404,
                detail=error_message
            )
        
        # Default for ValueError is bad request
        return HTTPException(
            status_code=400,
            detail=error_message
        )
    
    # Log unexpected exceptions
    logger.exception(f"Unhandled exception: {exc}")
    
    # Return a generic server error for unexpected exceptions
    return HTTPException(
        status_code=default_status,
        detail=default_message
    ) 