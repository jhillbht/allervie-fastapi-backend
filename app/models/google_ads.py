from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class MetricWithChange(BaseModel):
    """Model for a metric with a percentage change."""
    value: float
    change: float


class AdsPerformanceResponse(BaseModel):
    """Response model for Google Ads performance metrics."""
    impressions: MetricWithChange
    clicks: MetricWithChange
    conversions: MetricWithChange
    cost: MetricWithChange
    clickThroughRate: MetricWithChange
    conversionRate: MetricWithChange
    costPerConversion: MetricWithChange


class Campaign(BaseModel):
    """Model for a Google Ads campaign."""
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


class AdGroup(BaseModel):
    """Model for a Google Ads ad group."""
    id: str
    name: str
    campaign_id: str
    campaign_name: str
    status: str
    impressions: float
    clicks: float
    conversions: float
    cost: float
    ctr: float
    conversion_rate: float
    costPerConversion: float


class SearchTerm(BaseModel):
    """Model for a Google Ads search term."""
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


# Mock data models
class MockAdsPerformance(BaseModel):
    """Mock data for Google Ads performance metrics."""
    impressions: Dict[str, float] = Field(default_factory=lambda: {"value": 203626, "change": 41.9})
    clicks: Dict[str, float] = Field(default_factory=lambda: {"value": 4581, "change": 26.8})
    conversions: Dict[str, float] = Field(default_factory=lambda: {"value": 104, "change": 26.5})
    cost: Dict[str, float] = Field(default_factory=lambda: {"value": 4488, "change": 41.9})
    clickThroughRate: Dict[str, float] = Field(default_factory=lambda: {"value": 2.25, "change": -16.1})
    conversionRate: Dict[str, float] = Field(default_factory=lambda: {"value": 2.28, "change": 20.1})
    costPerConversion: Dict[str, float] = Field(default_factory=lambda: {"value": 43.16, "change": 33.0})


class MockCampaign(BaseModel):
    """Mock data for a Google Ads campaign."""
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


class MockData:
    """Mock data provider for testing and fallback."""
    @staticmethod
    def get_mock_campaigns() -> List[MockCampaign]:
        """Get mock campaign data."""
        return [
            MockCampaign(
                id="c1",
                name="New Patient Acquisition",
                status="ENABLED",
                impressions=89726,
                clicks=1876,
                conversions=42,
                cost=1920.45,
                ctr=2.09,
                conversion_rate=2.24,
                costPerConversion=45.73
            ),
            MockCampaign(
                id="c2",
                name="Allergy Testing Promo",
                status="ENABLED",
                impressions=62341,
                clicks=1520,
                conversions=39,
                cost=1345.20,
                ctr=2.44,
                conversion_rate=2.57,
                costPerConversion=34.49
            ),
            MockCampaign(
                id="c3",
                name="Asthma Awareness",
                status="ENABLED",
                impressions=42184,
                clicks=954,
                conversions=18,
                cost=876.30,
                ctr=2.26,
                conversion_rate=1.89,
                costPerConversion=48.68
            ),
            MockCampaign(
                id="c4",
                name="Clinical Trials",
                status="PAUSED",
                impressions=8475,
                clicks=231,
                conversions=5,
                cost=346.05,
                ctr=2.73,
                conversion_rate=2.16,
                costPerConversion=69.21
            )
        ]
