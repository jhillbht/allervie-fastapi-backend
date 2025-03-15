"""
Google Ads API client for the Allervie Analytics Dashboard FastAPI backend.
"""

import os
import logging
import yaml
from typing import Dict, Any, Optional, List, Tuple
from app.core.config import settings
import datetime

logger = logging.getLogger(__name__)

# Try to import the Google Ads API client
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_AVAILABLE = True
except ImportError:
    logger.warning("Google Ads API client not available, using mock data")
    GOOGLE_ADS_AVAILABLE = False

def get_google_ads_client() -> Optional[Any]:
    """
    Get a Google Ads API client from the google-ads.yaml configuration file.
    
    Returns:
        GoogleAdsClient: Google Ads API client or None if not available
    """
    if not GOOGLE_ADS_AVAILABLE:
        logger.warning("Google Ads API client not available")
        return None
        
    # Path to the google-ads.yaml file
    yaml_path = os.path.join(settings.CREDENTIALS_DIR, "google-ads.yaml")
    
    if not os.path.exists(yaml_path):
        logger.warning(f"Google Ads configuration file not found at {yaml_path}")
        return None
        
    try:
        # Load the client from the configuration file
        client = GoogleAdsClient.load_from_storage(yaml_path, version="v17")
        logger.info("Successfully created Google Ads client")
        return client
    except Exception as e:
        logger.error(f"Error creating Google Ads client: {str(e)}")
        return None

