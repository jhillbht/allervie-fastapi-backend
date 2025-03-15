"""
Google Ads API endpoints for the Allervie Analytics Dashboard FastAPI backend.
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.schemas import User, GoogleAdsPerformance
from app.services.auth import get_current_user
from app.services.google_ads_client import get_ads_performance_with_fallback, get_google_ads_client
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/performance", response_model=GoogleAdsPerformance)
async def ads_performance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    previous_period: bool = Query(False, description="Include previous period data for comparison"),
    user: User = Depends(get_current_user)
):
    """
    Get Google Ads performance data from the Google Ads API.
    
    This endpoint retrieves performance metrics from the Google Ads API,
    including impressions, clicks, conversions, cost, and derived metrics.
    It supports date range filtering and previous period comparison.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to yesterday)
        previous_period: Whether to include previous period data for comparison
        user: User object from token
        
    Returns:
        GoogleAdsPerformance: Performance metrics with values and percentage changes
    """
    logger.info(f"Getting Google Ads performance data for user: {user.id}")
    logger.info(f"Parameters: start_date={start_date}, end_date={end_date}, previous_period={previous_period}")
    
    try:
        # Get the performance data - only real data, no mock data or fallbacks
        performance_data = get_ads_performance_with_fallback(start_date, end_date, previous_period)
        logger.info(f"Successfully retrieved Google Ads performance data")
        
        # Return the performance data
        return GoogleAdsPerformance(**performance_data)
    except Exception as e:
        logger.error(f"Error fetching Google Ads performance data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Failed to retrieve Google Ads performance data",
                "message": str(e),
                "help": "Please verify your Google Ads API credentials and ensure the API is properly configured."
            }
        )

@router.get("/test-connection")
async def test_google_ads_connection(user: User = Depends(get_current_user)):
    """
    Test the Google Ads API connection.
    
    Args:
        user: User object from token
        
    Returns:
        dict: Connection status
    """
    logger.info(f"Testing Google Ads API connection for user: {user.id}")
    
    try:
        # Get the Google Ads client
        client = get_google_ads_client()
        
        if not client:
            return {
                'status': 'error',
                'message': 'Failed to create Google Ads client'
            }
            
        # Get customer ID from client
        customer_id = client.login_customer_id
        
        # Try a simple query to test the connection
        ga_service = client.get_service("GoogleAdsService")
        
        # Create a simple query
        query = """
            SELECT 
                customer.id
            FROM customer
            LIMIT 1
        """
        
        # Execute the query
        search_request = client.get_type("SearchGoogleAdsRequest")
        search_request.customer_id = customer_id
        search_request.query = query
        
        response = ga_service.search(request=search_request)
        
        # If we get here, the connection works
        return {
            'status': 'success',
            'message': 'Google Ads API connection successful',
            'customer_id': customer_id
        }
    except Exception as e:
        logger.error(f"Error testing Google Ads API connection: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        return {
            'status': 'error',
            'message': f'Google Ads API connection failed: {str(e)}',
            'traceback': traceback.format_exc()
        }

# Removed use-real-ads-client endpoint as we're always using real data now
