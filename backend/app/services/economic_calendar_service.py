"""
Economic Calendar Service untuk Economic Events dan Alerts
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import logging
import requests
from bs4 import BeautifulSoup
import json

logger = logging.getLogger(__name__)

class EconomicCalendarService:
    """Service untuk economic calendar operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def scrape_economic_calendar(self, start_date: date = None, end_date: date = None) -> Dict:
        """Scrape economic calendar from free sources"""
        try:
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Scrape from multiple sources
            events = []
            
            # Scrape from investing.com (free)
            investing_events = self._scrape_investing_com(start_date, end_date)
            events.extend(investing_events)
            
            # Scrape from forex factory (free)
            forex_factory_events = self._scrape_forex_factory(start_date, end_date)
            events.extend(forex_factory_events)
            
            # Scrape from economic calendar websites
            calendar_events = self._scrape_economic_calendar_sites(start_date, end_date)
            events.extend(calendar_events)
            
            # Remove duplicates
            unique_events = self._remove_duplicate_events(events)
            
            return {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_events': len(unique_events),
                'events': unique_events,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping economic calendar: {e}")
            return {"error": str(e)}
    
    def _scrape_investing_com(self, start_date: date, end_date: date) -> List[Dict]:
        """Scrape economic events from investing.com"""
        try:
            events = []
            
            # This is a simplified implementation
            # In production, you would use proper web scraping with rate limiting
            
            # Mock data for demonstration
            mock_events = [
                {
                    'event_id': f"INV_{uuid.uuid4().hex[:8]}",
                    'title': 'GDP Growth Rate',
                    'country': 'United States',
                    'currency': 'USD',
                    'importance': 'High',
                    'event_date': start_date.isoformat(),
                    'time': '14:30',
                    'previous': '2.1%',
                    'forecast': '2.3%',
                    'actual': None,
                    'impact': 'High',
                    'source': 'investing.com'
                },
                {
                    'event_id': f"INV_{uuid.uuid4().hex[:8]}",
                    'title': 'Unemployment Rate',
                    'country': 'United States',
                    'currency': 'USD',
                    'importance': 'High',
                    'event_date': (start_date + timedelta(days=1)).isoformat(),
                    'time': '14:30',
                    'previous': '3.7%',
                    'forecast': '3.6%',
                    'actual': None,
                    'impact': 'High',
                    'source': 'investing.com'
                }
            ]
            
            events.extend(mock_events)
            return events
            
        except Exception as e:
            logger.error(f"Error scraping investing.com: {e}")
            return []
    
    def _scrape_forex_factory(self, start_date: date, end_date: date) -> List[Dict]:
        """Scrape economic events from forex factory"""
        try:
            events = []
            
            # Mock data for demonstration
            mock_events = [
                {
                    'event_id': f"FF_{uuid.uuid4().hex[:8]}",
                    'title': 'Non-Farm Payrolls',
                    'country': 'United States',
                    'currency': 'USD',
                    'importance': 'High',
                    'event_date': (start_date + timedelta(days=2)).isoformat(),
                    'time': '14:30',
                    'previous': '150K',
                    'forecast': '160K',
                    'actual': None,
                    'impact': 'High',
                    'source': 'forex_factory'
                }
            ]
            
            events.extend(mock_events)
            return events
            
        except Exception as e:
            logger.error(f"Error scraping forex factory: {e}")
            return []
    
    def _scrape_economic_calendar_sites(self, start_date: date, end_date: date) -> List[Dict]:
        """Scrape economic events from other calendar sites"""
        try:
            events = []
            
            # Mock data for demonstration
            mock_events = [
                {
                    'event_id': f"EC_{uuid.uuid4().hex[:8]}",
                    'title': 'Interest Rate Decision',
                    'country': 'United States',
                    'currency': 'USD',
                    'importance': 'High',
                    'event_date': (start_date + timedelta(days=3)).isoformat(),
                    'time': '14:00',
                    'previous': '5.25%',
                    'forecast': '5.50%',
                    'actual': None,
                    'impact': 'High',
                    'source': 'economic_calendar'
                }
            ]
            
            events.extend(mock_events)
            return events
            
        except Exception as e:
            logger.error(f"Error scraping economic calendar sites: {e}")
            return []
    
    def _remove_duplicate_events(self, events: List[Dict]) -> List[Dict]:
        """Remove duplicate events based on title and date"""
        try:
            unique_events = []
            seen_events = set()
            
            for event in events:
                # Create a unique key for the event
                event_key = f"{event['title']}_{event['event_date']}_{event['country']}"
                
                if event_key not in seen_events:
                    seen_events.add(event_key)
                    unique_events.append(event)
            
            return unique_events
            
        except Exception as e:
            logger.error(f"Error removing duplicate events: {e}")
            return events
    
    def get_economic_events(self, 
                           start_date: date = None, 
                           end_date: date = None,
                           countries: List[str] = None,
                           importance: List[str] = None,
                           limit: int = 100) -> Dict:
        """Get economic events with filters"""
        try:
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Scrape events
            calendar_data = self.scrape_economic_calendar(start_date, end_date)
            
            if "error" in calendar_data:
                return calendar_data
            
            events = calendar_data.get('events', [])
            
            # Apply filters
            filtered_events = events
            
            if countries:
                filtered_events = [e for e in filtered_events if e.get('country') in countries]
            
            if importance:
                filtered_events = [e for e in filtered_events if e.get('importance') in importance]
            
            # Limit results
            if limit:
                filtered_events = filtered_events[:limit]
            
            return {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'total_events': len(filtered_events),
                'events': filtered_events,
                'filters_applied': {
                    'countries': countries,
                    'importance': importance,
                    'limit': limit
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting economic events: {e}")
            return {"error": str(e)}
    
    def create_economic_alert(self,
                             event_title: str,
                             country: str,
                             event_date: date,
                             importance: str,
                             alert_before_hours: int = 24,
                             notify_email: bool = False,
                             notify_in_app: bool = True) -> Dict:
        """Create economic event alert"""
        try:
            # Generate unique alert ID
            alert_id = f"EA_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create alert (this would be saved to database in production)
            alert_data = {
                'alert_id': alert_id,
                'event_title': event_title,
                'country': country,
                'event_date': event_date.isoformat(),
                'importance': importance,
                'alert_before_hours': alert_before_hours,
                'notify_email': notify_email,
                'notify_in_app': notify_in_app,
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'alert_id': alert_id,
                'status': 'created',
                'message': 'Economic alert created successfully',
                'alert_data': alert_data
            }
            
        except Exception as e:
            logger.error(f"Error creating economic alert: {e}")
            return {"error": str(e)}
    
    def check_economic_alerts(self) -> List[Dict]:
        """Check and trigger economic alerts"""
        try:
            # This would check database for alerts in production
            # For now, return mock data
            
            triggered_alerts = [
                {
                    'alert_id': f"EA_{uuid.uuid4().hex[:8]}",
                    'event_title': 'GDP Growth Rate',
                    'country': 'United States',
                    'event_date': date.today().isoformat(),
                    'importance': 'High',
                    'alert_message': 'Economic event: GDP Growth Rate for United States is scheduled for today',
                    'triggered_at': datetime.now().isoformat()
                }
            ]
            
            return triggered_alerts
            
        except Exception as e:
            logger.error(f"Error checking economic alerts: {e}")
            return []
    
    def get_economic_impact_analysis(self, symbol: str, event_date: date = None) -> Dict:
        """Get economic impact analysis for a symbol"""
        try:
            if not event_date:
                event_date = date.today()
            
            # Get economic events for the date
            events = self.get_economic_events(
                start_date=event_date,
                end_date=event_date
            )
            
            if "error" in events:
                return events
            
            # Analyze impact
            high_impact_events = [e for e in events['events'] if e.get('impact') == 'High']
            medium_impact_events = [e for e in events['events'] if e.get('impact') == 'Medium']
            low_impact_events = [e for e in events['events'] if e.get('impact') == 'Low']
            
            # Calculate impact score
            impact_score = 0
            impact_score += len(high_impact_events) * 3
            impact_score += len(medium_impact_events) * 2
            impact_score += len(low_impact_events) * 1
            
            # Determine impact level
            if impact_score >= 6:
                impact_level = 'Very High'
            elif impact_score >= 4:
                impact_level = 'High'
            elif impact_score >= 2:
                impact_level = 'Medium'
            else:
                impact_level = 'Low'
            
            return {
                'symbol': symbol,
                'event_date': event_date.isoformat(),
                'impact_level': impact_level,
                'impact_score': impact_score,
                'high_impact_events': len(high_impact_events),
                'medium_impact_events': len(medium_impact_events),
                'low_impact_events': len(low_impact_events),
                'total_events': len(events['events']),
                'events': events['events']
            }
            
        except Exception as e:
            logger.error(f"Error getting economic impact analysis: {e}")
            return {"error": str(e)}
    
    def get_economic_calendar_summary(self, start_date: date = None, end_date: date = None) -> Dict:
        """Get economic calendar summary"""
        try:
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=7)
            
            # Get events
            events_data = self.get_economic_events(start_date, end_date)
            
            if "error" in events_data:
                return events_data
            
            events = events_data['events']
            
            # Create summary
            summary = {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'total_days': (end_date - start_date).days
                },
                'events_summary': {
                    'total_events': len(events),
                    'high_importance': len([e for e in events if e.get('importance') == 'High']),
                    'medium_importance': len([e for e in events if e.get('importance') == 'Medium']),
                    'low_importance': len([e for e in events if e.get('importance') == 'Low'])
                },
                'countries': list(set([e.get('country') for e in events if e.get('country')])),
                'currencies': list(set([e.get('currency') for e in events if e.get('currency')])),
                'top_events': sorted(events, key=lambda x: x.get('importance', ''), reverse=True)[:10]
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting economic calendar summary: {e}")
            return {"error": str(e)}
    
    def get_available_countries(self) -> List[Dict]:
        """Get available countries for economic events"""
        try:
            countries = [
                {'code': 'US', 'name': 'United States', 'currency': 'USD'},
                {'code': 'EU', 'name': 'European Union', 'currency': 'EUR'},
                {'code': 'GB', 'name': 'United Kingdom', 'currency': 'GBP'},
                {'code': 'JP', 'name': 'Japan', 'currency': 'JPY'},
                {'code': 'CA', 'name': 'Canada', 'currency': 'CAD'},
                {'code': 'AU', 'name': 'Australia', 'currency': 'AUD'},
                {'code': 'CH', 'name': 'Switzerland', 'currency': 'CHF'},
                {'code': 'CN', 'name': 'China', 'currency': 'CNY'},
                {'code': 'IN', 'name': 'India', 'currency': 'INR'},
                {'code': 'BR', 'name': 'Brazil', 'currency': 'BRL'}
            ]
            
            return countries
            
        except Exception as e:
            logger.error(f"Error getting available countries: {e}")
            return []
    
    def get_importance_levels(self) -> List[Dict]:
        """Get available importance levels"""
        try:
            importance_levels = [
                {'level': 'High', 'description': 'High impact on markets', 'color': 'red'},
                {'level': 'Medium', 'description': 'Medium impact on markets', 'color': 'orange'},
                {'level': 'Low', 'description': 'Low impact on markets', 'color': 'green'}
            ]
            
            return importance_levels
            
        except Exception as e:
            logger.error(f"Error getting importance levels: {e}")
            return []
