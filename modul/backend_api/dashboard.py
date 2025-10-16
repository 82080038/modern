"""
Dashboard API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from app.database import get_db
from app.services.dashboard_service import DashboardService
from app.models.dashboard import WidgetType, DashboardLayout
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Pydantic schemas
class CreateDashboardRequest(BaseModel):
    name: str
    description: Optional[str] = None
    layout_type: str = "grid"  # grid, flexible, custom
    grid_columns: int = 4
    grid_rows: int = 3
    theme: str = "light"  # light, dark, auto
    color_scheme: str = "blue"  # blue, green, red, purple

class AddWidgetRequest(BaseModel):
    widget_type: str  # chart, watchlist, news, alerts, performance, market_overview, technical_indicators, pattern_recognition, backtest_results, custom
    title: str
    description: Optional[str] = None
    position_x: int = 0
    position_y: int = 0
    width: int = 1
    height: int = 1
    config: Optional[Dict] = None

class UpdateWidgetPositionRequest(BaseModel):
    position_x: int
    position_y: int
    width: Optional[int] = None
    height: Optional[int] = None

class UpdateWidgetConfigRequest(BaseModel):
    config: Dict

class CacheWidgetDataRequest(BaseModel):
    data_type: str
    data_key: str
    data_value: Dict
    expires_in: int = 300  # seconds

class CreatePresetRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    layout_config: Optional[Dict] = None
    widgets_config: Optional[Dict] = None
    theme_config: Optional[Dict] = None

class ApplyPresetRequest(BaseModel):
    preset_id: str

class CreateTemplateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    widget_type: str
    default_config: Optional[Dict] = None
    default_size: Optional[Dict] = None

@router.post("/create")
async def create_dashboard(
    dashboard_request: CreateDashboardRequest,
    db: Session = Depends(get_db)
):
    """Create new dashboard"""
    try:
        # Validate layout type
        valid_layouts = [lt.value for lt in DashboardLayout]
        if dashboard_request.layout_type not in valid_layouts:
            raise HTTPException(status_code=400, detail=f"Invalid layout type. Valid options: {valid_layouts}")
        
        # Convert to enum
        layout_type = DashboardLayout(dashboard_request.layout_type)
        
        # Create dashboard service
        dashboard_service = DashboardService(db)
        
        # Create dashboard
        result = dashboard_service.create_dashboard(
            name=dashboard_request.name,
            description=dashboard_request.description,
            layout_type=layout_type,
            grid_columns=dashboard_request.grid_columns,
            grid_rows=dashboard_request.grid_rows,
            theme=dashboard_request.theme,
            color_scheme=dashboard_request.color_scheme
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{dashboard_id}/add-widget")
async def add_widget_to_dashboard(
    dashboard_id: str,
    widget_request: AddWidgetRequest,
    db: Session = Depends(get_db)
):
    """Add widget to dashboard"""
    try:
        # Validate widget type
        valid_types = [wt.value for wt in WidgetType]
        if widget_request.widget_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid widget type. Valid options: {valid_types}")
        
        # Convert to enum
        widget_type = WidgetType(widget_request.widget_type)
        
        # Create dashboard service
        dashboard_service = DashboardService(db)
        
        # Add widget
        result = dashboard_service.add_widget_to_dashboard(
            dashboard_id=dashboard_id,
            widget_type=widget_type,
            title=widget_request.title,
            position_x=widget_request.position_x,
            position_y=widget_request.position_y,
            width=widget_request.width,
            height=widget_request.height,
            config=widget_request.config
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding widget to dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/widget/{widget_id}/position")
async def update_widget_position(
    widget_id: str,
    position_request: UpdateWidgetPositionRequest,
    db: Session = Depends(get_db)
):
    """Update widget position and size"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.update_widget_position(
            widget_id=widget_id,
            position_x=position_request.position_x,
            position_y=position_request.position_y,
            width=position_request.width,
            height=position_request.height
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating widget position: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/widget/{widget_id}/config")
async def update_widget_config(
    widget_id: str,
    config_request: UpdateWidgetConfigRequest,
    db: Session = Depends(get_db)
):
    """Update widget configuration"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.update_widget_config(
            widget_id=widget_id,
            config=config_request.config
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating widget config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{dashboard_id}")
async def get_dashboard_data(
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """Get dashboard data with widgets"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.get_dashboard_data(dashboard_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget/{widget_id}")
async def get_widget_data(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """Get widget data and configuration"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.get_widget_data(widget_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting widget data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/widget/{widget_id}/cache")
async def cache_widget_data(
    widget_id: str,
    cache_request: CacheWidgetDataRequest,
    db: Session = Depends(get_db)
):
    """Cache widget data"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.cache_widget_data(
            widget_id=widget_id,
            data_type=cache_request.data_type,
            data_key=cache_request.data_key,
            data_value=cache_request.data_value,
            expires_in=cache_request.expires_in
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error caching widget data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget/{widget_id}/cache/{data_key}")
async def get_cached_widget_data(
    widget_id: str,
    data_key: str,
    db: Session = Depends(get_db)
):
    """Get cached widget data"""
    try:
        dashboard_service = DashboardService(db)
        cached_data = dashboard_service.get_cached_widget_data(widget_id, data_key)
        
        if cached_data is None:
            raise HTTPException(status_code=404, detail="Cached data not found or expired")
        
        return {
            "widget_id": widget_id,
            "data_key": data_key,
            "data": cached_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting cached widget data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/preset/create")
async def create_dashboard_preset(
    preset_request: CreatePresetRequest,
    db: Session = Depends(get_db)
):
    """Create dashboard preset"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.create_dashboard_preset(
            name=preset_request.name,
            description=preset_request.description,
            category=preset_request.category,
            layout_config=preset_request.layout_config,
            widgets_config=preset_request.widgets_config,
            theme_config=preset_request.theme_config
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating dashboard preset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{dashboard_id}/apply-preset")
async def apply_dashboard_preset(
    dashboard_id: str,
    preset_request: ApplyPresetRequest,
    db: Session = Depends(get_db)
):
    """Apply dashboard preset"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.apply_dashboard_preset(
            dashboard_id=dashboard_id,
            preset_id=preset_request.preset_id
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error applying dashboard preset: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/presets")
async def list_dashboard_presets(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, description="Maximum number of presets to return"),
    db: Session = Depends(get_db)
):
    """List dashboard presets"""
    try:
        dashboard_service = DashboardService(db)
        presets = dashboard_service.list_dashboard_presets(category=category, limit=limit)
        
        return {
            "presets": presets,
            "total_count": len(presets)
        }
        
    except Exception as e:
        logger.error(f"Error listing dashboard presets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/template/create")
async def create_widget_template(
    template_request: CreateTemplateRequest,
    db: Session = Depends(get_db)
):
    """Create widget template"""
    try:
        # Validate widget type
        valid_types = [wt.value for wt in WidgetType]
        if template_request.widget_type not in valid_types:
            raise HTTPException(status_code=400, detail=f"Invalid widget type. Valid options: {valid_types}")
        
        # Convert to enum
        widget_type = WidgetType(template_request.widget_type)
        
        dashboard_service = DashboardService(db)
        result = dashboard_service.create_widget_template(
            name=template_request.name,
            description=template_request.description,
            widget_type=widget_type,
            default_config=template_request.default_config,
            default_size=template_request.default_size
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating widget template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_widget_templates(
    widget_type: Optional[str] = Query(None, description="Filter by widget type"),
    db: Session = Depends(get_db)
):
    """Get widget templates"""
    try:
        dashboard_service = DashboardService(db)
        
        # Convert widget type if provided
        widget_type_enum = None
        if widget_type:
            valid_types = [wt.value for wt in WidgetType]
            if widget_type not in valid_types:
                raise HTTPException(status_code=400, detail=f"Invalid widget type. Valid options: {valid_types}")
            widget_type_enum = WidgetType(widget_type)
        
        templates = dashboard_service.get_widget_templates(widget_type=widget_type_enum)
        
        return {
            "templates": templates,
            "total_count": len(templates)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting widget templates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/widget/{widget_id}")
async def delete_widget(
    widget_id: str,
    db: Session = Depends(get_db)
):
    """Delete widget from dashboard"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.delete_widget(widget_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting widget: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{dashboard_id}")
async def delete_dashboard(
    dashboard_id: str,
    db: Session = Depends(get_db)
):
    """Delete dashboard and all widgets"""
    try:
        dashboard_service = DashboardService(db)
        result = dashboard_service.delete_dashboard(dashboard_id)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_dashboards(
    limit: int = Query(50, description="Maximum number of dashboards to return"),
    offset: int = Query(0, description="Number of dashboards to skip"),
    db: Session = Depends(get_db)
):
    """List all dashboards"""
    try:
        dashboard_service = DashboardService(db)
        dashboards = dashboard_service.list_dashboards(limit=limit, offset=offset)
        
        return {
            "dashboards": dashboards,
            "total_count": len(dashboards)
        }
        
    except Exception as e:
        logger.error(f"Error listing dashboards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/widget-types")
async def get_available_widget_types(db: Session = Depends(get_db)):
    """Get available widget types"""
    try:
        widget_types = []
        for widget_type in WidgetType:
            widget_types.append({
                "type": widget_type.value,
                "name": widget_type.value.replace('_', ' ').title(),
                "description": f"{widget_type.value.replace('_', ' ').title()} widget"
            })
        
        return {
            "widget_types": widget_types,
            "total_count": len(widget_types)
        }
        
    except Exception as e:
        logger.error(f"Error getting widget types: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/layout-types")
async def get_available_layout_types(db: Session = Depends(get_db)):
    """Get available layout types"""
    try:
        layout_types = []
        for layout_type in DashboardLayout:
            layout_types.append({
                "type": layout_type.value,
                "name": layout_type.value.replace('_', ' ').title(),
                "description": f"{layout_type.value.replace('_', ' ').title()} layout"
            })
        
        return {
            "layout_types": layout_types,
            "total_count": len(layout_types)
        }
        
    except Exception as e:
        logger.error(f"Error getting layout types: {e}")
        raise HTTPException(status_code=500, detail=str(e))
