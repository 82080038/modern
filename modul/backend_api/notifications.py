"""
Notifications API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.database import get_db
from app.services.notification_service import NotificationService
from app.models.notifications import NotificationType, NotificationPriority, NotificationStatus
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/notifications", tags=["Notifications"])

# Pydantic schemas
class CreateNotificationRequest(BaseModel):
    type: str  # order_filled, price_alert, sentiment_alert, etc.
    title: str
    message: str
    priority: str = "medium"  # low, medium, high, critical
    symbol: Optional[str] = None
    order_id: Optional[str] = None
    trade_id: Optional[str] = None
    metadata: Optional[Dict] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    expires_in_hours: int = 24

class CreateAlertRuleRequest(BaseModel):
    name: str
    description: Optional[str] = None
    symbol: str
    alert_type: str  # price, volume, sentiment, etc.
    condition: str  # above, below, equals
    threshold_value: float
    notification_type: str
    priority: str = "medium"
    title_template: Optional[str] = None
    message_template: Optional[str] = None
    cooldown_minutes: int = 60

class NotificationResponse(BaseModel):
    id: str
    type: str
    priority: str
    status: str
    title: str
    message: str
    icon: str
    color: str
    symbol: Optional[str]
    order_id: Optional[str]
    trade_id: Optional[str]
    metadata: Optional[Dict]
    action_url: Optional[str]
    action_text: Optional[str]
    created_at: str
    read_at: Optional[str]
    expires_at: Optional[str]

class NotificationStatsResponse(BaseModel):
    total_notifications: int
    unread_count: int
    read_count: int
    archived_count: int
    type_counts: Dict[str, int]
    priority_counts: Dict[str, int]

@router.post("/", response_model=NotificationResponse)
async def create_notification(
    notification_request: CreateNotificationRequest,
    db: Session = Depends(get_db)
):
    """Create new notification"""
    try:
        # Validate notification type
        valid_types = [t.value for t in NotificationType]
        if notification_request.type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid notification type. Valid options: {valid_types}")
        
        # Validate priority
        valid_priorities = [p.value for p in NotificationPriority]
        if notification_request.priority not in valid_priorities:
            raise HTTPException(status_code=400, detail=f"Invalid priority. Valid options: {valid_priorities}")
        
        # Convert to enums
        notification_type = NotificationType(notification_request.type)
        priority = NotificationPriority(notification_request.priority)
        
        # Create notification service
        notification_service = NotificationService(db)
        
        # Create notification
        result = notification_service.create_notification(
            notification_type=notification_type,
            title=notification_request.title,
            message=notification_request.message,
            priority=priority,
            symbol=notification_request.symbol,
            order_id=notification_request.order_id,
            trade_id=notification_request.trade_id,
            metadata=notification_request.metadata,
            action_url=notification_request.action_url,
            action_text=notification_request.action_text,
            expires_in_hours=notification_request.expires_in_hours
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "id": result["notification_id"],
            "type": notification_request.type,
            "priority": notification_request.priority,
            "status": "unread",
            "title": notification_request.title,
            "message": notification_request.message,
            "icon": "📢",  # Default icon
            "color": "primary",  # Default color
            "symbol": notification_request.symbol,
            "order_id": notification_request.order_id,
            "trade_id": notification_request.trade_id,
            "metadata": notification_request.metadata,
            "action_url": notification_request.action_url,
            "action_text": notification_request.action_text,
            "created_at": datetime.now().isoformat(),
            "read_at": None,
            "expires_at": None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    status: Optional[str] = Query(None, description="Filter by status: unread, read, archived"),
    type: Optional[str] = Query(None, description="Filter by notification type"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(50, description="Maximum number of notifications to return"),
    offset: int = Query(0, description="Number of notifications to skip"),
    db: Session = Depends(get_db)
):
    """Get notifications with filters"""
    try:
        # Validate status if provided
        if status:
            valid_statuses = [s.value for s in NotificationStatus]
            if status not in valid_statuses:
                raise HTTPException(status_code=400, detail=f"Invalid status. Valid options: {valid_statuses}")
            status_enum = NotificationStatus(status)
        else:
            status_enum = None
        
        # Validate type if provided
        if type:
            valid_types = [t.value for t in NotificationType]
            if type not in valid_types:
                raise HTTPException(status_code=400, detail=f"Invalid type. Valid options: {valid_types}")
            type_enum = NotificationType(type)
        else:
            type_enum = None
        
        # Create notification service
        notification_service = NotificationService(db)
        
        # Get notifications
        notifications = notification_service.get_notifications(
            status=status_enum,
            notification_type=type_enum,
            symbol=symbol,
            limit=limit,
            offset=offset
        )
        
        return notifications
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats", response_model=NotificationStatsResponse)
async def get_notification_stats(db: Session = Depends(get_db)):
    """Get notification statistics"""
    try:
        notification_service = NotificationService(db)
        stats = notification_service.get_notification_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=400, detail=stats["error"])
        
        return NotificationStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    try:
        notification_service = NotificationService(db)
        result = notification_service.mark_as_read(notification_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/read-all")
async def mark_all_notifications_as_read(db: Session = Depends(get_db)):
    """Mark all notifications as read"""
    try:
        notification_service = NotificationService(db)
        result = notification_service.mark_all_as_read()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{notification_id}/archive")
async def archive_notification(
    notification_id: str,
    db: Session = Depends(get_db)
):
    """Archive notification"""
    try:
        notification_service = NotificationService(db)
        result = notification_service.archive_notification(notification_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving notification: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/alert-rules")
async def create_alert_rule(
    rule_request: CreateAlertRuleRequest,
    db: Session = Depends(get_db)
):
    """Create alert rule"""
    try:
        # Validate notification type
        valid_types = [t.value for t in NotificationType]
        if rule_request.notification_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid notification type. Valid options: {valid_types}")
        
        # Validate priority
        valid_priorities = [p.value for p in NotificationPriority]
        if rule_request.priority not in valid_priorities:
            raise HTTPException(status_code=400, detail=f"Invalid priority. Valid options: {valid_priorities}")
        
        # Validate condition
        valid_conditions = ["above", "below", "equals"]
        if rule_request.condition not in valid_conditions:
            raise HTTPException(status_code=400, detail=f"Invalid condition. Valid options: {valid_conditions}")
        
        # Convert to enums
        notification_type = NotificationType(rule_request.notification_type)
        priority = NotificationPriority(rule_request.priority)
        
        # Create notification service
        notification_service = NotificationService(db)
        
        # Create alert rule
        result = notification_service.create_alert_rule(
            name=rule_request.name,
            description=rule_request.description,
            symbol=rule_request.symbol,
            alert_type=rule_request.alert_type,
            condition=rule_request.condition,
            threshold_value=rule_request.threshold_value,
            notification_type=notification_type,
            priority=priority,
            title_template=rule_request.title_template,
            message_template=rule_request.message_template,
            cooldown_minutes=rule_request.cooldown_minutes
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating alert rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/alert-rules")
async def get_alert_rules(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get alert rules"""
    try:
        from app.models.notifications import AlertRule
        
        query = db.query(AlertRule)
        
        if symbol:
            query = query.filter(AlertRule.symbol == symbol.upper())
        
        if is_active is not None:
            query = query.filter(AlertRule.is_active == is_active)
        
        rules = query.order_by(AlertRule.created_at.desc()).all()
        
        rule_list = []
        for rule in rules:
            rule_list.append({
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "symbol": rule.symbol,
                "alert_type": rule.alert_type,
                "condition": rule.condition,
                "threshold_value": rule.threshold_value,
                "notification_type": rule.notification_type.value,
                "priority": rule.priority.value,
                "is_active": rule.is_active,
                "cooldown_minutes": rule.cooldown_minutes,
                "trigger_count": rule.trigger_count,
                "last_triggered": rule.last_triggered.isoformat() if rule.last_triggered else None,
                "created_at": rule.created_at.isoformat()
            })
        
        return {
            "rules": rule_list,
            "total_count": len(rule_list)
        }
        
    except Exception as e:
        logger.error(f"Error getting alert rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_notifications(db: Session = Depends(get_db)):
    """Clean up expired and old notifications"""
    try:
        notification_service = NotificationService(db)
        result = notification_service.cleanup_expired_notifications()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up notifications: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unread-count")
async def get_unread_count(db: Session = Depends(get_db)):
    """Get unread notification count"""
    try:
        notification_service = NotificationService(db)
        stats = notification_service.get_notification_stats()
        
        if "error" in stats:
            raise HTTPException(status_code=400, detail=stats["error"])
        
        return {
            "unread_count": stats["unread_count"],
            "total_count": stats["total_notifications"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        raise HTTPException(status_code=500, detail=str(e))
