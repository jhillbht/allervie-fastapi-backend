"""
Diagnostics endpoints for the Allervie Analytics Dashboard FastAPI backend.
"""

import os
import socket
import platform
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import HTMLResponse
from app.models.schemas import User, ApiEndpoint
from app.services.auth import get_current_user
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/endpoints", response_model=List[ApiEndpoint])
async def list_endpoints():
    """
    List all available API endpoints for testing purposes.
    
    This endpoint is intended for development/testing to see all available API 
    endpoints that can be called from the frontend.
    
    Returns:
        List[ApiEndpoint]: List of available endpoints
    """
    logger.info("Listing all available API endpoints")
    
    # Hard-coded list of endpoints for now
    # In a real implementation, we would dynamically generate this
    endpoints = [
        {
            "url": "/api/auth/login",
            "methods": ["GET"],
            "description": "Initiate the OAuth 2.0 authorization flow",
            "auth_required": False
        },
        {
            "url": "/api/auth/callback",
            "methods": ["GET"],
            "description": "Handle the OAuth 2.0 callback",
            "auth_required": False
        },
        {
            "url": "/api/auth/verify",
            "methods": ["GET"],
            "description": "Verify the user's token and return user info",
            "auth_required": True
        },
        {
            "url": "/api/auth/mock-token",
            "methods": ["GET"],
            "description": "Create a mock auth token for testing",
            "auth_required": False
        },
        {
            "url": "/api/auth/logout",
            "methods": ["GET"],
            "description": "Log the user out",
            "auth_required": False
        },
        {
            "url": "/api/dashboard/summary",
            "methods": ["GET"],
            "description": "Get dashboard summary data",
            "auth_required": True
        },
        {
            "url": "/api/dashboard/form-performance",
            "methods": ["GET"],
            "description": "Get form performance data",
            "auth_required": True
        },
        {
            "url": "/api/dashboard/site-metrics",
            "methods": ["GET"],
            "description": "Get site metrics data",
            "auth_required": True
        },
        {
            "url": "/api/dashboard/performance-over-time",
            "methods": ["GET"],
            "description": "Get performance time series data",
            "auth_required": True
        },
        {
            "url": "/api/google-ads/performance",
            "methods": ["GET"],
            "description": "Get Google Ads performance data",
            "auth_required": True
        },
        {
            "url": "/api/google-ads/test-connection",
            "methods": ["GET"],
            "description": "Test the Google Ads API connection",
            "auth_required": True
        },
        {
            "url": "/api/google-ads/use-real-ads-client",
            "methods": ["GET"],
            "description": "Set a flag to use the real Google Ads client even with a mock token",
            "auth_required": True
        },
        {
            "url": "/api/diagnostics/endpoints",
            "methods": ["GET"],
            "description": "List all available API endpoints for testing purposes",
            "auth_required": False
        },
        {
            "url": "/api/diagnostics/check-port",
            "methods": ["GET"],
            "description": "Check if a port is available for use",
            "auth_required": False
        },
        {
            "url": "/api/diagnostics/system-info",
            "methods": ["GET"],
            "description": "Get basic system information",
            "auth_required": False
        },
        {
            "url": "/health",
            "methods": ["GET"],
            "description": "Health check endpoint",
            "auth_required": False
        }
    ]
    
    return endpoints

@router.get("/check-port")
async def check_port_availability(port: int = Query(..., description="Port to check")):
    """
    Check if a port is available for use.
    
    Args:
        port: Port to check
        
    Returns:
        dict: Port availability status
    """
    if not port:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Missing required parameter: port",
                "message": "Please specify a port to check"
            }
        )
        
    try:
        # Try to create a socket and bind to the port
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            
            if result == 0:
                # Port is in use
                return {
                    "port": port,
                    "available": False,
                    "message": f"Port {port} is already in use"
                }
            else:
                # Port is available
                return {
                    "port": port,
                    "available": True,
                    "message": f"Port {port} is available"
                }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "port": port,
                "error": str(e),
                "message": f"Error checking port {port}"
            }
        )

@router.get("/system-info")
async def get_system_info():
    """
    Get basic system information.
    
    Returns:
        dict: System information
    """
    try:
        info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add network interface information if available
        try:
            if hasattr(socket, 'if_nameindex'):
                interfaces = []
                for i in socket.if_nameindex():
                    interfaces.append({
                        "index": i[0],
                        "name": i[1]
                    })
                info["network_interfaces"] = interfaces
        except:
            pass
            
        return info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "message": "Error retrieving system information"
            }
        )
