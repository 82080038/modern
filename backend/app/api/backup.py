"""
Backup API Endpoints untuk MySQL Database
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime
from app.database import get_db
from app.scripts.backup_database import DatabaseBackup
from pydantic import BaseModel
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/backup", tags=["Backup"])

# Pydantic schemas
class CreateBackupRequest(BaseModel):
    include_data: bool = True
    include_structure: bool = True
    compress: bool = True
    custom_filename: Optional[str] = None

class RestoreBackupRequest(BaseModel):
    backup_path: str

class BackupInfoResponse(BaseModel):
    filename: str
    path: str
    size: int
    size_mb: float
    created_at: str
    modified_at: str
    compressed: bool
    database_info: Dict

class BackupListResponse(BaseModel):
    backups: List[BackupInfoResponse]
    total_count: int
    total_size_mb: float

# Global backup utility instance
backup_util = None

def get_backup_util():
    """Get backup utility instance"""
    global backup_util
    if backup_util is None:
        # Get database config from environment or use defaults
        backup_util = DatabaseBackup(
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "3306")),
            username=os.getenv("DB_USERNAME", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "trading_platform"),
            backup_dir=os.getenv("BACKUP_DIR", "backups")
        )
    return backup_util

@router.post("/create")
async def create_backup(
    backup_request: CreateBackupRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create database backup"""
    try:
        backup_util = get_backup_util()
        
        # Create backup
        result = backup_util.create_backup(
            include_data=backup_request.include_data,
            include_structure=backup_request.include_structure,
            compress=backup_request.compress,
            custom_filename=backup_request.custom_filename
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Log backup creation
        logger.info(f"Database backup created: {result['backup_path']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/restore")
async def restore_backup(
    restore_request: RestoreBackupRequest,
    db: Session = Depends(get_db)
):
    """Restore database from backup"""
    try:
        backup_util = get_backup_util()
        
        # Restore backup
        result = backup_util.restore_backup(restore_request.backup_path)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Log backup restoration
        logger.info(f"Database restored from: {result['restored_from']}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list", response_model=BackupListResponse)
async def list_backups(db: Session = Depends(get_db)):
    """List all available backups"""
    try:
        backup_util = get_backup_util()
        backups = backup_util.list_backups()
        
        if not backups:
            return BackupListResponse(
                backups=[],
                total_count=0,
                total_size_mb=0.0
            )
        
        # Calculate total size
        total_size_mb = sum(backup['size_mb'] for backup in backups)
        
        # Convert to response format
        backup_list = []
        for backup in backups:
            backup_list.append(BackupInfoResponse(
                filename=backup['filename'],
                path=backup['path'],
                size=backup['size'],
                size_mb=backup['size_mb'],
                created_at=backup['created_at'],
                modified_at=backup['modified_at'],
                compressed=backup['compressed'],
                database_info={}
            ))
        
        return BackupListResponse(
            backups=backup_list,
            total_count=len(backup_list),
            total_size_mb=total_size_mb
        )
        
    except Exception as e:
        logger.error(f"Error listing backups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info/{backup_filename}")
async def get_backup_info(
    backup_filename: str,
    db: Session = Depends(get_db)
):
    """Get information about a specific backup"""
    try:
        backup_util = get_backup_util()
        
        # Construct full path
        backup_path = os.path.join(backup_util.backup_dir, backup_filename)
        
        # Get backup info
        result = backup_util.get_backup_info(backup_path)
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting backup info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cleanup")
async def cleanup_old_backups(
    keep_days: int = Query(30, description="Number of days to keep backups"),
    db: Session = Depends(get_db)
):
    """Clean up old backups"""
    try:
        backup_util = get_backup_util()
        
        # Cleanup old backups
        result = backup_util.cleanup_old_backups(keep_days)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        # Log cleanup
        logger.info(f"Backup cleanup completed: {result['deleted_count']} files deleted")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up backups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_backup_status(db: Session = Depends(get_db)):
    """Get backup system status"""
    try:
        backup_util = get_backup_util()
        
        # Get backup list
        backups = backup_util.list_backups()
        
        # Calculate statistics
        total_backups = len(backups)
        total_size_mb = sum(backup['size_mb'] for backup in backups)
        
        # Get latest backup
        latest_backup = backups[0] if backups else None
        
        # Check backup directory
        backup_dir_exists = os.path.exists(backup_util.backup_dir)
        backup_dir_writable = os.access(backup_util.backup_dir, os.W_OK) if backup_dir_exists else False
        
        return {
            "backup_directory": str(backup_util.backup_dir),
            "directory_exists": backup_dir_exists,
            "directory_writable": backup_dir_writable,
            "total_backups": total_backups,
            "total_size_mb": round(total_size_mb, 2),
            "latest_backup": {
                "filename": latest_backup['filename'],
                "created_at": latest_backup['created_at'],
                "size_mb": latest_backup['size_mb']
            } if latest_backup else None,
            "database_config": {
                "host": backup_util.host,
                "port": backup_util.port,
                "database": backup_util.database,
                "username": backup_util.username
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting backup status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/schedule")
async def schedule_backup(
    schedule_type: str = Body(..., description="Schedule type: daily, weekly, monthly"),
    db: Session = Depends(get_db)
):
    """Schedule automatic backups (placeholder for future implementation)"""
    try:
        # This would integrate with a task scheduler like Celery
        # For now, just return a placeholder response
        
        return {
            "message": "Backup scheduling not yet implemented",
            "schedule_type": schedule_type,
            "note": "Use the /create endpoint to create manual backups"
        }
        
    except Exception as e:
        logger.error(f"Error scheduling backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/download/{backup_filename}")
async def download_backup(
    backup_filename: str,
    db: Session = Depends(get_db)
):
    """Download backup file (placeholder for future implementation)"""
    try:
        backup_util = get_backup_util()
        backup_path = os.path.join(backup_util.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            raise HTTPException(status_code=404, detail="Backup file not found")
        
        # This would return the file for download
        # For now, just return file info
        file_stat = os.stat(backup_path)
        
        return {
            "filename": backup_filename,
            "path": backup_path,
            "size": file_stat.st_size,
            "size_mb": round(file_stat.st_size / (1024 * 1024), 2),
            "note": "File download not yet implemented. Use the file path to access the backup."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading backup: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-connection")
async def test_backup_connection(db: Session = Depends(get_db)):
    """Test database connection for backup"""
    try:
        backup_util = get_backup_util()
        
        # Test connection by creating a small test backup
        test_result = backup_util.create_backup(
            include_data=False,
            include_structure=False,
            compress=False,
            custom_filename="connection_test"
        )
        
        if "error" in test_result:
            return {
                "connection_status": "failed",
                "error": test_result["error"]
            }
        
        # Clean up test backup
        test_file = test_result["backup_path"]
        if os.path.exists(test_file):
            os.remove(test_file)
        
        return {
            "connection_status": "success",
            "message": "Database connection test successful",
            "database": backup_util.database,
            "host": backup_util.host,
            "port": backup_util.port
        }
        
    except Exception as e:
        logger.error(f"Error testing backup connection: {e}")
        return {
            "connection_status": "failed",
            "error": str(e)
        }
