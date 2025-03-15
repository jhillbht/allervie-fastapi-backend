"""
API routes for Google Ads data.
"""

from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.services.google_ads_client import (
    get_ads_performance_with_fallback,
    get_ads_campaigns_with_fallback,
    get_ads_ad_groups_with_fallback,
    get_ads_search_terms_with_fallback
)
from app.services.auth import get_current_active_user
from app.models.ads_models import (
    AdsPerformanceData,
    CampaignData,
    AdGroupData,
    SearchTermData,
    UserData
)

router = APIRouter(prefix="/google-ads", tags=["Google Ads"])


@router.get("/performance", response_model=AdsPerformanceData)
async def get_ads_performance(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    previous_period: bool = Query(False, description="Include data from previous period for comparison"),
    use_mock: bool = Query(False, description="Force using mock data instead of real API"),
    current_user: UserData = Depends(get_current_active_user)
) -> AdsPerformanceData:
    """
    Get Google Ads performance metrics.
    
    Retrieves key metrics from the Google Ads API, including impressions, clicks,
    conversions, and costs. Calculates derived metrics like CTR, conversion rate,
    and cost per conversion. When previous_period is True, also fetches data
    for the previous time period of the same length and calculates percentage changes.
    
    - **start_date**: Start date in YYYY-MM-DD format (defaults to 30 days ago)
    - **end_date**: End date in YYYY-MM-DD format (defaults to yesterday)
    - **previous_period**: Whether to include previous period data for comparison
    - **use_mock**: Force using mock data instead of real API
    
    Returns:
        AdsPerformanceData: Performance metrics with values and percentage changes
    """
    performance_data = get_ads_performance_with_fallback(
        start_date=start_date,
        end_date=end_date,
        previous_period=previous_period
    )
    
    return performance_data


@router.get("/campaigns", response_model=List[CampaignData])
async def get_campaigns(
    use_mock: bool = Query(False, description="Force using mock data instead of real API"),
    current_user: UserData = Depends(get_current_active_user)
) -> List[CampaignData]:
    """
    Get Google Ads campaigns.
    
    Retrieves campaign data from the Google Ads API, including campaign names,
    status, and performance metrics.
    
    - **use_mock**: Force using mock data instead of real API
    
    Returns:
        List[CampaignData]: List of campaign data
    """
    campaigns = get_ads_campaigns_with_fallback()
    return campaigns


@router.get("/ad_groups", response_model=List[AdGroupData])
async def get_ad_groups(
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    use_mock: bool = Query(False, description="Force using mock data instead of real API"),
    current_user: UserData = Depends(get_current_active_user)
) -> List[AdGroupData]:
    """
    Get Google Ads ad groups.
    
    Retrieves ad group data from the Google Ads API, including ad group names,
    status, and performance metrics. Optionally filtered by campaign ID.
    
    - **campaign_id**: Filter by campaign ID
    - **use_mock**: Force using mock data instead of real API
    
    Returns:
        List[AdGroupData]: List of ad group data
    """
    ad_groups = get_ads_ad_groups_with_fallback(campaign_id=campaign_id)
    return ad_groups


@router.get("/search_terms", response_model=List[SearchTermData])
async def get_search_terms(
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    use_mock: bool = Query(False, description="Force using mock data instead of real API"),
    current_user: UserData = Depends(get_current_active_user)
) -> List[SearchTermData]:
    """
    Get Google Ads search terms.
    
    Retrieves search term data from the Google Ads API, including search terms,
    match types, and performance metrics. Optionally filtered by campaign ID.
    
    - **campaign_id**: Filter by campaign ID
    - **use_mock**: Force using mock data instead of real API
    
    Returns:
        List[SearchTermData]: List of search term data
    """
    search_terms = get_ads_search_terms_with_fallback(campaign_id=campaign_id)
    return search_terms
