"""
Security API Endpoints untuk Development (Single User)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, Request
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.database import get_db
from app.services.security_service import SecurityService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/security", tags=["Security"])

# Pydantic schemas
class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id: str
    username: str
    role: str
    session_id: str
    expires_at: str
    message: str

class SessionResponse(BaseModel):
    valid: bool
    user_id: str
    username: str
    role: str
    session_id: str
    expires_at: str

class SecurityLogResponse(BaseModel):
    log_id: str
    event_type: str
    user_id: Optional[str]
    session_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    event_data: Optional[Dict]
    risk_level: str
    is_suspicious: bool
    created_at: str

class SecurityMetricsResponse(BaseModel):
    period_days: int
    total_logins: int
    successful_logins: int
    failed_logins: int
    login_success_rate: float
    suspicious_activities: int
    blocked_attempts: int
    active_sessions: int
    security_score: int

@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Login user"""
    try:
        # Get client IP and User-Agent
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Create security service
        security_service = SecurityService(db)
        
        # Authenticate user
        result = security_service.authenticate_user(
            username=login_request.username,
            password=login_request.password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if "error" in result:
            raise HTTPException(status_code=401, detail=result["error"])
        
        return LoginResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout(
    session_id: str = Body(..., description="Session ID to logout"),
    db: Session = Depends(get_db)
):
    """Logout user"""
    try:
        security_service = SecurityService(db)
        result = security_service.logout_user(session_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in logout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate-session", response_model=SessionResponse)
async def validate_session(
    session_id: str = Query(..., description="Session ID to validate"),
    db: Session = Depends(get_db)
):
    """Validate user session"""
    try:
        security_service = SecurityService(db)
        result = security_service.validate_session(session_id)
        
        if "error" in result:
            raise HTTPException(status_code=401, detail=result["error"])
        
        return SessionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs", response_model=List[SecurityLogResponse])
async def get_security_logs(
    limit: int = Query(100, description="Maximum number of logs to return"),
    offset: int = Query(0, description="Number of logs to skip"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    db: Session = Depends(get_db)
):
    """Get security logs"""
    try:
        security_service = SecurityService(db)
        logs = security_service.get_security_logs(
            limit=limit,
            offset=offset,
            event_type=event_type
        )
        
        return logs
        
    except Exception as e:
        logger.error(f"Error getting security logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sessions")
async def get_active_sessions(
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    db: Session = Depends(get_db)
):
    """Get active sessions"""
    try:
        security_service = SecurityService(db)
        sessions = security_service.get_active_sessions(user_id=user_id)
        
        return {
            "sessions": sessions,
            "total_count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Error getting active sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def revoke_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Revoke specific session"""
    try:
        security_service = SecurityService(db)
        result = security_service.revoke_session(session_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/user/{user_id}")
async def revoke_all_user_sessions(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Revoke all sessions for a user"""
    try:
        security_service = SecurityService(db)
        result = security_service.revoke_all_sessions(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error revoking all user sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics", response_model=SecurityMetricsResponse)
async def get_security_metrics(
    days: int = Query(7, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """Get security metrics"""
    try:
        security_service = SecurityService(db)
        metrics = security_service.get_security_metrics(days=days)
        
        if "error" in metrics:
            raise HTTPException(status_code=400, detail=metrics["error"])
        
        return SecurityMetricsResponse(**metrics)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting security metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/setup")
async def setup_default_user(db: Session = Depends(get_db)):
    """Setup default user for development"""
    try:
        security_service = SecurityService(db)
        result = security_service.create_default_user()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error setting up default user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cleanup")
async def cleanup_expired_sessions(db: Session = Depends(get_db)):
    """Clean up expired sessions"""
    try:
        security_service = SecurityService(db)
        result = security_service.cleanup_expired_sessions()
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_security_status(db: Session = Depends(get_db)):
    """Get current security status"""
    try:
        security_service = SecurityService(db)
        
        # Get basic metrics
        metrics = security_service.get_security_metrics(days=1)
        active_sessions = security_service.get_active_sessions()
        
        # Get recent security events
        recent_logs = security_service.get_security_logs(limit=10)
        
        # Calculate status
        status = "healthy"
        if metrics.get("security_score", 0) < 50:
            status = "warning"
        if metrics.get("suspicious_activities", 0) > 5:
            status = "critical"
        
        return {
            "status": status,
            "security_score": metrics.get("security_score", 0),
            "active_sessions": len(active_sessions),
            "recent_events": len(recent_logs),
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting security status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Middleware function untuk authentication
async def get_current_user(session_id: str = None, db: Session = Depends(get_db)):
    """Get current authenticated user"""
    if not session_id:
        raise HTTPException(status_code=401, detail="Session ID required")
    
    security_service = SecurityService(db)
    result = security_service.validate_session(session_id)
    
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    
    return result

# Dependency untuk protected routes
async def require_auth(session_id: str = None, db: Session = Depends(get_db)):
    """Require authentication for protected routes"""
    return await get_current_user(session_id, db)
