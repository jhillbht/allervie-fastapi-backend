"""
Data models for Google Ads API data.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Union


class MetricWithChange(BaseModel):
    """
    A metric with its value and percentage change from previous period.
    """
    value: float
    change: float


class AdsPerformanceData(BaseModel):
    """
    Google Ads performance data with metrics and their percentage changes.
    """
    impressions: MetricWithChange
    clicks: MetricWithChange
    conversions: MetricWithChange
    cost: MetricWithChange
    clickThroughRate: MetricWithChange
    conversionRate: MetricWithChange
    costPerConversion: MetricWithChange


class CampaignData(BaseModel):
    """
    Google Ads campaign data.
    """
    id: str
    name: str
    status: str
    impressions: float
    clicks: float
    conversions: float
    cost: float
    ctr: float
    conversion_rate: float
    costPerConversion: float


class AdGroupData(BaseModel):
    """
    Google Ads ad group data.
    """
    id: str
    name: str
    status: str
    campaign_id: str
    campaign_name: str
    impressions: float
    clicks: float
    conversions: float
    cost: float
    ctr: float
    conversion_rate: float
    costPerConversion: float


class SearchTermData(BaseModel):
    """
    Google Ads search term data.
    """
    search_term: str
    campaign_id: str
    campaign_name: str
    match_type: str
    impressions: float
    clicks: float
    conversions: float
    cost: float
    ctr: float
    conversion_rate: float
    costPerConversion: float


class UserData(BaseModel):
    """
    User data for authentication.
    """
    id: str
    name: str
    email: str
    picture: Optional[str] = None


class TokenData(BaseModel):
    """
    Token data for authentication.
    """
    access_token: str
    id_token: Optional[str] = None
    expires_in: int