def get_ads_performance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    previous_period: bool = False
) -> Dict[str, Any]:
    """
    Get Google Ads performance data from the Google Ads API.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to yesterday)
        previous_period: Whether to include previous period data for comparison
        
    Returns:
        Dict[str, Any]: Performance metrics with values and percentage changes
    """
    if not GOOGLE_ADS_AVAILABLE:
        logger.error("Google Ads API client not available")
        raise Exception("Google Ads API client not available. Please install the google-ads package.")
        
    # Get the Google Ads client
    client = get_google_ads_client()
    
    if not client:
        logger.error("Google Ads client not available")
        raise Exception("Failed to create Google Ads client. Please check your credentials.")
        
    try:
        # Set default date range if not provided
        if not start_date:
            # Default to 30 days ago
            start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
            
        if not end_date:
            # Default to yesterday
            end_date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
            
        # Calculate previous period date range if requested
        if previous_period:
            # Calculate the length of the current period
            current_start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            current_end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            period_length = (current_end - current_start).days
            
            # Calculate the previous period date range
            prev_end = current_start - datetime.timedelta(days=1)
            prev_start = prev_end - datetime.timedelta(days=period_length)
            
            prev_start_str = prev_start.strftime("%Y-%m-%d")
            prev_end_str = prev_end.strftime("%Y-%m-%d")
        
        # Get customer ID from client
        customer_id = client.login_customer_id or settings.CLIENT_CUSTOMER_ID
        
        # Get Google Ads service
        ga_service = client.get_service("GoogleAdsService")
        
        # Create query for current period
        query = f"""
            SELECT 
                metrics.impressions,
                metrics.clicks,
                metrics.conversions,
                metrics.cost_micros,
                metrics.conversions_from_interactions_rate,
                metrics.ctr,
                metrics.cost_per_conversion
            FROM campaign
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
            AND campaign.status != 'REMOVED'
        """
        
        # Execute the query
        response = ga_service.search(
            customer_id=customer_id,
            query=query
        )
        
        # Process results
        impressions = 0
        clicks = 0
        conversions = 0
        cost_micros = 0
        
        # Sum metrics across all campaigns
        for row in response:
            impressions += row.metrics.impressions
            clicks += row.metrics.clicks
            conversions += row.metrics.conversions
            cost_micros += row.metrics.cost_micros
            
        # Calculate derived metrics
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        cost = cost_micros / 1000000  # Convert micros to standard currency
        cost_per_conversion = (cost / conversions) if conversions > 0 else 0
        
        # Initialize previous period metrics
        prev_impressions = 0
        prev_clicks = 0
        prev_conversions = 0
        prev_cost_micros = 0
        
        # Get previous period data if requested
        if previous_period:
            prev_query = f"""
                SELECT 
                    metrics.impressions,
                    metrics.clicks,
                    metrics.conversions,
                    metrics.cost_micros
                FROM campaign
                WHERE segments.date BETWEEN '{prev_start_str}' AND '{prev_end_str}'
                AND campaign.status != 'REMOVED'
            """
            
            prev_response = ga_service.search(
                customer_id=customer_id,
                query=prev_query
            )
            
            # Sum metrics across all campaigns for previous period
            for row in prev_response:
                prev_impressions += row.metrics.impressions
                prev_clicks += row.metrics.clicks
                prev_conversions += row.metrics.conversions
                prev_cost_micros += row.metrics.cost_micros
                
            # Calculate derived metrics for previous period
            prev_ctr = (prev_clicks / prev_impressions * 100) if prev_impressions > 0 else 0
            prev_conversion_rate = (prev_conversions / prev_clicks * 100) if prev_clicks > 0 else 0
            prev_cost = prev_cost_micros / 1000000
            prev_cost_per_conversion = (prev_cost / prev_conversions) if prev_conversions > 0 else 0
            
            # Calculate percentage changes
            impressions_change = calculate_percentage_change(impressions, prev_impressions)
            clicks_change = calculate_percentage_change(clicks, prev_clicks)
            conversions_change = calculate_percentage_change(conversions, prev_conversions)
            cost_change = calculate_percentage_change(cost, prev_cost)
            ctr_change = calculate_percentage_change(ctr, prev_ctr)
            conversion_rate_change = calculate_percentage_change(conversion_rate, prev_conversion_rate)
            cost_per_conversion_change = calculate_percentage_change(cost_per_conversion, prev_cost_per_conversion)
        else:
            # No previous period, set all changes to 0
            impressions_change = 0
            clicks_change = 0
            conversions_change = 0
            cost_change = 0
            ctr_change = 0
            conversion_rate_change = 0
            cost_per_conversion_change = 0
            
        # Format the response
        return {
            "impressions": {
                "value": int(impressions),
                "change": impressions_change
            },
            "clicks": {
                "value": int(clicks),
                "change": clicks_change
            },
            "conversions": {
                "value": int(conversions),
                "change": conversions_change
            },
            "cost": {
                "value": round(cost, 2),
                "change": cost_change
            },
            "clickThroughRate": {
                "value": round(ctr, 2),
                "change": ctr_change
            },
            "conversionRate": {
                "value": round(conversion_rate, 2),
                "change": conversion_rate_change
            },
            "costPerConversion": {
                "value": round(cost_per_conversion, 2) if conversions > 0 else 0,
                "change": cost_per_conversion_change
            }
        }
    except GoogleAdsException as e:
        logger.error(f"Google Ads API error: {e}")
        raise Exception(f"Google Ads API error: {e}")
    except Exception as e:
        logger.error(f"Error fetching Google Ads performance data: {e}")
        raise Exception(f"Error fetching Google Ads performance data: {e}")

def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        float: Percentage change (positive or negative)
    """
    if previous == 0:
        return 0
    return round(((current - previous) / previous) * 100, 2)

# Mock data function removed as we're only using real Google Ads data

def get_ads_performance_with_fallback(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    previous_period: bool = False
) -> Dict[str, Any]:
    """
    Get Google Ads performance data - no fallback as we're only using real data.
    
    Args:
        start_date: Start date in YYYY-MM-DD format (defaults to 30 days ago)
        end_date: End date in YYYY-MM-DD format (defaults to yesterday)
        previous_period: Whether to include previous period data for comparison
        
    Returns:
        Dict[str, Any]: Performance metrics with values and percentage changes
    """
    # Get real data directly - we don't use mock data anymore
    data = get_ads_performance(start_date, end_date, previous_period)
    logger.info("Successfully retrieved Google Ads performance data")
    return data
