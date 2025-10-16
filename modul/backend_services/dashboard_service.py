"""
Dashboard Service untuk Widget-based Dashboard System
"""
from sqlalchemy.orm import Session
from app.models.dashboard import (
    Dashboard, DashboardWidget, WidgetData, DashboardPreset, 
    WidgetTemplate, DashboardShare, DashboardAnalytics,
    WidgetType, DashboardLayout
)
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import uuid
import logging
import json

logger = logging.getLogger(__name__)

class DashboardService:
    """Service untuk dashboard operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_dashboard(self,
                        name: str,
                        description: str = None,
                        layout_type: DashboardLayout = DashboardLayout.GRID,
                        grid_columns: int = 4,
                        grid_rows: int = 3,
                        theme: str = "light",
                        color_scheme: str = "blue") -> Dict:
        """Create new dashboard"""
        try:
            # Generate unique dashboard ID
            dashboard_id = f"DB_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create dashboard
            dashboard = Dashboard(
                dashboard_id=dashboard_id,
                name=name,
                description=description,
                layout_type=layout_type,
                grid_columns=grid_columns,
                grid_rows=grid_rows,
                theme=theme,
                color_scheme=color_scheme
            )
            
            self.db.add(dashboard)
            self.db.commit()
            
            return {
                "dashboard_id": dashboard_id,
                "name": name,
                "status": "created",
                "message": "Dashboard created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating dashboard: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def add_widget_to_dashboard(self,
                               dashboard_id: str,
                               widget_type: WidgetType,
                               title: str,
                               position_x: int = 0,
                               position_y: int = 0,
                               width: int = 1,
                               height: int = 1,
                               config: Dict = None) -> Dict:
        """Add widget to dashboard"""
        try:
            # Check if dashboard exists
            dashboard = self.db.query(Dashboard).filter(Dashboard.dashboard_id == dashboard_id).first()
            if not dashboard:
                return {"error": "Dashboard not found"}
            
            # Generate unique widget ID
            widget_id = f"WD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create widget
            widget = DashboardWidget(
                widget_id=widget_id,
                dashboard_id=dashboard_id,
                widget_type=widget_type,
                title=title,
                position_x=position_x,
                position_y=position_y,
                width=width,
                height=height,
                config=config or {}
            )
            
            self.db.add(widget)
            self.db.commit()
            
            return {
                "widget_id": widget_id,
                "title": title,
                "status": "added",
                "message": "Widget added to dashboard successfully"
            }
            
        except Exception as e:
            logger.error(f"Error adding widget to dashboard: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def update_widget_position(self,
                              widget_id: str,
                              position_x: int,
                              position_y: int,
                              width: int = None,
                              height: int = None) -> Dict:
        """Update widget position and size"""
        try:
            widget = self.db.query(DashboardWidget).filter(DashboardWidget.widget_id == widget_id).first()
            if not widget:
                return {"error": "Widget not found"}
            
            widget.position_x = position_x
            widget.position_y = position_y
            
            if width is not None:
                widget.width = width
            if height is not None:
                widget.height = height
            
            widget.updated_at = datetime.now()
            self.db.commit()
            
            return {
                "widget_id": widget_id,
                "status": "updated",
                "message": "Widget position updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating widget position: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def update_widget_config(self, widget_id: str, config: Dict) -> Dict:
        """Update widget configuration"""
        try:
            widget = self.db.query(DashboardWidget).filter(DashboardWidget.widget_id == widget_id).first()
            if not widget:
                return {"error": "Widget not found"}
            
            # Merge with existing config
            existing_config = widget.config or {}
            existing_config.update(config)
            widget.config = existing_config
            widget.updated_at = datetime.now()
            
            self.db.commit()
            
            return {
                "widget_id": widget_id,
                "status": "updated",
                "message": "Widget configuration updated successfully"
            }
            
        except Exception as e:
            logger.error(f"Error updating widget config: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_dashboard_data(self, dashboard_id: str) -> Dict:
        """Get dashboard data with widgets"""
        try:
            # Get dashboard
            dashboard = self.db.query(Dashboard).filter(Dashboard.dashboard_id == dashboard_id).first()
            if not dashboard:
                return {"error": "Dashboard not found"}
            
            # Get widgets
            widgets = self.db.query(DashboardWidget).filter(
                DashboardWidget.dashboard_id == dashboard_id,
                DashboardWidget.is_visible == True
            ).all()
            
            # Format widgets data
            widgets_data = []
            for widget in widgets:
                widget_data = {
                    "widget_id": widget.widget_id,
                    "widget_type": widget.widget_type.value,
                    "title": widget.title,
                    "description": widget.description,
                    "position": {
                        "x": widget.position_x,
                        "y": widget.position_y,
                        "width": widget.width,
                        "height": widget.height
                    },
                    "config": widget.config,
                    "data_source": widget.data_source,
                    "refresh_interval": widget.refresh_interval,
                    "display_settings": {
                        "is_resizable": widget.is_resizable,
                        "is_movable": widget.is_movable,
                        "border_style": widget.border_style,
                        "background_color": widget.background_color
                    }
                }
                widgets_data.append(widget_data)
            
            return {
                "dashboard_id": dashboard_id,
                "name": dashboard.name,
                "description": dashboard.description,
                "layout": {
                    "type": dashboard.layout_type.value,
                    "grid_columns": dashboard.grid_columns,
                    "grid_rows": dashboard.grid_rows,
                    "config": dashboard.layout_config
                },
                "theme": {
                    "theme": dashboard.theme,
                    "color_scheme": dashboard.color_scheme
                },
                "settings": {
                    "auto_refresh": dashboard.auto_refresh,
                    "refresh_interval": dashboard.refresh_interval
                },
                "widgets": widgets_data,
                "total_widgets": len(widgets_data),
                "created_at": dashboard.created_at.isoformat(),
                "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            return {"error": str(e)}
    
    def get_widget_data(self, widget_id: str) -> Dict:
        """Get widget data and configuration"""
        try:
            widget = self.db.query(DashboardWidget).filter(DashboardWidget.widget_id == widget_id).first()
            if not widget:
                return {"error": "Widget not found"}
            
            # Get cached data if available
            cached_data = self.db.query(WidgetData).filter(
                WidgetData.widget_id == widget_id,
                WidgetData.is_valid == True,
                WidgetData.expires_at > datetime.now()
            ).order_by(WidgetData.updated_at.desc()).first()
            
            return {
                "widget_id": widget_id,
                "dashboard_id": widget.widget_id,
                "widget_type": widget.widget_type.value,
                "title": widget.title,
                "description": widget.description,
                "position": {
                    "x": widget.position_x,
                    "y": widget.position_y,
                    "width": widget.width,
                    "height": widget.height
                },
                "config": widget.config,
                "data_source": widget.data_source,
                "refresh_interval": widget.refresh_interval,
                "cached_data": cached_data.data_value if cached_data else None,
                "data_expires_at": cached_data.expires_at.isoformat() if cached_data and cached_data.expires_at else None,
                "created_at": widget.created_at.isoformat(),
                "updated_at": widget.updated_at.isoformat() if widget.updated_at else None
            }
            
        except Exception as e:
            logger.error(f"Error getting widget data: {e}")
            return {"error": str(e)}
    
    def cache_widget_data(self, widget_id: str, data_type: str, data_key: str, data_value: Dict, expires_in: int = 300) -> Dict:
        """Cache widget data"""
        try:
            # Remove old data for this widget and key
            self.db.query(WidgetData).filter(
                WidgetData.widget_id == widget_id,
                WidgetData.data_key == data_key
            ).delete()
            
            # Create new cache entry
            cache_entry = WidgetData(
                widget_id=widget_id,
                data_type=data_type,
                data_key=data_key,
                data_value=data_value,
                expires_at=datetime.now() + timedelta(seconds=expires_in)
            )
            
            self.db.add(cache_entry)
            self.db.commit()
            
            return {
                "widget_id": widget_id,
                "data_key": data_key,
                "status": "cached",
                "expires_at": cache_entry.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error caching widget data: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_cached_widget_data(self, widget_id: str, data_key: str) -> Optional[Dict]:
        """Get cached widget data"""
        try:
            cached_data = self.db.query(WidgetData).filter(
                WidgetData.widget_id == widget_id,
                WidgetData.data_key == data_key,
                WidgetData.is_valid == True,
                WidgetData.expires_at > datetime.now()
            ).order_by(WidgetData.updated_at.desc()).first()
            
            if cached_data:
                return cached_data.data_value
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached widget data: {e}")
            return None
    
    def create_dashboard_preset(self,
                              name: str,
                              description: str = None,
                              category: str = None,
                              layout_config: Dict = None,
                              widgets_config: Dict = None,
                              theme_config: Dict = None) -> Dict:
        """Create dashboard preset"""
        try:
            # Generate unique preset ID
            preset_id = f"PR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create preset
            preset = DashboardPreset(
                preset_id=preset_id,
                name=name,
                description=description,
                category=category,
                layout_config=layout_config,
                widgets_config=widgets_config,
                theme_config=theme_config
            )
            
            self.db.add(preset)
            self.db.commit()
            
            return {
                "preset_id": preset_id,
                "name": name,
                "status": "created",
                "message": "Dashboard preset created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating dashboard preset: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def apply_dashboard_preset(self, dashboard_id: str, preset_id: str) -> Dict:
        """Apply dashboard preset"""
        try:
            # Get preset
            preset = self.db.query(DashboardPreset).filter(DashboardPreset.preset_id == preset_id).first()
            if not preset:
                return {"error": "Preset not found"}
            
            # Get dashboard
            dashboard = self.db.query(Dashboard).filter(Dashboard.dashboard_id == dashboard_id).first()
            if not dashboard:
                return {"error": "Dashboard not found"}
            
            # Apply preset configuration
            if preset.layout_config:
                dashboard.layout_config = preset.layout_config
            
            if preset.theme_config:
                theme_config = preset.theme_config
                if 'theme' in theme_config:
                    dashboard.theme = theme_config['theme']
                if 'color_scheme' in theme_config:
                    dashboard.color_scheme = theme_config['color_scheme']
            
            # Clear existing widgets
            self.db.query(DashboardWidget).filter(DashboardWidget.dashboard_id == dashboard_id).delete()
            
            # Add widgets from preset
            if preset.widgets_config:
                for widget_config in preset.widgets_config:
                    widget = DashboardWidget(
                        widget_id=f"WD_{uuid.uuid4().hex[:8]}",
                        dashboard_id=dashboard_id,
                        widget_type=WidgetType(widget_config['widget_type']),
                        title=widget_config['title'],
                        position_x=widget_config.get('position_x', 0),
                        position_y=widget_config.get('position_y', 0),
                        width=widget_config.get('width', 1),
                        height=widget_config.get('height', 1),
                        config=widget_config.get('config', {})
                    )
                    self.db.add(widget)
            
            # Update usage count
            preset.usage_count += 1
            
            self.db.commit()
            
            return {
                "dashboard_id": dashboard_id,
                "preset_id": preset_id,
                "status": "applied",
                "message": "Dashboard preset applied successfully"
            }
            
        except Exception as e:
            logger.error(f"Error applying dashboard preset: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def list_dashboard_presets(self, category: str = None, limit: int = 50) -> List[Dict]:
        """List dashboard presets"""
        try:
            query = self.db.query(DashboardPreset).filter(DashboardPreset.is_public == True)
            
            if category:
                query = query.filter(DashboardPreset.category == category)
            
            presets = query.order_by(DashboardPreset.usage_count.desc()).limit(limit).all()
            
            preset_list = []
            for preset in presets:
                preset_list.append({
                    "preset_id": preset.preset_id,
                    "name": preset.name,
                    "description": preset.description,
                    "category": preset.category,
                    "is_featured": preset.is_featured,
                    "usage_count": preset.usage_count,
                    "created_at": preset.created_at.isoformat()
                })
            
            return preset_list
            
        except Exception as e:
            logger.error(f"Error listing dashboard presets: {e}")
            return []
    
    def create_widget_template(self,
                              name: str,
                              description: str = None,
                              widget_type: WidgetType = None,
                              default_config: Dict = None,
                              default_size: Dict = None) -> Dict:
        """Create widget template"""
        try:
            # Generate unique template ID
            template_id = f"WT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create template
            template = WidgetTemplate(
                template_id=template_id,
                name=name,
                description=description,
                widget_type=widget_type,
                default_config=default_config,
                default_size=default_size or {"width": 1, "height": 1}
            )
            
            self.db.add(template)
            self.db.commit()
            
            return {
                "template_id": template_id,
                "name": name,
                "status": "created",
                "message": "Widget template created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating widget template: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_widget_templates(self, widget_type: WidgetType = None) -> List[Dict]:
        """Get widget templates"""
        try:
            query = self.db.query(WidgetTemplate).filter(WidgetTemplate.is_public == True)
            
            if widget_type:
                query = query.filter(WidgetTemplate.widget_type == widget_type)
            
            templates = query.order_by(WidgetTemplate.usage_count.desc()).all()
            
            template_list = []
            for template in templates:
                template_list.append({
                    "template_id": template.template_id,
                    "name": template.name,
                    "description": template.description,
                    "widget_type": template.widget_type.value,
                    "default_config": template.default_config,
                    "default_size": template.default_size,
                    "is_featured": template.is_featured,
                    "usage_count": template.usage_count,
                    "created_at": template.created_at.isoformat()
                })
            
            return template_list
            
        except Exception as e:
            logger.error(f"Error getting widget templates: {e}")
            return []
    
    def delete_widget(self, widget_id: str) -> Dict:
        """Delete widget from dashboard"""
        try:
            # Delete widget
            deleted_count = self.db.query(DashboardWidget).filter(DashboardWidget.widget_id == widget_id).delete()
            
            if deleted_count == 0:
                return {"error": "Widget not found"}
            
            # Delete cached data
            self.db.query(WidgetData).filter(WidgetData.widget_id == widget_id).delete()
            
            self.db.commit()
            
            return {
                "widget_id": widget_id,
                "status": "deleted",
                "message": "Widget deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting widget: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def delete_dashboard(self, dashboard_id: str) -> Dict:
        """Delete dashboard and all widgets"""
        try:
            # Delete widgets
            self.db.query(DashboardWidget).filter(DashboardWidget.dashboard_id == dashboard_id).delete()
            
            # Delete cached data
            self.db.query(WidgetData).filter(WidgetData.widget_id.in_(
                self.db.query(DashboardWidget.widget_id).filter(DashboardWidget.dashboard_id == dashboard_id)
            )).delete()
            
            # Delete dashboard
            deleted_count = self.db.query(Dashboard).filter(Dashboard.dashboard_id == dashboard_id).delete()
            
            if deleted_count == 0:
                return {"error": "Dashboard not found"}
            
            self.db.commit()
            
            return {
                "dashboard_id": dashboard_id,
                "status": "deleted",
                "message": "Dashboard deleted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error deleting dashboard: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def list_dashboards(self, limit: int = 50, offset: int = 0) -> List[Dict]:
        """List all dashboards"""
        try:
            dashboards = self.db.query(Dashboard).order_by(Dashboard.created_at.desc()).offset(offset).limit(limit).all()
            
            dashboard_list = []
            for dashboard in dashboards:
                # Count widgets
                widget_count = self.db.query(DashboardWidget).filter(
                    DashboardWidget.dashboard_id == dashboard.dashboard_id
                ).count()
                
                dashboard_list.append({
                    "dashboard_id": dashboard.dashboard_id,
                    "name": dashboard.name,
                    "description": dashboard.description,
                    "layout_type": dashboard.layout_type.value,
                    "theme": dashboard.theme,
                    "color_scheme": dashboard.color_scheme,
                    "widget_count": widget_count,
                    "is_default": dashboard.is_default,
                    "is_public": dashboard.is_public,
                    "created_at": dashboard.created_at.isoformat(),
                    "updated_at": dashboard.updated_at.isoformat() if dashboard.updated_at else None
                })
            
            return dashboard_list
            
        except Exception as e:
            logger.error(f"Error listing dashboards: {e}")
            return []
