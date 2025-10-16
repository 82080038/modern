"""
Two-Factor Authentication API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.two_factor_service import TwoFactorService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/two-factor", tags=["Two-Factor Authentication"])

# Pydantic schemas
class TwoFactorSetupResponse(BaseModel):
    secret: str
    qr_code: str
    manual_entry_key: str
    issuer: str
    account_name: str

class TwoFactorVerifyRequest(BaseModel):
    token: str

class TwoFactorVerifyResponse(BaseModel):
    valid: bool
    message: str

class TwoFactorEnableRequest(BaseModel):
    token: str

class TwoFactorDisableRequest(BaseModel):
    token: str

class TwoFactorStatusResponse(BaseModel):
    is_enabled: bool
    has_backup_codes: bool

class BackupCodesResponse(BaseModel):
    backup_codes: list
    message: str

@router.post("/setup/{user_id}", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Setup Two-Factor Authentication untuk user"""
    try:
        service = TwoFactorService(db)
        result = service.generate_secret(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return TwoFactorSetupResponse(**result)
        
    except Exception as e:
        logger.error(f"Error setting up 2FA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify/{user_id}", response_model=TwoFactorVerifyResponse)
async def verify_two_factor_token(
    user_id: int,
    request: TwoFactorVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify TOTP token"""
    try:
        service = TwoFactorService(db)
        result = service.verify_token(user_id, request.token)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return TwoFactorVerifyResponse(**result)
        
    except Exception as e:
        logger.error(f"Error verifying 2FA token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/enable/{user_id}")
async def enable_two_factor(
    user_id: int,
    request: TwoFactorEnableRequest,
    db: Session = Depends(get_db)
):
    """Enable Two-Factor Authentication"""
    try:
        service = TwoFactorService(db)
        result = service.enable_2fa(user_id, request.token)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error enabling 2FA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/disable/{user_id}")
async def disable_two_factor(
    user_id: int,
    request: TwoFactorDisableRequest,
    db: Session = Depends(get_db)
):
    """Disable Two-Factor Authentication"""
    try:
        service = TwoFactorService(db)
        result = service.disable_2fa(user_id, request.token)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except Exception as e:
        logger.error(f"Error disabling 2FA: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{user_id}", response_model=TwoFactorStatusResponse)
async def get_two_factor_status(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get Two-Factor Authentication status"""
    try:
        service = TwoFactorService(db)
        is_enabled = service.is_2fa_enabled(user_id)
        
        # Check if user has backup codes
        from app.models.security import TwoFactorAuth
        two_factor = db.query(TwoFactorAuth).filter(
            TwoFactorAuth.user_id == user_id
        ).first()
        
        has_backup_codes = two_factor and two_factor.backup_codes and len(two_factor.backup_codes) > 0
        
        return TwoFactorStatusResponse(
            is_enabled=is_enabled,
            has_backup_codes=has_backup_codes
        )
        
    except Exception as e:
        logger.error(f"Error getting 2FA status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/backup-codes/{user_id}", response_model=BackupCodesResponse)
async def generate_backup_codes(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Generate backup codes untuk 2FA"""
    try:
        service = TwoFactorService(db)
        result = service.generate_backup_codes(user_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return BackupCodesResponse(**result)
        
    except Exception as e:
        logger.error(f"Error generating backup codes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify-backup/{user_id}")
async def verify_backup_code(
    user_id: int,
    request: TwoFactorVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify backup code"""
    try:
        service = TwoFactorService(db)
        is_valid = service.verify_backup_code(user_id, request.token)
        
        if is_valid:
            return {"valid": True, "message": "Backup code verified successfully"}
        else:
            return {"valid": False, "message": "Invalid backup code"}
        
    except Exception as e:
        logger.error(f"Error verifying backup code: {e}")
        raise HTTPException(status_code=500, detail=str(e))
