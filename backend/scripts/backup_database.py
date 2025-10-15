"""
Database Backup Script untuk MySQL
Membuat backup database ke format yang kompatibel dengan phpMyAdmin
"""
import os
import subprocess
import datetime
import logging
from pathlib import Path
import json
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Database backup utility untuk MySQL"""
    
    def __init__(self, 
                 host: str = "localhost",
                 port: int = 3306,
                 username: str = "root",
                 password: str = "",
                 database: str = "trading_platform",
                 backup_dir: str = "backups"):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.database = database
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, 
                     include_data: bool = True,
                     include_structure: bool = True,
                     compress: bool = True,
                     custom_filename: str = None) -> Dict:
        """Create database backup"""
        try:
            # Generate filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            if custom_filename:
                filename = f"{custom_filename}_{timestamp}"
            else:
                filename = f"{self.database}_backup_{timestamp}"
            
            if compress:
                filename += ".sql.gz"
            else:
                filename += ".sql"
            
            backup_path = self.backup_dir / filename
            
            # Build mysqldump command
            cmd = [
                "mysqldump",
                f"--host={self.host}",
                f"--port={self.port}",
                f"--user={self.username}",
                f"--password={self.password}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events"
            ]
            
            # Add structure/data options
            if include_structure and not include_data:
                cmd.append("--no-data")
            elif include_data and not include_structure:
                cmd.append("--no-create-info")
            elif not include_structure and not include_data:
                return {"error": "At least one of include_structure or include_data must be True"}
            
            # Add database name
            cmd.append(self.database)
            
            # Execute backup
            if compress:
                # Pipe through gzip
                with open(backup_path, 'wb') as f:
                    process1 = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    process2 = subprocess.Popen(['gzip'], stdin=process1.stdout, stdout=f, stderr=subprocess.PIPE)
                    process1.stdout.close()
                    stdout, stderr = process2.communicate()
                    
                    if process1.returncode != 0:
                        stderr1 = process1.stderr.read().decode()
                        return {"error": f"mysqldump failed: {stderr1}"}
                    if process2.returncode != 0:
                        stderr2 = stderr.decode()
                        return {"error": f"gzip failed: {stderr2}"}
            else:
                # Direct output
                with open(backup_path, 'w') as f:
                    result = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE, text=True)
                    if result.returncode != 0:
                        return {"error": f"mysqldump failed: {result.stderr}"}
            
            # Get file size
            file_size = backup_path.stat().st_size
            
            # Log backup creation
            logger.info(f"Database backup created: {backup_path} ({file_size} bytes)")
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "filename": filename,
                "file_size": file_size,
                "file_size_mb": round(file_size / (1024 * 1024), 2),
                "created_at": datetime.datetime.now().isoformat(),
                "database": self.database,
                "compressed": compress
            }
            
        except Exception as e:
            logger.error(f"Error creating database backup: {e}")
            return {"error": str(e)}
    
    def restore_backup(self, backup_path: str) -> Dict:
        """Restore database from backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return {"error": "Backup file not found"}
            
            # Build mysql command
            cmd = [
                "mysql",
                f"--host={self.host}",
                f"--port={self.port}",
                f"--user={self.username}",
                f"--password={self.password}",
                self.database
            ]
            
            # Handle compressed files
            if backup_file.suffix == '.gz':
                # Pipe through gunzip
                process1 = subprocess.Popen(['gunzip', '-c', str(backup_file)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                process2 = subprocess.Popen(cmd, stdin=process1.stdout, stderr=subprocess.PIPE)
                process1.stdout.close()
                stdout, stderr = process2.communicate()
                
                if process1.returncode != 0:
                    stderr1 = process1.stderr.read().decode()
                    return {"error": f"gunzip failed: {stderr1}"}
                if process2.returncode != 0:
                    stderr2 = stderr.decode()
                    return {"error": f"mysql restore failed: {stderr2}"}
            else:
                # Direct input
                with open(backup_file, 'r') as f:
                    result = subprocess.run(cmd, stdin=f, stderr=subprocess.PIPE, text=True)
                    if result.returncode != 0:
                        return {"error": f"mysql restore failed: {result.stderr}"}
            
            logger.info(f"Database restored from: {backup_path}")
            
            return {
                "success": True,
                "restored_from": str(backup_path),
                "restored_at": datetime.datetime.now().isoformat(),
                "database": self.database
            }
            
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return {"error": str(e)}
    
    def list_backups(self) -> List[Dict]:
        """List all available backups"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.sql*"):
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "size": stat.st_size,
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                    "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "compressed": backup_file.suffix == '.gz'
                })
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def cleanup_old_backups(self, keep_days: int = 30) -> Dict:
        """Clean up old backups"""
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=keep_days)
            deleted_count = 0
            deleted_size = 0
            
            for backup_file in self.backup_dir.glob("*.sql*"):
                file_time = datetime.datetime.fromtimestamp(backup_file.stat().st_ctime)
                if file_time < cutoff_date:
                    file_size = backup_file.stat().st_size
                    backup_file.unlink()
                    deleted_count += 1
                    deleted_size += file_size
                    logger.info(f"Deleted old backup: {backup_file.name}")
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "deleted_size_mb": round(deleted_size / (1024 * 1024), 2),
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old backups: {e}")
            return {"error": str(e)}
    
    def get_backup_info(self, backup_path: str) -> Dict:
        """Get information about a specific backup"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                return {"error": "Backup file not found"}
            
            stat = backup_file.stat()
            
            # Try to get database info from backup file
            database_info = self._extract_database_info(backup_file)
            
            return {
                "filename": backup_file.name,
                "path": str(backup_file),
                "size": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified_at": datetime.datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "compressed": backup_file.suffix == '.gz',
                "database_info": database_info
            }
            
        except Exception as e:
            logger.error(f"Error getting backup info: {e}")
            return {"error": str(e)}
    
    def _extract_database_info(self, backup_file: Path) -> Dict:
        """Extract database information from backup file"""
        try:
            # Read first few lines to get database info
            if backup_file.suffix == '.gz':
                import gzip
                with gzip.open(backup_file, 'rt') as f:
                    lines = [f.readline() for _ in range(20)]
            else:
                with open(backup_file, 'r') as f:
                    lines = [f.readline() for _ in range(20)]
            
            # Look for database name and version info
            database_name = None
            mysql_version = None
            
            for line in lines:
                if line.startswith('-- Current Database:'):
                    database_name = line.split(':')[1].strip()
                elif line.startswith('-- MySQL dump'):
                    mysql_version = line.strip()
            
            return {
                "database_name": database_name,
                "mysql_version": mysql_version,
                "has_structure": any('CREATE TABLE' in line for line in lines),
                "has_data": any('INSERT INTO' in line for line in lines)
            }
            
        except Exception as e:
            logger.error(f"Error extracting database info: {e}")
            return {}

def main():
    """Main function untuk command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Database Backup Utility")
    parser.add_argument("--host", default="localhost", help="MySQL host")
    parser.add_argument("--port", type=int, default=3306, help="MySQL port")
    parser.add_argument("--username", default="root", help="MySQL username")
    parser.add_argument("--password", default="", help="MySQL password")
    parser.add_argument("--database", default="trading_platform", help="Database name")
    parser.add_argument("--backup-dir", default="backups", help="Backup directory")
    parser.add_argument("--action", choices=["backup", "restore", "list", "cleanup"], required=True, help="Action to perform")
    parser.add_argument("--backup-file", help="Backup file for restore action")
    parser.add_argument("--keep-days", type=int, default=30, help="Days to keep backups (for cleanup)")
    parser.add_argument("--compress", action="store_true", help="Compress backup")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create backup utility
    backup_util = DatabaseBackup(
        host=args.host,
        port=args.port,
        username=args.username,
        password=args.password,
        database=args.database,
        backup_dir=args.backup_dir
    )
    
    if args.action == "backup":
        result = backup_util.create_backup(compress=args.compress)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Backup created successfully: {result['backup_path']}")
    
    elif args.action == "restore":
        if not args.backup_file:
            print("Error: --backup-file required for restore action")
            return
        result = backup_util.restore_backup(args.backup_file)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Database restored successfully from: {result['restored_from']}")
    
    elif args.action == "list":
        backups = backup_util.list_backups()
        if not backups:
            print("No backups found")
        else:
            print(f"Found {len(backups)} backups:")
            for backup in backups:
                print(f"  {backup['filename']} ({backup['size_mb']} MB) - {backup['created_at']}")
    
    elif args.action == "cleanup":
        result = backup_util.cleanup_old_backups(args.keep_days)
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Cleanup completed: {result['deleted_count']} files deleted ({result['deleted_size_mb']} MB)")

if __name__ == "__main__":
    main()
