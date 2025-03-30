"""
Utilities for standardized error handling across API endpoints.
"""
import logging
from typing import Dict, Any, Optional, List, Union, Type
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
import os

from models.error import create_error_response, ValidationErrorDetail

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
    
    # Add CORS headers - use the first origin as default, or * if no origins are defined
    response.headers["Access-Control-Allow-Origin"] = origins[0] if origins else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    
    return response


def format_validation_errors(errors: List[Dict[str, Any]]) -> List[ValidationErrorDetail]:
    """
    Format validation errors into a standard structure.
    
    Args:
        errors: List of validation error dictionaries
        
    Returns:
        List of ValidationErrorDetail objects
    """
    return [
        ValidationErrorDetail(
            loc=err.get("loc", []),
            msg=err.get("msg", "Validation error"),
            type=err.get("type", "validation_error")
        )
        for err in errors
    ]


class StandardHTTPException(HTTPException):
    """
    Extended HTTP exception with standardized error response format.
    """
    def __init__(
        self, 
        status_code: int, 
        detail: Union[str, List[Dict[str, Any]], Dict[str, Any]],
        error_type: Optional[str] = None,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.error_type = error_type
        super().__init__(status_code=status_code, detail=detail, headers=headers)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    Handle HTTPException and return standardized error response.
    
    Args:
        request: FastAPI request object
        exc: HTTPException instance
        
    Returns:
        JSONResponse with standardized error format
    """
    # Get error type if available (for StandardHTTPException)
    error_type = getattr(exc, "error_type", None)
    
    # Create standard error response
    content = create_error_response(
        status_code=exc.status_code,
        detail=exc.detail,
        error_type=error_type or get_error_type_from_status(exc.status_code)
    )
    
    # Log the error (except for 404s which can be noisy)
    if exc.status_code != 404:
        logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    
    # Create the response
    response = JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers or {}
    )
    
    # Add CORS headers
    return add_cors_headers(response)


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation exceptions and return standardized error response.
    
    Args:
        request: FastAPI request object
        exc: RequestValidationError instance
        
    Returns:
        JSONResponse with standardized error format
    """
    # Convert errors to standard format
    errors = format_validation_errors(exc.errors())
    
    # Create standard error response
    content = create_error_response(
        status_code=422,
        detail=errors,
        error_type="validation_error"
    )
    
    logger.error(f"Validation error: {errors}")
    
    # Create response
    response = JSONResponse(
        status_code=422,
        content=content
    )
    
    # Add CORS headers
    return add_cors_headers(response)


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
) -> StandardHTTPException:
    """
    Convert any exception to a StandardHTTPException with appropriate status and message.
    
    Args:
        exc: The exception to handle
        default_status: Default HTTP status code
        default_message: Default error message
        
    Returns:
        StandardHTTPException with appropriate error details
    """
    # Handle ValueError specially
    if isinstance(exc, ValueError):
        error_message = str(exc)
        
        # Check for common patterns in error messages
        if "not found" in error_message.lower() or "does not exist" in error_message.lower():
            return StandardHTTPException(
                status_code=404,
                detail=error_message,
                error_type="not_found"
            )
        
        # Default for ValueError is bad request
        return StandardHTTPException(
            status_code=400,
            detail=error_message,
            error_type="bad_request"
        )
    
    # Log unexpected exceptions
    logger.exception(f"Unhandled exception: {exc}")
    
    # Return a generic server error for unexpected exceptions
    return StandardHTTPException(
        status_code=default_status,
        detail=default_message,
        error_type="server_error"
    )
