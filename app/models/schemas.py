"""
Pydantic models for the Allervie Analytics Dashboard FastAPI backend.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

# Define trend enum
class TrendDirection(str, Enum):
    UP = "up"
    DOWN = "down"
    NEUTRAL = "neutral"

# Authentication models
class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    id_token: Optional[str] = None

class TokenData(BaseModel):
    user_id: Optional[str] = None

class User(BaseModel):
    id: str
    name: str
    email: str
    picture: Optional[str] = None

class UserInDB(User):
    hashed_password: Optional[str] = None

# Dashboard data models
class MetricWithTrend(BaseModel):
    value: Union[float, int, str]
    change: float
    trend: TrendDirection

class TrafficSource(BaseModel):
    source: str
    value: float
    color: str

class DashboardSummary(BaseModel):
    visitors: MetricWithTrend
    pageViews: MetricWithTrend
    bounceRate: MetricWithTrend
    avgSession: MetricWithTrend
    trafficSources: List[TrafficSource]

class FormPerformanceItem(BaseModel):
    totalSubmissions: int
    completionRate: float
    avgTimeToComplete: str
    changePercentage: float

class FormPerformance(BaseModel):
    patientForms: FormPerformanceItem
    sponsorForms: FormPerformanceItem

class MetricItem(BaseModel):
    value: Union[float, int, str]
    change: float

class SiteMetrics(BaseModel):
    conversionRate: MetricItem
    revenue: MetricItem
    sessions: MetricItem
    engagement: MetricItem
    bounceRate: MetricItem
    avgOrder: MetricItem

class TimeSeriesPoint(BaseModel):
    time: str
    conversions: int
    sessions: int

class GoogleAdsPerformance(BaseModel):
    impressions: Optional[MetricItem] = None
    clicks: Optional[MetricItem] = None
    conversions: Optional[MetricItem] = None
    cost: Optional[MetricItem] = None
    conversionRate: Optional[MetricItem] = None
    clickThroughRate: Optional[MetricItem] = None
    costPerConversion: Optional[MetricItem] = None

class HealthCheck(BaseModel):
    status: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    service: str = "Allervie Analytics API"
    environment: str
    version: str = "1.0.0"
    apiAvailable: bool = True

class ApiEndpoint(BaseModel):
    url: str
    methods: List[str]
    description: str
    auth_required: bool
