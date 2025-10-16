"""
Economic Calendar API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date, timedelta
from app.database import get_db
from app.services.economic_calendar_service import EconomicCalendarService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/economic-calendar", tags=["Economic Calendar"])

# Pydantic schemas
class CreateEconomicAlertRequest(BaseModel):
    event_title: str
    country: str
    event_date: date
    importance: str
    alert_before_hours: int = 24
    notify_email: bool = False
    notify_in_app: bool = True

@router.get("/events")
async def get_economic_events(
    start_date: Optional[date] = Query(None, description="Start date for events"),
    end_date: Optional[date] = Query(None, description="End date for events"),
    countries: Optional[str] = Query(None, description="Comma-separated list of countries"),
    importance: Optional[str] = Query(None, description="Comma-separated list of importance levels"),
    limit: int = Query(100, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    """Get economic events with filters"""
    try:
        # Parse countries
        country_list = None
        if countries:
            country_list = [c.strip() for c in countries.split(',')]
        
        # Parse importance levels
        importance_list = None
        if importance:
            importance_list = [i.strip() for i in importance.split(',')]
        
        # Create economic calendar service
        economic_service = EconomicCalendarService(db)
        
        # Get events
        result = economic_service.get_economic_events(
            start_date=start_date,
            end_date=end_date,
            countries=country_list,
            importance=importance_list,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting economic events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/scrape")
async def scrape_economic_calendar(
    start_date: Optional[date] = Query(None, description="Start date for scraping"),
    end_date: Optional[date] = Query(None, description="End date for scraping"),
    db: Session = Depends(get_db)
):
    """Scrape economic calendar from free sources"""
    try:
        economic_service = EconomicCalendarService(db)
        result = economic_service.scrape_economic_calendar(start_date, end_date)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scraping economic calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alert/create")
async def create_economic_alert(
    alert_request: CreateEconomicAlertRequest,
    db: Session = Depends(get_db)
):
    """Create economic event alert"""
    try:
        economic_service = EconomicCalendarService(db)
        result = economic_service.create_economic_alert(
            event_title=alert_request.event_title,
            country=alert_request.country,
            event_date=alert_request.event_date,
            importance=alert_request.importance,
            alert_before_hours=alert_request.alert_before_hours,
            notify_email=alert_request.notify_email,
            notify_in_app=alert_request.notify_in_app
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating economic alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/check")
async def check_economic_alerts(db: Session = Depends(get_db)):
    """Check and trigger economic alerts"""
    try:
        economic_service = EconomicCalendarService(db)
        alerts = economic_service.check_economic_alerts()
        
        return {
            "triggered_alerts": alerts,
            "total_triggered": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Error checking economic alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/impact-analysis/{symbol}")
async def get_economic_impact_analysis(
    symbol: str,
    event_date: Optional[date] = Query(None, description="Date for impact analysis"),
    db: Session = Depends(get_db)
):
    """Get economic impact analysis for a symbol"""
    try:
        economic_service = EconomicCalendarService(db)
        result = economic_service.get_economic_impact_analysis(symbol, event_date)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting economic impact analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_economic_calendar_summary(
    start_date: Optional[date] = Query(None, description="Start date for summary"),
    end_date: Optional[date] = Query(None, description="End date for summary"),
    db: Session = Depends(get_db)
):
    """Get economic calendar summary"""
    try:
        economic_service = EconomicCalendarService(db)
        result = economic_service.get_economic_calendar_summary(start_date, end_date)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting economic calendar summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/countries")
async def get_available_countries(db: Session = Depends(get_db)):
    """Get available countries for economic events"""
    try:
        economic_service = EconomicCalendarService(db)
        countries = economic_service.get_available_countries()
        
        return {
            "countries": countries,
            "total_count": len(countries)
        }
        
    except Exception as e:
        logger.error(f"Error getting available countries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/importance-levels")
async def get_importance_levels(db: Session = Depends(get_db)):
    """Get available importance levels"""
    try:
        economic_service = EconomicCalendarService(db)
        importance_levels = economic_service.get_importance_levels()
        
        return {
            "importance_levels": importance_levels,
            "total_count": len(importance_levels)
        }
        
    except Exception as e:
        logger.error(f"Error getting importance levels: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/today")
async def get_today_events(
    countries: Optional[str] = Query(None, description="Comma-separated list of countries"),
    importance: Optional[str] = Query(None, description="Comma-separated list of importance levels"),
    db: Session = Depends(get_db)
):
    """Get today's economic events"""
    try:
        today = date.today()
        
        # Parse countries
        country_list = None
        if countries:
            country_list = [c.strip() for c in countries.split(',')]
        
        # Parse importance levels
        importance_list = None
        if importance:
            importance_list = [i.strip() for i in importance.split(',')]
        
        economic_service = EconomicCalendarService(db)
        result = economic_service.get_economic_events(
            start_date=today,
            end_date=today,
            countries=country_list,
            importance=importance_list
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting today's events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/week")
async def get_week_events(
    countries: Optional[str] = Query(None, description="Comma-separated list of countries"),
    importance: Optional[str] = Query(None, description="Comma-separated list of importance levels"),
    db: Session = Depends(get_db)
):
    """Get this week's economic events"""
    try:
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Parse countries
        country_list = None
        if countries:
            country_list = [c.strip() for c in countries.split(',')]
        
        # Parse importance levels
        importance_list = None
        if importance:
            importance_list = [i.strip() for i in importance.split(',')]
        
        economic_service = EconomicCalendarService(db)
        result = economic_service.get_economic_events(
            start_date=week_start,
            end_date=week_end,
            countries=country_list,
            importance=importance_list
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting week's events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/high-impact")
async def get_high_impact_events(
    start_date: Optional[date] = Query(None, description="Start date for events"),
    end_date: Optional[date] = Query(None, description="End date for events"),
    limit: int = Query(20, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    """Get high impact economic events"""
    try:
        economic_service = EconomicCalendarService(db)
        result = economic_service.get_economic_events(
            start_date=start_date,
            end_date=end_date,
            importance=['High'],
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting high impact events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/by-country/{country}")
async def get_events_by_country(
    country: str,
    start_date: Optional[date] = Query(None, description="Start date for events"),
    end_date: Optional[date] = Query(None, description="End date for events"),
    limit: int = Query(50, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    """Get economic events for a specific country"""
    try:
        economic_service = EconomicCalendarService(db)
        result = economic_service.get_economic_events(
            start_date=start_date,
            end_date=end_date,
            countries=[country],
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting events by country: {e}")
        raise HTTPException(status_code=500, detail=str(e))
