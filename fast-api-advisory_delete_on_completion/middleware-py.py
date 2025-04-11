"""Middleware for First1KGreek FastAPI application.

This module provides middleware components for the FastAPI application.
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging with timing."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Process a request and log details with timing.
        
        Args:
            request: The incoming request
            call_next: The next middleware/route handler
            
        Returns:
            The response from the next handler
        """
        # Generate request ID (could use UUID in production)
        request_id = f"req_{int(time.time() * 1000)}"
        
        # Add request ID to request state
        request.state.request_id = request_id
        
        # Log request
        logger.info(
            f"Request {request_id}: {request.method} {request.url.path} "
            f"(Client: {request.client.host if request.client else 'unknown'})"
        )
        
        # Measure request processing time
        start_time = time.time()
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                f"Response {request_id}: {response.status_code} "
                f"(Processed in {process_time:.4f}s)"
            )
            
            # Add timing header to response
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            # Log exception
            process_time = time.time() - start_time
            logger.error(
                f"Error {request_id}: {str(e)} "
                f"(Processed in {process_time:.4f}s)"
            )
            raise
