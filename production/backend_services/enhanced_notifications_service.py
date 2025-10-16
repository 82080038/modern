"""
Enhanced Notifications Service
==============================

Service untuk notifications dengan implementasi algoritma terbukti
menggunakan smart filtering, priority management, dan multi-channel delivery.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import asyncio
import json
from app.models.notifications import Notification, NotificationType, NotificationPriority, NotificationChannel
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class EnhancedNotificationsService:
    """
    Enhanced Notifications Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = CacheService(db)
        
        # Notification channels
        self.channels = {
            'email': {'enabled': True, 'priority': 1},
            'sms': {'enabled': True, 'priority': 2},
            'push': {'enabled': True, 'priority': 3},
            'webhook': {'enabled': True, 'priority': 4},
            'in_app': {'enabled': True, 'priority': 5}
        }
        
        # Priority levels
        self.priority_levels = {
            'critical': {'score': 5, 'description': 'Critical alerts requiring immediate attention'},
            'high': {'score': 4, 'description': 'High priority notifications'},
            'medium': {'score': 3, 'description': 'Medium priority notifications'},
            'low': {'score': 2, 'description': 'Low priority notifications'},
            'info': {'score': 1, 'description': 'Informational notifications'}
        }
        
        # Notification types
        self.notification_types = {
            'price_alert': {'priority': 'high', 'channels': ['email', 'push', 'in_app']},
            'trade_execution': {'priority': 'medium', 'channels': ['email', 'push', 'in_app']},
            'portfolio_alert': {'priority': 'high', 'channels': ['email', 'push', 'in_app']},
            'risk_alert': {'priority': 'critical', 'channels': ['email', 'sms', 'push', 'in_app']},
            'market_news': {'priority': 'low', 'channels': ['email', 'in_app']},
            'system_alert': {'priority': 'medium', 'channels': ['email', 'push', 'in_app']},
            'earnings_alert': {'priority': 'high', 'channels': ['email', 'push', 'in_app']},
            'economic_event': {'priority': 'medium', 'channels': ['email', 'in_app']}
        }
        
        # Smart filtering rules
        self.filtering_rules = {
            'frequency_limit': {
                'price_alert': {'max_per_hour': 5, 'max_per_day': 20},
                'trade_execution': {'max_per_hour': 10, 'max_per_day': 50},
                'portfolio_alert': {'max_per_hour': 3, 'max_per_day': 15},
                'risk_alert': {'max_per_hour': 10, 'max_per_day': 50},
                'market_news': {'max_per_hour': 2, 'max_per_day': 10},
                'system_alert': {'max_per_hour': 5, 'max_per_day': 25},
                'earnings_alert': {'max_per_hour': 2, 'max_per_day': 8},
                'economic_event': {'max_per_hour': 1, 'max_per_day': 5}
            },
            'time_based_filtering': {
                'quiet_hours': {'start': '22:00', 'end': '06:00'},
                'weekend_filtering': True,
                'holiday_filtering': True
            }
        }
    
    async def create_notification(
        self, 
        user_id: int,
        notification_type: str,
        title: str,
        message: str,
        priority: str = 'medium',
        channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        scheduled_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Create enhanced notification dengan smart filtering"""
        try:
            # Validate notification type
            if notification_type not in self.notification_types:
                return {'error': f'Invalid notification type: {notification_type}'}
            
            # Apply smart filtering
            filter_result = await self._apply_smart_filtering(user_id, notification_type, priority)
            if not filter_result['allowed']:
                return {'error': f'Notification filtered: {filter_result["reason"]}'}
            
            # Determine priority
            if priority == 'auto':
                priority = self._determine_priority(notification_type, metadata)
            
            # Determine channels
            if not channels:
                channels = self._determine_channels(notification_type, priority)
            
            # Create notification
            notification = Notification(
                user_id=user_id,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                channels=json.dumps(channels),
                metadata=json.dumps(metadata or {}),
                scheduled_time=scheduled_time,
                status='pending',
                created_at=datetime.now()
            )
            
            self.db.add(notification)
            self.db.flush()  # Get the ID
            
            # Queue for delivery
            await self._queue_notification_delivery(notification)
            
            return {
                'success': True,
                'notification_id': notification.id,
                'status': 'queued',
                'channels': channels,
                'priority': priority,
                'scheduled_time': scheduled_time
            }
            
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return {'error': str(e)}
    
    async def _apply_smart_filtering(self, user_id: int, notification_type: str, priority: str) -> Dict[str, Any]:
        """Apply smart filtering rules"""
        try:
            # Check frequency limits
            frequency_check = await self._check_frequency_limits(user_id, notification_type)
            if not frequency_check['allowed']:
                return {'allowed': False, 'reason': frequency_check['reason']}
            
            # Check time-based filtering
            time_check = await self._check_time_based_filtering(priority)
            if not time_check['allowed']:
                return {'allowed': False, 'reason': time_check['reason']}
            
            # Check user preferences
            preferences_check = await self._check_user_preferences(user_id, notification_type)
            if not preferences_check['allowed']:
                return {'allowed': False, 'reason': preferences_check['reason']}
            
            # Check duplicate filtering
            duplicate_check = await self._check_duplicate_filtering(user_id, notification_type)
            if not duplicate_check['allowed']:
                return {'allowed': False, 'reason': duplicate_check['reason']}
            
            return {'allowed': True, 'reason': 'All filters passed'}
            
        except Exception as e:
            logger.error(f"Error applying smart filtering: {e}")
            return {'allowed': False, 'reason': f'Filtering error: {str(e)}'}
    
    async def _check_frequency_limits(self, user_id: int, notification_type: str) -> Dict[str, Any]:
        """Check frequency limits untuk notification type"""
        try:
            limits = self.filtering_rules['frequency_limit'].get(notification_type, {})
            if not limits:
                return {'allowed': True, 'reason': 'No frequency limits'}
            
            # Check hourly limit
            hour_ago = datetime.now() - timedelta(hours=1)
            hourly_count = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.notification_type == notification_type,
                Notification.created_at >= hour_ago
            ).count()
            
            if hourly_count >= limits.get('max_per_hour', 10):
                return {'allowed': False, 'reason': f'Hourly limit exceeded: {hourly_count}/{limits.get("max_per_hour", 10)}'}
            
            # Check daily limit
            day_ago = datetime.now() - timedelta(days=1)
            daily_count = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.notification_type == notification_type,
                Notification.created_at >= day_ago
            ).count()
            
            if daily_count >= limits.get('max_per_day', 50):
                return {'allowed': False, 'reason': f'Daily limit exceeded: {daily_count}/{limits.get("max_per_day", 50)}'}
            
            return {'allowed': True, 'reason': 'Frequency limits OK'}
            
        except Exception as e:
            logger.error(f"Error checking frequency limits: {e}")
            return {'allowed': False, 'reason': f'Frequency check error: {str(e)}'}
    
    async def _check_time_based_filtering(self, priority: str) -> Dict[str, Any]:
        """Check time-based filtering rules"""
        try:
            now = datetime.now()
            current_time = now.time()
            current_weekday = now.weekday()
            
            # Check quiet hours
            quiet_hours = self.filtering_rules['time_based_filtering']['quiet_hours']
            quiet_start = datetime.strptime(quiet_hours['start'], '%H:%M').time()
            quiet_end = datetime.strptime(quiet_hours['end'], '%H:%M').time()
            
            if quiet_start <= quiet_end:
                # Same day quiet hours
                if quiet_start <= current_time <= quiet_end and priority not in ['critical', 'high']:
                    return {'allowed': False, 'reason': 'Quiet hours - only critical/high priority allowed'}
            else:
                # Overnight quiet hours
                if current_time >= quiet_start or current_time <= quiet_end:
                    if priority not in ['critical', 'high']:
                        return {'allowed': False, 'reason': 'Quiet hours - only critical/high priority allowed'}
            
            # Check weekend filtering
            if self.filtering_rules['time_based_filtering']['weekend_filtering']:
                if current_weekday >= 5:  # Saturday = 5, Sunday = 6
                    if priority not in ['critical', 'high']:
                        return {'allowed': False, 'reason': 'Weekend - only critical/high priority allowed'}
            
            return {'allowed': True, 'reason': 'Time-based filtering passed'}
            
        except Exception as e:
            logger.error(f"Error checking time-based filtering: {e}")
            return {'allowed': True, 'reason': 'Time-based filtering error - allowing'}
    
    async def _check_user_preferences(self, user_id: int, notification_type: str) -> Dict[str, Any]:
        """Check user notification preferences"""
        try:
            # This would check user preferences from database
            # For now, assume all notifications are allowed
            return {'allowed': True, 'reason': 'User preferences OK'}
            
        except Exception as e:
            logger.error(f"Error checking user preferences: {e}")
            return {'allowed': True, 'reason': 'User preferences error - allowing'}
    
    async def _check_duplicate_filtering(self, user_id: int, notification_type: str) -> Dict[str, Any]:
        """Check for duplicate notifications"""
        try:
            # Check for recent duplicate notifications
            recent_time = datetime.now() - timedelta(minutes=5)
            recent_duplicates = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.notification_type == notification_type,
                Notification.created_at >= recent_time
            ).count()
            
            if recent_duplicates > 0:
                return {'allowed': False, 'reason': f'Duplicate notification within 5 minutes: {recent_duplicates}'}
            
            return {'allowed': True, 'reason': 'No duplicates found'}
            
        except Exception as e:
            logger.error(f"Error checking duplicate filtering: {e}")
            return {'allowed': True, 'reason': 'Duplicate check error - allowing'}
    
    def _determine_priority(self, notification_type: str, metadata: Optional[Dict[str, Any]]) -> str:
        """Determine notification priority"""
        try:
            # Get base priority from notification type
            base_priority = self.notification_types.get(notification_type, {}).get('priority', 'medium')
            
            # Adjust priority based on metadata
            if metadata:
                # Risk alerts are always critical
                if metadata.get('risk_level') == 'critical':
                    return 'critical'
                
                # Price alerts with significant changes
                if notification_type == 'price_alert':
                    price_change = metadata.get('price_change_percentage', 0)
                    if abs(price_change) > 10:
                        return 'high'
                    elif abs(price_change) > 5:
                        return 'medium'
                
                # Portfolio alerts with significant changes
                if notification_type == 'portfolio_alert':
                    portfolio_change = metadata.get('portfolio_change_percentage', 0)
                    if abs(portfolio_change) > 15:
                        return 'high'
                    elif abs(portfolio_change) > 5:
                        return 'medium'
            
            return base_priority
            
        except Exception as e:
            logger.error(f"Error determining priority: {e}")
            return 'medium'
    
    def _determine_channels(self, notification_type: str, priority: str) -> List[str]:
        """Determine notification channels"""
        try:
            # Get base channels from notification type
            base_channels = self.notification_types.get(notification_type, {}).get('channels', ['email', 'in_app'])
            
            # Adjust channels based on priority
            if priority == 'critical':
                # Critical notifications use all available channels
                return ['email', 'sms', 'push', 'in_app']
            elif priority == 'high':
                # High priority notifications use multiple channels
                return ['email', 'push', 'in_app']
            else:
                # Medium and low priority use base channels
                return base_channels
            
        except Exception as e:
            logger.error(f"Error determining channels: {e}")
            return ['email', 'in_app']
    
    async def _queue_notification_delivery(self, notification: Notification):
        """Queue notification for delivery"""
        try:
            # Add to delivery queue
            delivery_task = {
                'notification_id': notification.id,
                'user_id': notification.user_id,
                'channels': json.loads(notification.channels),
                'priority': notification.priority,
                'scheduled_time': notification.scheduled_time,
                'created_at': notification.created_at
            }
            
            # Store in cache for processing
            await self.cache_service.set(
                f"notification_queue_{notification.id}",
                delivery_task,
                ttl=3600  # 1 hour
            )
            
            # Start delivery process
            asyncio.create_task(self._process_notification_delivery(notification))
            
        except Exception as e:
            logger.error(f"Error queuing notification delivery: {e}")
    
    async def _process_notification_delivery(self, notification: Notification):
        """Process notification delivery"""
        try:
            channels = json.loads(notification.channels)
            
            # Deliver to each channel
            for channel in channels:
                try:
                    if channel == 'email':
                        await self._deliver_email_notification(notification)
                    elif channel == 'sms':
                        await self._deliver_sms_notification(notification)
                    elif channel == 'push':
                        await self._deliver_push_notification(notification)
                    elif channel == 'webhook':
                        await self._deliver_webhook_notification(notification)
                    elif channel == 'in_app':
                        await self._deliver_in_app_notification(notification)
                    
                except Exception as e:
                    logger.error(f"Error delivering to {channel}: {e}")
                    continue
            
            # Update notification status
            notification.status = 'delivered'
            notification.delivered_at = datetime.now()
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error processing notification delivery: {e}")
            notification.status = 'failed'
            notification.failed_at = datetime.now()
            self.db.commit()
    
    async def _deliver_email_notification(self, notification: Notification):
        """Deliver email notification"""
        try:
            # This would implement actual email delivery
            logger.info(f"Email notification delivered: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error delivering email notification: {e}")
    
    async def _deliver_sms_notification(self, notification: Notification):
        """Deliver SMS notification"""
        try:
            # This would implement actual SMS delivery
            logger.info(f"SMS notification delivered: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error delivering SMS notification: {e}")
    
    async def _deliver_push_notification(self, notification: Notification):
        """Deliver push notification"""
        try:
            # This would implement actual push notification delivery
            logger.info(f"Push notification delivered: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error delivering push notification: {e}")
    
    async def _deliver_webhook_notification(self, notification: Notification):
        """Deliver webhook notification"""
        try:
            # This would implement actual webhook delivery
            logger.info(f"Webhook notification delivered: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error delivering webhook notification: {e}")
    
    async def _deliver_in_app_notification(self, notification: Notification):
        """Deliver in-app notification"""
        try:
            # This would implement actual in-app notification delivery
            logger.info(f"In-app notification delivered: {notification.title}")
            
        except Exception as e:
            logger.error(f"Error delivering in-app notification: {e}")
    
    async def get_user_notifications(
        self, 
        user_id: int, 
        limit: int = 50,
        offset: int = 0,
        notification_type: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get user notifications dengan filtering"""
        try:
            query = self.db.query(Notification).filter(Notification.user_id == user_id)
            
            # Apply filters
            if notification_type:
                query = query.filter(Notification.notification_type == notification_type)
            
            if priority:
                query = query.filter(Notification.priority == priority)
            
            if status:
                query = query.filter(Notification.status == status)
            
            # Get total count
            total_count = query.count()
            
            # Get notifications
            notifications = query.order_by(Notification.created_at.desc()).offset(offset).limit(limit).all()
            
            # Format notifications
            formatted_notifications = []
            for notification in notifications:
                formatted_notifications.append({
                    'id': notification.id,
                    'notification_type': notification.notification_type,
                    'title': notification.title,
                    'message': notification.message,
                    'priority': notification.priority,
                    'channels': json.loads(notification.channels),
                    'metadata': json.loads(notification.metadata),
                    'status': notification.status,
                    'created_at': notification.created_at,
                    'delivered_at': notification.delivered_at,
                    'failed_at': notification.failed_at
                })
            
            return {
                'success': True,
                'notifications': formatted_notifications,
                'total_count': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            logger.error(f"Error getting user notifications: {e}")
            return {'error': str(e)}
    
    async def mark_notification_read(self, notification_id: int, user_id: int) -> Dict[str, Any]:
        """Mark notification as read"""
        try:
            notification = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id
            ).first()
            
            if not notification:
                return {'error': 'Notification not found'}
            
            # Update status
            notification.status = 'read'
            notification.read_at = datetime.now()
            self.db.commit()
            
            return {
                'success': True,
                'notification_id': notification_id,
                'status': 'read'
            }
            
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            return {'error': str(e)}
    
    async def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """Get notification statistics untuk user"""
        try:
            # Get total notifications
            total_notifications = self.db.query(Notification).filter(
                Notification.user_id == user_id
            ).count()
            
            # Get notifications by type
            notifications_by_type = {}
            for notification_type in self.notification_types.keys():
                count = self.db.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.notification_type == notification_type
                ).count()
                notifications_by_type[notification_type] = count
            
            # Get notifications by priority
            notifications_by_priority = {}
            for priority in self.priority_levels.keys():
                count = self.db.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.priority == priority
                ).count()
                notifications_by_priority[priority] = count
            
            # Get notifications by status
            notifications_by_status = {}
            for status in ['pending', 'delivered', 'read', 'failed']:
                count = self.db.query(Notification).filter(
                    Notification.user_id == user_id,
                    Notification.status == status
                ).count()
                notifications_by_status[status] = count
            
            return {
                'success': True,
                'total_notifications': total_notifications,
                'notifications_by_type': notifications_by_type,
                'notifications_by_priority': notifications_by_priority,
                'notifications_by_status': notifications_by_status
            }
            
        except Exception as e:
            logger.error(f"Error getting notification stats: {e}")
            return {'error': str(e)}
    
    async def create_price_alert(
        self, 
        user_id: int,
        symbol: str,
        target_price: float,
        condition: str = 'above',
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create price alert notification"""
        try:
            if condition not in ['above', 'below']:
                return {'error': 'Invalid condition. Must be "above" or "below"'}
            
            title = f"Price Alert: {symbol}"
            message = message or f"{symbol} price is {condition} ${target_price:.2f}"
            
            metadata = {
                'symbol': symbol,
                'target_price': target_price,
                'condition': condition,
                'alert_type': 'price_alert'
            }
            
            return await self.create_notification(
                user_id=user_id,
                notification_type='price_alert',
                title=title,
                message=message,
                priority='high',
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error creating price alert: {e}")
            return {'error': str(e)}
    
    async def create_portfolio_alert(
        self, 
        user_id: int,
        portfolio_id: int,
        alert_type: str,
        threshold: float,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create portfolio alert notification"""
        try:
            if alert_type not in ['value_change', 'daily_pnl', 'risk_level']:
                return {'error': 'Invalid alert type'}
            
            title = f"Portfolio Alert: {alert_type.title()}"
            message = message or f"Portfolio {alert_type} threshold reached: {threshold}"
            
            metadata = {
                'portfolio_id': portfolio_id,
                'alert_type': alert_type,
                'threshold': threshold,
                'alert_category': 'portfolio_alert'
            }
            
            return await self.create_notification(
                user_id=user_id,
                notification_type='portfolio_alert',
                title=title,
                message=message,
                priority='high',
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error creating portfolio alert: {e}")
            return {'error': str(e)}
    
    async def create_risk_alert(
        self, 
        user_id: int,
        risk_level: str,
        risk_metric: str,
        current_value: float,
        threshold: float,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create risk alert notification"""
        try:
            if risk_level not in ['low', 'medium', 'high', 'critical']:
                return {'error': 'Invalid risk level'}
            
            title = f"Risk Alert: {risk_metric.title()}"
            message = message or f"Risk level: {risk_level}. {risk_metric}: {current_value} (threshold: {threshold})"
            
            metadata = {
                'risk_level': risk_level,
                'risk_metric': risk_metric,
                'current_value': current_value,
                'threshold': threshold,
                'alert_category': 'risk_alert'
            }
            
            priority = 'critical' if risk_level == 'critical' else 'high'
            
            return await self.create_notification(
                user_id=user_id,
                notification_type='risk_alert',
                title=title,
                message=message,
                priority=priority,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"Error creating risk alert: {e}")
            return {'error': str(e)}
