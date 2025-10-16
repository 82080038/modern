"""
Earnings API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date, timedelta
from app.database import get_db
from app.services.earnings_service import EarningsService
from app.models.earnings import EventType, EventStatus
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/earnings", tags=["Earnings"])

# Pydantic schemas
class CreateEarningsEventRequest(BaseModel):
    symbol: str
    event_type: str  # earnings, dividend, stock_split, etc.
    announcement_date: date
    company_name: Optional[str] = None
    quarter: Optional[str] = None
    fiscal_year: Optional[int] = None
    earnings_per_share: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    dividend_amount: Optional[float] = None
    dividend_currency: Optional[str] = None
    split_ratio: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None

class CreateCorporateActionRequest(BaseModel):
    symbol: str
    action_type: str  # dividend, stock_split, merger, etc.
    announcement_date: date
    company_name: Optional[str] = None
    ex_date: Optional[date] = None
    record_date: Optional[date] = None
    effective_date: Optional[date] = None
    action_data: Optional[Dict] = None
    description: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None

class CreateEarningsAlertRequest(BaseModel):
    symbol: str
    event_type: str
    days_before: int = 1
    notify_email: bool = False
    notify_in_app: bool = True

class UpdateEventStatusRequest(BaseModel):
    status: str  # upcoming, confirmed, completed, cancelled, postponed

@router.post("/event/create")
async def create_earnings_event(
    event_request: CreateEarningsEventRequest,
    db: Session = Depends(get_db)
):
    """Create earnings event"""
    try:
        # Validate event type
        valid_types = [et.value for et in EventType]
        if event_request.event_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid event type. Valid options: {valid_types}")
        
        # Convert to enum
        event_type = EventType(event_request.event_type)
        
        # Create earnings service
        earnings_service = EarningsService(db)
        
        # Create event
        result = earnings_service.create_earnings_event(
            symbol=event_request.symbol,
            event_type=event_type,
            announcement_date=event_request.announcement_date,
            company_name=event_request.company_name,
            quarter=event_request.quarter,
            fiscal_year=event_request.fiscal_year,
            earnings_per_share=event_request.earnings_per_share,
            revenue=event_request.revenue,
            net_income=event_request.net_income,
            dividend_amount=event_request.dividend_amount,
            dividend_currency=event_request.dividend_currency,
            split_ratio=event_request.split_ratio,
            description=event_request.description,
            source=event_request.source,
            source_url=event_request.source_url
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating earnings event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/corporate-action/create")
async def create_corporate_action(
    action_request: CreateCorporateActionRequest,
    db: Session = Depends(get_db)
):
    """Create corporate action"""
    try:
        # Validate action type
        valid_types = [et.value for et in EventType]
        if action_request.action_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid action type. Valid options: {valid_types}")
        
        # Convert to enum
        action_type = EventType(action_request.action_type)
        
        # Create earnings service
        earnings_service = EarningsService(db)
        
        # Create action
        result = earnings_service.create_corporate_action(
            symbol=action_request.symbol,
            action_type=action_type,
            announcement_date=action_request.announcement_date,
            company_name=action_request.company_name,
            ex_date=action_request.ex_date,
            record_date=action_request.record_date,
            effective_date=action_request.effective_date,
            action_data=action_request.action_data,
            description=action_request.description,
            source=action_request.source,
            source_url=action_request.source_url
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating corporate action: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calendar")
async def get_earnings_calendar(
    start_date: Optional[date] = Query(None, description="Start date for calendar"),
    end_date: Optional[date] = Query(None, description="End date for calendar"),
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols"),
    event_types: Optional[str] = Query(None, description="Comma-separated list of event types"),
    limit: int = Query(100, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    """Get earnings calendar"""
    try:
        # Parse symbols
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Parse event types
        event_type_list = None
        if event_types:
            event_type_strings = [et.strip() for et in event_types.split(',')]
            valid_types = [et.value for et in EventType]
            event_type_list = []
            for et in event_type_strings:
                if et in valid_types:
                    event_type_list.append(EventType(et))
        
        # Create earnings service
        earnings_service = EarningsService(db)
        
        # Get calendar
        result = earnings_service.get_earnings_calendar(
            start_date=start_date,
            end_date=end_date,
            symbols=symbol_list,
            event_types=event_type_list,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting earnings calendar: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/corporate-actions")
async def get_corporate_actions(
    start_date: Optional[date] = Query(None, description="Start date for actions"),
    end_date: Optional[date] = Query(None, description="End date for actions"),
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols"),
    action_types: Optional[str] = Query(None, description="Comma-separated list of action types"),
    limit: int = Query(100, description="Maximum number of actions to return"),
    db: Session = Depends(get_db)
):
    """Get corporate actions"""
    try:
        # Parse symbols
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Parse action types
        action_type_list = None
        if action_types:
            action_type_strings = [at.strip() for at in action_types.split(',')]
            valid_types = [et.value for et in EventType]
            action_type_list = []
            for at in action_type_strings:
                if at in valid_types:
                    action_type_list.append(EventType(at))
        
        # Create earnings service
        earnings_service = EarningsService(db)
        
        # Get actions
        result = earnings_service.get_corporate_actions(
            start_date=start_date,
            end_date=end_date,
            symbols=symbol_list,
            action_types=action_type_list,
            limit=limit
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting corporate actions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alert/create")
async def create_earnings_alert(
    alert_request: CreateEarningsAlertRequest,
    db: Session = Depends(get_db)
):
    """Create earnings alert"""
    try:
        # Validate event type
        valid_types = [et.value for et in EventType]
        if alert_request.event_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid event type. Valid options: {valid_types}")
        
        # Convert to enum
        event_type = EventType(alert_request.event_type)
        
        # Create earnings service
        earnings_service = EarningsService(db)
        
        # Create alert
        result = earnings_service.create_earnings_alert(
            symbol=alert_request.symbol,
            event_type=event_type,
            days_before=alert_request.days_before,
            notify_email=alert_request.notify_email,
            notify_in_app=alert_request.notify_in_app
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating earnings alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts/check")
async def check_earnings_alerts(db: Session = Depends(get_db)):
    """Check and trigger earnings alerts"""
    try:
        earnings_service = EarningsService(db)
        alerts = earnings_service.check_earnings_alerts()
        
        return {
            "triggered_alerts": alerts,
            "total_triggered": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Error checking earnings alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/upcoming")
async def get_upcoming_events(
    symbol: Optional[str] = Query(None, description="Symbol to filter by"),
    days_ahead: int = Query(30, description="Number of days ahead to look"),
    db: Session = Depends(get_db)
):
    """Get upcoming events"""
    try:
        earnings_service = EarningsService(db)
        result = earnings_service.get_upcoming_events(symbol=symbol, days_ahead=days_ahead)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upcoming events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{symbol}")
async def get_earnings_history(
    symbol: str,
    limit: int = Query(20, description="Maximum number of events to return"),
    db: Session = Depends(get_db)
):
    """Get earnings history for a symbol"""
    try:
        earnings_service = EarningsService(db)
        result = earnings_service.get_earnings_history(symbol, limit)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting earnings history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/event/{event_id}/status")
async def update_event_status(
    event_id: str,
    status_request: UpdateEventStatusRequest,
    db: Session = Depends(get_db)
):
    """Update event status"""
    try:
        # Validate status
        valid_statuses = [es.value for es in EventStatus]
        if status_request.status not in valid_statuses:
            raise HTTPException(status_code=400, detail=f"Invalid status. Valid options: {valid_statuses}")
        
        # Convert to enum
        status = EventStatus(status_request.status)
        
        # Create earnings service
        earnings_service = EarningsService(db)
        
        # Update status
        result = earnings_service.update_event_status(event_id, status)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating event status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/alert/{alert_id}")
async def delete_earnings_alert(
    alert_id: str,
    db: Session = Depends(get_db)
):
    """Delete earnings alert"""
    try:
        earnings_service = EarningsService(db)
        result = earnings_service.delete_earnings_alert(alert_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting earnings alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alerts")
async def list_earnings_alerts(
    symbol: Optional[str] = Query(None, description="Symbol to filter by"),
    db: Session = Depends(get_db)
):
    """List earnings alerts"""
    try:
        earnings_service = EarningsService(db)
        alerts = earnings_service.list_earnings_alerts(symbol=symbol)
        
        return {
            "alerts": alerts,
            "total_count": len(alerts)
        }
        
    except Exception as e:
        logger.error(f"Error listing earnings alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/event-types")
async def get_available_event_types(db: Session = Depends(get_db)):
    """Get available event types"""
    try:
        event_types = []
        for event_type in EventType:
            event_types.append({
                "type": event_type.value,
                "name": event_type.value.replace('_', ' ').title(),
                "description": f"{event_type.value.replace('_', ' ').title()} event"
            })
        
        return {
            "event_types": event_types,
            "total_count": len(event_types)
        }
        
    except Exception as e:
        logger.error(f"Error getting event types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status-types")
async def get_available_status_types(db: Session = Depends(get_db)):
    """Get available status types"""
    try:
        status_types = []
        for status in EventStatus:
            status_types.append({
                "status": status.value,
                "name": status.value.replace('_', ' ').title(),
                "description": f"{status.value.replace('_', ' ').title()} status"
            })
        
        return {
            "status_types": status_types,
            "total_count": len(status_types)
        }
        
    except Exception as e:
        logger.error(f"Error getting status types: {e}")
        raise HTTPException(status_code=500, detail=str(e))
