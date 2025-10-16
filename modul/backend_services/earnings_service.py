"""
Earnings Service untuk Earnings Calendar dan Corporate Actions
"""
from sqlalchemy.orm import Session
from app.models.earnings import (
    EarningsEvent, CorporateAction, EarningsAlert, EarningsCalendar, 
    EarningsNotification, EarningsAnalytics, EventType, EventStatus
)
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import logging
import json

logger = logging.getLogger(__name__)

class EarningsService:
    """Service untuk earnings operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_earnings_event(self,
                             symbol: str,
                             event_type: EventType,
                             announcement_date: date,
                             company_name: str = None,
                             quarter: str = None,
                             fiscal_year: int = None,
                             earnings_per_share: float = None,
                             revenue: float = None,
                             net_income: float = None,
                             dividend_amount: float = None,
                             dividend_currency: str = None,
                             split_ratio: str = None,
                             description: str = None,
                             source: str = None,
                             source_url: str = None) -> Dict:
        """Create earnings event"""
        try:
            # Generate unique event ID
            event_id = f"EE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create earnings event
            event = EarningsEvent(
                event_id=event_id,
                symbol=symbol.upper(),
                company_name=company_name,
                event_type=event_type,
                announcement_date=announcement_date,
                quarter=quarter,
                fiscal_year=fiscal_year,
                earnings_per_share=earnings_per_share,
                revenue=revenue,
                net_income=net_income,
                dividend_amount=dividend_amount,
                dividend_currency=dividend_currency,
                split_ratio=split_ratio,
                description=description,
                source=source,
                source_url=source_url
            )
            
            self.db.add(event)
            self.db.commit()
            
            return {
                "event_id": event_id,
                "symbol": symbol.upper(),
                "event_type": event_type.value,
                "status": "created",
                "message": "Earnings event created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating earnings event: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def create_corporate_action(self,
                               symbol: str,
                               action_type: EventType,
                               announcement_date: date,
                               company_name: str = None,
                               ex_date: date = None,
                               record_date: date = None,
                               effective_date: date = None,
                               action_data: Dict = None,
                               description: str = None,
                               source: str = None,
                               source_url: str = None) -> Dict:
        """Create corporate action"""
        try:
            # Generate unique action ID
            action_id = f"CA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create corporate action
            action = CorporateAction(
                action_id=action_id,
                symbol=symbol.upper(),
                company_name=company_name,
                action_type=action_type,
                announcement_date=announcement_date,
                ex_date=ex_date,
                record_date=record_date,
                effective_date=effective_date,
                action_data=action_data,
                description=description,
                source=source,
                source_url=source_url
            )
            
            self.db.add(action)
            self.db.commit()
            
            return {
                "action_id": action_id,
                "symbol": symbol.upper(),
                "action_type": action_type.value,
                "status": "created",
                "message": "Corporate action created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating corporate action: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_earnings_calendar(self,
                             start_date: date = None,
                             end_date: date = None,
                             symbols: List[str] = None,
                             event_types: List[EventType] = None,
                             limit: int = 100) -> Dict:
        """Get earnings calendar"""
        try:
            # Set default date range
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Build query
            query = self.db.query(EarningsEvent).filter(
                EarningsEvent.announcement_date >= start_date,
                EarningsEvent.announcement_date <= end_date
            )
            
            # Filter by symbols
            if symbols:
                query = query.filter(EarningsEvent.symbol.in_([s.upper() for s in symbols]))
            
            # Filter by event types
            if event_types:
                query = query.filter(EarningsEvent.event_type.in_(event_types))
            
            # Get events
            events = query.order_by(EarningsEvent.announcement_date).limit(limit).all()
            
            # Format events
            events_data = []
            for event in events:
                event_data = {
                    "event_id": event.event_id,
                    "symbol": event.symbol,
                    "company_name": event.company_name,
                    "event_type": event.event_type.value,
                    "announcement_date": event.announcement_date.isoformat(),
                    "ex_date": event.ex_date.isoformat() if event.ex_date else None,
                    "record_date": event.record_date.isoformat() if event.record_date else None,
                    "payment_date": event.payment_date.isoformat() if event.payment_date else None,
                    "event_status": event.event_status.value,
                    "description": event.description,
                    "quarter": event.quarter,
                    "fiscal_year": event.fiscal_year,
                    "earnings_per_share": event.earnings_per_share,
                    "revenue": event.revenue,
                    "net_income": event.net_income,
                    "dividend_amount": event.dividend_amount,
                    "dividend_currency": event.dividend_currency,
                    "split_ratio": event.split_ratio,
                    "is_confirmed": event.is_confirmed,
                    "is_estimated": event.is_estimated,
                    "source": event.source,
                    "source_url": event.source_url
                }
                events_data.append(event_data)
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_events": len(events_data),
                "events": events_data
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings calendar: {e}")
            return {"error": str(e)}
    
    def get_corporate_actions(self,
                             start_date: date = None,
                             end_date: date = None,
                             symbols: List[str] = None,
                             action_types: List[EventType] = None,
                             limit: int = 100) -> Dict:
        """Get corporate actions"""
        try:
            # Set default date range
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Build query
            query = self.db.query(CorporateAction).filter(
                CorporateAction.announcement_date >= start_date,
                CorporateAction.announcement_date <= end_date
            )
            
            # Filter by symbols
            if symbols:
                query = query.filter(CorporateAction.symbol.in_([s.upper() for s in symbols]))
            
            # Filter by action types
            if action_types:
                query = query.filter(CorporateAction.action_type.in_(action_types))
            
            # Get actions
            actions = query.order_by(CorporateAction.announcement_date).limit(limit).all()
            
            # Format actions
            actions_data = []
            for action in actions:
                action_data = {
                    "action_id": action.action_id,
                    "symbol": action.symbol,
                    "company_name": action.company_name,
                    "action_type": action.action_type.value,
                    "announcement_date": action.announcement_date.isoformat(),
                    "ex_date": action.ex_date.isoformat() if action.ex_date else None,
                    "record_date": action.record_date.isoformat() if action.record_date else None,
                    "effective_date": action.effective_date.isoformat() if action.effective_date else None,
                    "action_status": action.action_status.value,
                    "description": action.description,
                    "action_data": action.action_data,
                    "impact_on_price": action.impact_on_price,
                    "impact_magnitude": action.impact_magnitude,
                    "is_confirmed": action.is_confirmed,
                    "is_estimated": action.is_estimated,
                    "source": action.source,
                    "source_url": action.source_url
                }
                actions_data.append(action_data)
            
            return {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "total_actions": len(actions_data),
                "actions": actions_data
            }
            
        except Exception as e:
            logger.error(f"Error getting corporate actions: {e}")
            return {"error": str(e)}
    
    def create_earnings_alert(self,
                             symbol: str,
                             event_type: EventType,
                             days_before: int = 1,
                             notify_email: bool = False,
                             notify_in_app: bool = True) -> Dict:
        """Create earnings alert"""
        try:
            # Generate unique alert ID
            alert_id = f"EA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create alert
            alert = EarningsAlert(
                alert_id=alert_id,
                symbol=symbol.upper(),
                event_type=event_type,
                days_before=days_before,
                notify_email=notify_email,
                notify_in_app=notify_in_app
            )
            
            self.db.add(alert)
            self.db.commit()
            
            return {
                "alert_id": alert_id,
                "symbol": symbol.upper(),
                "event_type": event_type.value,
                "status": "created",
                "message": "Earnings alert created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating earnings alert: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def check_earnings_alerts(self) -> List[Dict]:
        """Check and trigger earnings alerts"""
        try:
            # Get active alerts
            alerts = self.db.query(EarningsAlert).filter(EarningsAlert.is_active == True).all()
            
            triggered_alerts = []
            
            for alert in alerts:
                # Calculate alert date
                alert_date = date.today() + timedelta(days=alert.days_before)
                
                # Find events for this symbol and date
                events = self.db.query(EarningsEvent).filter(
                    EarningsEvent.symbol == alert.symbol,
                    EarningsEvent.event_type == alert.event_type,
                    EarningsEvent.announcement_date == alert_date
                ).all()
                
                for event in events:
                    # Create notification
                    notification = EarningsNotification(
                        notification_id=f"EN_{uuid.uuid4().hex[:8]}",
                        event_id=event.event_id,
                        alert_id=alert.alert_id,
                        notification_type="in_app",
                        message=f"Earnings alert: {event.symbol} {event.event_type.value} on {event.announcement_date}",
                        is_sent=False
                    )
                    
                    self.db.add(notification)
                    
                    triggered_alerts.append({
                        "alert_id": alert.alert_id,
                        "event_id": event.event_id,
                        "symbol": event.symbol,
                        "event_type": event.event_type.value,
                        "announcement_date": event.announcement_date.isoformat(),
                        "message": notification.message
                    })
            
            self.db.commit()
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking earnings alerts: {e}")
            return []
    
    def get_upcoming_events(self, symbol: str = None, days_ahead: int = 30) -> Dict:
        """Get upcoming events"""
        try:
            start_date = date.today()
            end_date = start_date + timedelta(days=days_ahead)
            
            # Get earnings events
            earnings_query = self.db.query(EarningsEvent).filter(
                EarningsEvent.announcement_date >= start_date,
                EarningsEvent.announcement_date <= end_date
            )
            
            if symbol:
                earnings_query = earnings_query.filter(EarningsEvent.symbol == symbol.upper())
            
            earnings_events = earnings_query.order_by(EarningsEvent.announcement_date).all()
            
            # Get corporate actions
            actions_query = self.db.query(CorporateAction).filter(
                CorporateAction.announcement_date >= start_date,
                CorporateAction.announcement_date <= end_date
            )
            
            if symbol:
                actions_query = actions_query.filter(CorporateAction.symbol == symbol.upper())
            
            corporate_actions = actions_query.order_by(CorporateAction.announcement_date).all()
            
            # Format events
            events_data = []
            for event in earnings_events:
                events_data.append({
                    "id": event.event_id,
                    "type": "earnings",
                    "symbol": event.symbol,
                    "company_name": event.company_name,
                    "event_type": event.event_type.value,
                    "date": event.announcement_date.isoformat(),
                    "description": event.description,
                    "is_confirmed": event.is_confirmed
                })
            
            for action in corporate_actions:
                events_data.append({
                    "id": action.action_id,
                    "type": "corporate_action",
                    "symbol": action.symbol,
                    "company_name": action.company_name,
                    "event_type": action.action_type.value,
                    "date": action.announcement_date.isoformat(),
                    "description": action.description,
                    "is_confirmed": action.is_confirmed
                })
            
            # Sort by date
            events_data.sort(key=lambda x: x["date"])
            
            return {
                "symbol": symbol,
                "days_ahead": days_ahead,
                "total_events": len(events_data),
                "events": events_data
            }
            
        except Exception as e:
            logger.error(f"Error getting upcoming events: {e}")
            return {"error": str(e)}
    
    def get_earnings_history(self, symbol: str, limit: int = 20) -> Dict:
        """Get earnings history for a symbol"""
        try:
            # Get past earnings events
            events = self.db.query(EarningsEvent).filter(
                EarningsEvent.symbol == symbol.upper(),
                EarningsEvent.announcement_date < date.today()
            ).order_by(EarningsEvent.announcement_date.desc()).limit(limit).all()
            
            events_data = []
            for event in events:
                events_data.append({
                    "event_id": event.event_id,
                    "announcement_date": event.announcement_date.isoformat(),
                    "quarter": event.quarter,
                    "fiscal_year": event.fiscal_year,
                    "earnings_per_share": event.earnings_per_share,
                    "revenue": event.revenue,
                    "net_income": event.net_income,
                    "dividend_amount": event.dividend_amount,
                    "is_confirmed": event.is_confirmed
                })
            
            return {
                "symbol": symbol,
                "total_events": len(events_data),
                "events": events_data
            }
            
        except Exception as e:
            logger.error(f"Error getting earnings history: {e}")
            return {"error": str(e)}
    
    def update_event_status(self, event_id: str, status: EventStatus) -> Dict:
        """Update event status"""
        try:
            # Try earnings events first
            event = self.db.query(EarningsEvent).filter(EarningsEvent.event_id == event_id).first()
            if event:
                event.event_status = status
                event.updated_at = datetime.now()
                self.db.commit()
                
                return {
                    "event_id": event_id,
                    "status": status.value,
                    "message": "Earnings event status updated successfully"
                }
            
            # Try corporate actions
            action = self.db.query(CorporateAction).filter(CorporateAction.action_id == event_id).first()
            if action:
                action.action_status = status
                action.updated_at = datetime.now()
                self.db.commit()
                
                return {
                    "action_id": event_id,
                    "status": status.value,
                    "message": "Corporate action status updated successfully"
                }
            
            return {"error": "Event not found"}
            
        except Exception as e:
            logger.error(f"Error updating event status: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def delete_earnings_alert(self, alert_id: str) -> Dict:
        """Delete earnings alert"""
        try:
            deleted_count = self.db.query(EarningsAlert).filter(EarningsAlert.alert_id == alert_id).delete()
            
            if deleted_count == 0:
                return {"error": "Alert not found"}
            
            self.db.commit()
            
            return {
                "alert_id": alert_id,
                "status": "deleted",
                "message": "Earnings alert deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting earnings alert: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def list_earnings_alerts(self, symbol: str = None) -> List[Dict]:
        """List earnings alerts"""
        try:
            query = self.db.query(EarningsAlert).filter(EarningsAlert.is_active == True)
            
            if symbol:
                query = query.filter(EarningsAlert.symbol == symbol.upper())
            
            alerts = query.order_by(EarningsAlert.created_at.desc()).all()
            
            alerts_data = []
            for alert in alerts:
                alerts_data.append({
                    "alert_id": alert.alert_id,
                    "symbol": alert.symbol,
                    "event_type": alert.event_type.value,
                    "days_before": alert.days_before,
                    "notify_email": alert.notify_email,
                    "notify_in_app": alert.notify_in_app,
                    "created_at": alert.created_at.isoformat()
                })
            
            return alerts_data
            
        except Exception as e:
            logger.error(f"Error listing earnings alerts: {e}")
            return []
