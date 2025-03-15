"""
Dashboard data endpoints for the Allervie Analytics Dashboard FastAPI backend.
"""

import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.schemas import (
    DashboardSummary, 
    FormPerformance, 
    SiteMetrics, 
    TimeSeriesPoint,
    User
)
from app.services.auth import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(user: User = Depends(get_current_user)):
    """
    Get dashboard summary data.
    
    Args:
        user: User object from token
        
    Returns:
        DashboardSummary: Dashboard summary data
    """
    logger.info(f"Getting dashboard summary for user: {user.id}")
    
    # Mock dashboard data
    return DashboardSummary(
        visitors={
            "total": 12856,
            "change": 12.3,
            "trend": "up"
        },
        pageViews={
            "total": 42123,
            "change": 8.7,
            "trend": "up"
        },
        bounceRate={
            "value": 32.4,
            "change": -2.1,
            "trend": "down"
        },
        avgSession={
            "value": "3m 42s",
            "change": 0.8,
            "trend": "up"
        },
        trafficSources=[
            {"source": "Direct", "value": 35, "color": "#0070f3"},
            {"source": "Organic Search", "value": 28, "color": "#10b981"},
            {"source": "Social Media", "value": 22, "color": "#7928ca"},
            {"source": "Referral", "value": 15, "color": "#f59e0b"}
        ]
    )

@router.get("/form-performance", response_model=FormPerformance)
async def form_performance(user: User = Depends(get_current_user)):
    """
    Get form performance data.
    
    Args:
        user: User object from token
        
    Returns:
        FormPerformance: Form performance data
    """
    logger.info(f"Getting form performance for user: {user.id}")
    
    # Mock form performance data
    return FormPerformance(
        patientForms={
            "totalSubmissions": 247,
            "completionRate": 68.5,
            "avgTimeToComplete": "2m 34s",
            "changePercentage": -8.5
        },
        sponsorForms={
            "totalSubmissions": 89,
            "completionRate": 72.3,
            "avgTimeToComplete": "3m 12s",
            "changePercentage": -8.2
        }
    )

@router.get("/site-metrics", response_model=SiteMetrics)
async def site_metrics(user: User = Depends(get_current_user)):
    """
    Get site metrics data.
    
    Args:
        user: User object from token
        
    Returns:
        SiteMetrics: Site metrics data
    """
    logger.info(f"Getting site metrics for user: {user.id}")
    
    # Mock site metrics data
    return SiteMetrics(
        conversionRate={
            "value": 7.18,
            "change": 51.6
        },
        revenue={
            "value": 34990,
            "change": -47.8
        },
        sessions={
            "value": 59734,
            "change": 53.2
        },
        engagement={
            "value": 31.3,
            "change": -45.5
        },
        bounceRate={
            "value": 44.9,
            "change": -27.4
        },
        avgOrder={
            "value": 99,
            "change": -56.6
        }
    )

@router.get("/performance-over-time", response_model=List[TimeSeriesPoint])
async def performance_over_time(user: User = Depends(get_current_user)):
    """
    Get performance time series data.
    
    Args:
        user: User object from token
        
    Returns:
        List[TimeSeriesPoint]: Time series data
    """
    logger.info(f"Getting performance time series for user: {user.id}")
    
    # Mock time series data
    return [
        {"time": "9 AM", "conversions": 0, "sessions": 120},
        {"time": "10 AM", "conversions": 5, "sessions": 240},
        {"time": "11 AM", "conversions": 12, "sessions": 380},
        {"time": "12 PM", "conversions": 25, "sessions": 520},
        {"time": "1 PM", "conversions": 35, "sessions": 650},
        {"time": "2 PM", "conversions": 48, "sessions": 700},
        {"time": "3 PM", "conversions": 62, "sessions": 830},
        {"time": "4 PM", "conversions": 75, "sessions": 950},
        {"time": "5 PM", "conversions": 82, "sessions": 1050},
        {"time": "6 PM", "conversions": 90, "sessions": 1150},
        {"time": "7 PM", "conversions": 100, "sessions": 1250}
    ]
