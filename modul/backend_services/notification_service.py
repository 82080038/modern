"""
Notification Service untuk In-App Notifications
"""
from sqlalchemy.orm import Session
from app.models.notifications import (
    Notification, AlertRule, NotificationSettings,
    NotificationType, NotificationPriority, NotificationStatus
)
from app.services.data_service import DataService
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
import logging
import json

logger = logging.getLogger(__name__)

class NotificationService:
    """Service untuk notification operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_service = DataService(db)
    
    def create_notification(self,
                           notification_type: NotificationType,
                           title: str,
                           message: str,
                           priority: NotificationPriority = NotificationPriority.MEDIUM,
                           symbol: str = None,
                           order_id: str = None,
                           trade_id: str = None,
                           metadata: Dict = None,
                           action_url: str = None,
                           action_text: str = None,
                           expires_in_hours: int = 24) -> Dict:
        """Create new notification"""
        try:
            # Generate unique notification ID
            notification_id = f"NOTIF_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Set icon and color based on type
            icon, color = self._get_notification_style(notification_type, priority)
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(hours=expires_in_hours) if expires_in_hours > 0 else None
            
            # Create notification
            notification = Notification(
                notification_id=notification_id,
                type=notification_type,
                priority=priority,
                title=title,
                message=message,
                icon=icon,
                color=color,
                symbol=symbol,
                order_id=order_id,
                trade_id=trade_id,
                metadata=metadata,
                action_url=action_url,
                action_text=action_text,
                expires_at=expires_at
            )
            
            self.db.add(notification)
            self.db.commit()
            
            # Trigger real-time notification via WebSocket
            self._broadcast_notification(notification)
            
            return {
                "notification_id": notification_id,
                "status": "created",
                "message": "Notification created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _get_notification_style(self, notification_type: NotificationType, priority: NotificationPriority) -> tuple:
        """Get icon and color for notification"""
        styles = {
            NotificationType.ORDER_FILLED: ("✅", "success"),
            NotificationType.ORDER_CANCELLED: ("❌", "danger"),
            NotificationType.PRICE_ALERT: ("📈", "warning"),
            NotificationType.SENTIMENT_ALERT: ("😊", "info"),
            NotificationType.RISK_ALERT: ("⚠️", "danger"),
            NotificationType.SYSTEM_ALERT: ("🔧", "secondary"),
            NotificationType.MARKET_ALERT: ("📊", "primary")
        }
        
        icon, base_color = styles.get(notification_type, ("📢", "primary"))
        
        # Adjust color based on priority
        if priority == NotificationPriority.CRITICAL:
            color = "danger"
        elif priority == NotificationPriority.HIGH:
            color = "warning"
        elif priority == NotificationPriority.MEDIUM:
            color = base_color
        else:  # LOW
            color = "secondary"
        
        return icon, color
    
    def _broadcast_notification(self, notification: Notification):
        """Broadcast notification via WebSocket"""
        try:
            # This would integrate with WebSocket server
            # For now, just log the notification
            logger.info(f"Broadcasting notification: {notification.title}")
            
            # TODO: Integrate with WebSocket server to push real-time notifications
            # socketio.emit('notification', {
            #     'id': notification.notification_id,
            #     'type': notification.type.value,
            #     'title': notification.title,
            #     'message': notification.message,
            #     'icon': notification.icon,
            #     'color': notification.color,
            #     'timestamp': notification.created_at.isoformat()
            # })
            
        except Exception as e:
            logger.error(f"Error broadcasting notification: {e}")
    
    def get_notifications(self,
                         status: NotificationStatus = None,
                         notification_type: NotificationType = None,
                         symbol: str = None,
                         limit: int = 50,
                         offset: int = 0) -> List[Dict]:
        """Get notifications with filters"""
        try:
            query = self.db.query(Notification)
            
            # Apply filters
            if status:
                query = query.filter(Notification.status == status)
            
            if notification_type:
                query = query.filter(Notification.type == notification_type)
            
            if symbol:
                query = query.filter(Notification.symbol == symbol.upper())
            
            # Filter out expired notifications
            query = query.filter(
                (Notification.expires_at.is_(None)) | 
                (Notification.expires_at > datetime.now())
            )
            
            # Order by created_at desc and apply pagination
            notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
            
            notification_list = []
            for notif in notifications:
                notification_list.append({
                    "id": notif.notification_id,
                    "type": notif.type.value,
                    "priority": notif.priority.value,
                    "status": notif.status.value,
                    "title": notif.title,
                    "message": notif.message,
                    "icon": notif.icon,
                    "color": notif.color,
                    "symbol": notif.symbol,
                    "order_id": notif.order_id,
                    "trade_id": notif.trade_id,
                    "metadata": notif.metadata,
                    "action_url": notif.action_url,
                    "action_text": notif.action_text,
                    "created_at": notif.created_at.isoformat(),
                    "read_at": notif.read_at.isoformat() if notif.read_at else None,
                    "expires_at": notif.expires_at.isoformat() if notif.expires_at else None
                })
            
            return notification_list
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return []
    
    def mark_as_read(self, notification_id: str) -> Dict:
        """Mark notification as read"""
        try:
            notification = self.db.query(Notification).filter(
                Notification.notification_id == notification_id
            ).first()
            
            if not notification:
                return {"error": "Notification not found"}
            
            if notification.status == NotificationStatus.READ:
                return {"message": "Notification already marked as read"}
            
            notification.status = NotificationStatus.READ
            notification.read_at = datetime.now()
            
            self.db.commit()
            
            return {
                "notification_id": notification_id,
                "status": "read",
                "message": "Notification marked as read"
            }
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def mark_all_as_read(self) -> Dict:
        """Mark all unread notifications as read"""
        try:
            updated_count = self.db.query(Notification).filter(
                Notification.status == NotificationStatus.UNREAD
            ).update({
                "status": NotificationStatus.READ,
                "read_at": datetime.now()
            })
            
            self.db.commit()
            
            return {
                "updated_count": updated_count,
                "status": "success",
                "message": f"Marked {updated_count} notifications as read"
            }
            
        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def archive_notification(self, notification_id: str) -> Dict:
        """Archive notification"""
        try:
            notification = self.db.query(Notification).filter(
                Notification.notification_id == notification_id
            ).first()
            
            if not notification:
                return {"error": "Notification not found"}
            
            notification.status = NotificationStatus.ARCHIVED
            notification.archived_at = datetime.now()
            
            self.db.commit()
            
            return {
                "notification_id": notification_id,
                "status": "archived",
                "message": "Notification archived"
            }
            
        except Exception as e:
            logger.error(f"Error archiving notification: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_notification_stats(self) -> Dict:
        """Get notification statistics"""
        try:
            total_notifications = self.db.query(Notification).count()
            unread_count = self.db.query(Notification).filter(
                Notification.status == NotificationStatus.UNREAD
            ).count()
            read_count = self.db.query(Notification).filter(
                Notification.status == NotificationStatus.READ
            ).count()
            archived_count = self.db.query(Notification).filter(
                Notification.status == NotificationStatus.ARCHIVED
            ).count()
            
            # Count by type
            type_counts = {}
            for notif_type in NotificationType:
                count = self.db.query(Notification).filter(
                    Notification.type == notif_type
                ).count()
                type_counts[notif_type.value] = count
            
            # Count by priority
            priority_counts = {}
            for priority in NotificationPriority:
                count = self.db.query(Notification).filter(
                    Notification.priority == priority
                ).count()
                priority_counts[priority.value] = count
            
            return {
                "total_notifications": total_notifications,
                "unread_count": unread_count,
                "read_count": read_count,
                "archived_count": archived_count,
                "type_counts": type_counts,
                "priority_counts": priority_counts
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {"error": str(e)}
    
    def create_alert_rule(self,
                         name: str,
                         description: str,
                         symbol: str,
                         alert_type: str,
                         condition: str,
                         threshold_value: float,
                         notification_type: NotificationType,
                         priority: NotificationPriority = NotificationPriority.MEDIUM,
                         title_template: str = None,
                         message_template: str = None,
                         cooldown_minutes: int = 60) -> Dict:
        """Create alert rule"""
        try:
            # Generate unique rule ID
            rule_id = f"RULE_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Set default templates if not provided
            if not title_template:
                title_template = f"{alert_type.title()} Alert for {symbol}"
            
            if not message_template:
                message_template = f"{symbol} {alert_type} is {condition} {threshold_value}"
            
            # Create alert rule
            rule = AlertRule(
                rule_id=rule_id,
                name=name,
                description=description,
                symbol=symbol.upper(),
                alert_type=alert_type,
                condition=condition,
                threshold_value=threshold_value,
                notification_type=notification_type,
                priority=priority,
                title_template=title_template,
                message_template=message_template,
                cooldown_minutes=cooldown_minutes
            )
            
            self.db.add(rule)
            self.db.commit()
            
            return {
                "rule_id": rule_id,
                "status": "created",
                "message": "Alert rule created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating alert rule: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def check_price_alerts(self, symbol: str, current_price: float) -> List[Dict]:
        """Check price alerts for a symbol"""
        try:
            # Get active price alert rules for this symbol
            rules = self.db.query(AlertRule).filter(
                AlertRule.symbol == symbol.upper(),
                AlertRule.alert_type == "price",
                AlertRule.is_active == True
            ).all()
            
            triggered_alerts = []
            
            for rule in rules:
                # Check if rule should be triggered
                should_trigger = False
                
                if rule.condition == "above" and current_price > rule.threshold_value:
                    should_trigger = True
                elif rule.condition == "below" and current_price < rule.threshold_value:
                    should_trigger = True
                elif rule.condition == "equals" and abs(current_price - rule.threshold_value) < 0.01:
                    should_trigger = True
                
                if should_trigger:
                    # Check cooldown
                    if rule.last_triggered:
                        time_since_last = datetime.now() - rule.last_triggered
                        if time_since_last.total_seconds() < (rule.cooldown_minutes * 60):
                            continue  # Skip due to cooldown
                    
                    # Create notification
                    title = rule.title_template.replace("{symbol}", symbol).replace("{price}", str(current_price))
                    message = rule.message_template.replace("{symbol}", symbol).replace("{price}", str(current_price))
                    
                    notification_result = self.create_notification(
                        notification_type=rule.notification_type,
                        title=title,
                        message=message,
                        priority=rule.priority,
                        symbol=symbol,
                        metadata={
                            "rule_id": rule.rule_id,
                            "threshold": rule.threshold_value,
                            "current_price": current_price,
                            "condition": rule.condition
                        }
                    )
                    
                    if "error" not in notification_result:
                        # Update rule trigger info
                        rule.last_triggered = datetime.now()
                        rule.trigger_count += 1
                        self.db.commit()
                        
                        triggered_alerts.append({
                            "rule_id": rule.rule_id,
                            "notification_id": notification_result["notification_id"],
                            "threshold": rule.threshold_value,
                            "current_price": current_price
                        })
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking price alerts: {e}")
            return []
    
    def cleanup_expired_notifications(self) -> Dict:
        """Clean up expired notifications"""
        try:
            # Mark expired notifications
            expired_count = self.db.query(Notification).filter(
                Notification.expires_at < datetime.now(),
                Notification.is_expired == False
            ).update({"is_expired": True})
            
            # Archive old read notifications (older than 7 days)
            old_notifications = self.db.query(Notification).filter(
                Notification.status == NotificationStatus.READ,
                Notification.read_at < datetime.now() - timedelta(days=7)
            ).update({
                "status": NotificationStatus.ARCHIVED,
                "archived_at": datetime.now()
            })
            
            self.db.commit()
            
            return {
                "expired_count": expired_count,
                "archived_count": old_notifications,
                "status": "success",
                "message": f"Cleaned up {expired_count} expired and {old_notifications} old notifications"
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")
            self.db.rollback()
            return {"error": str(e)}
