"""
Security Service untuk Development (Single User)
"""
from sqlalchemy.orm import Session
from app.models.security import (
    User, UserSession, SecurityLog, SecuritySettings, IPWhitelist, SecurityMetrics,
    UserRole, SessionStatus
)
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import hashlib
import secrets
import uuid
import logging
import json
from passlib.context import CryptContext

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SecurityService:
    """Service untuk security operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.max_failed_attempts = 5
        self.lockout_duration = 30  # minutes
        self.session_duration = 24  # hours
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if not salt:
            salt = secrets.token_hex(16)
        
        # Combine password and salt
        salted_password = password + salt
        
        # Hash using bcrypt
        password_hash = pwd_context.hash(salted_password)
        
        return password_hash, salt
    
    def verify_password(self, password: str, password_hash: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            salted_password = password + salt
            return pwd_context.verify(salted_password, password_hash)
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    def create_default_user(self) -> Dict:
        """Create default user for development"""
        try:
            # Check if user already exists
            existing_user = self.db.query(User).filter(User.username == "admin").first()
            if existing_user:
                return {"message": "Default user already exists", "user_id": existing_user.user_id}
            
            # Create default user
            user_id = f"USER_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            password = "admin123"  # Default password for development
            password_hash, salt = self.hash_password(password)
            
            user = User(
                user_id=user_id,
                username="admin",
                email="admin@tradingplatform.local",
                password_hash=password_hash,
                salt=salt,
                full_name="Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            
            self.db.add(user)
            self.db.commit()
            
            # Log security event
            self._log_security_event(
                event_type="user_created",
                user_id=user_id,
                event_data={"username": "admin", "role": "admin"}
            )
            
            return {
                "user_id": user_id,
                "username": "admin",
                "password": password,
                "message": "Default user created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating default user: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None, user_agent: str = None) -> Dict:
        """Authenticate user"""
        try:
            # Get user
            user = self.db.query(User).filter(User.username == username).first()
            
            if not user:
                self._log_security_event(
                    event_type="failed_login",
                    event_data={"username": username, "reason": "user_not_found", "ip_address": ip_address}
                )
                return {"error": "Invalid credentials"}
            
            # Check if account is locked
            if user.account_locked_until and user.account_locked_until > datetime.now():
                self._log_security_event(
                    event_type="failed_login",
                    user_id=user.user_id,
                    event_data={"username": username, "reason": "account_locked", "ip_address": ip_address}
                )
                return {"error": "Account is locked due to too many failed attempts"}
            
            # Check if user is active
            if not user.is_active:
                self._log_security_event(
                    event_type="failed_login",
                    user_id=user.user_id,
                    event_data={"username": username, "reason": "account_inactive", "ip_address": ip_address}
                )
                return {"error": "Account is inactive"}
            
            # Verify password
            if not self.verify_password(password, user.password_hash, user.salt):
                # Increment failed attempts
                user.failed_login_attempts += 1
                user.last_failed_login = datetime.now()
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.max_failed_attempts:
                    user.account_locked_until = datetime.now() + timedelta(minutes=self.lockout_duration)
                    self._log_security_event(
                        event_type="account_locked",
                        user_id=user.user_id,
                        event_data={"username": username, "failed_attempts": user.failed_login_attempts, "ip_address": ip_address}
                    )
                
                self.db.commit()
                
                self._log_security_event(
                    event_type="failed_login",
                    user_id=user.user_id,
                    event_data={"username": username, "reason": "invalid_password", "ip_address": ip_address}
                )
                return {"error": "Invalid credentials"}
            
            # Reset failed attempts on successful login
            user.failed_login_attempts = 0
            user.last_login = datetime.now()
            user.account_locked_until = None
            
            # Create session
            session_result = self._create_session(user.user_id, ip_address, user_agent)
            
            self.db.commit()
            
            # Log successful login
            self._log_security_event(
                event_type="successful_login",
                user_id=user.user_id,
                event_data={"username": username, "ip_address": ip_address}
            )
            
            return {
                "user_id": user.user_id,
                "username": user.username,
                "role": user.role.value,
                "session_id": session_result["session_id"],
                "expires_at": session_result["expires_at"],
                "message": "Authentication successful"
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _create_session(self, user_id: str, ip_address: str = None, user_agent: str = None) -> Dict:
        """Create user session"""
        try:
            # Generate session ID
            session_id = f"SESS_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:16]}"
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(hours=self.session_duration)
            
            # Create session
            session = UserSession(
                session_id=session_id,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
                is_secure=False  # Set to True in production with HTTPS
            )
            
            self.db.add(session)
            
            return {
                "session_id": session_id,
                "expires_at": expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise e
    
    def validate_session(self, session_id: str) -> Dict:
        """Validate user session"""
        try:
            session = self.db.query(UserSession).filter(
                UserSession.session_id == session_id,
                UserSession.status == SessionStatus.ACTIVE
            ).first()
            
            if not session:
                return {"error": "Invalid session"}
            
            # Check if session is expired
            if session.expires_at < datetime.now():
                session.status = SessionStatus.EXPIRED
                self.db.commit()
                return {"error": "Session expired"}
            
            # Update last activity
            session.last_activity = datetime.now()
            self.db.commit()
            
            # Get user info
            user = self.db.query(User).filter(User.user_id == session.user_id).first()
            
            return {
                "valid": True,
                "user_id": session.user_id,
                "username": user.username,
                "role": user.role.value,
                "session_id": session_id,
                "expires_at": session.expires_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return {"error": str(e)}
    
    def logout_user(self, session_id: str) -> Dict:
        """Logout user and revoke session"""
        try:
            session = self.db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if not session:
                return {"error": "Session not found"}
            
            # Revoke session
            session.status = SessionStatus.REVOKED
            session.revoked_at = datetime.now()
            
            self.db.commit()
            
            # Log logout event
            self._log_security_event(
                event_type="logout",
                user_id=session.user_id,
                session_id=session_id,
                event_data={"session_duration": str(datetime.now() - session.created_at)}
            )
            
            return {
                "message": "Logged out successfully",
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error logging out user: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def _log_security_event(self, event_type: str, user_id: str = None, session_id: str = None, 
                           ip_address: str = None, user_agent: str = None, event_data: Dict = None):
        """Log security event"""
        try:
            log_id = f"LOG_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Determine risk level
            risk_level = "low"
            is_suspicious = False
            
            if event_type in ["failed_login", "account_locked", "suspicious_activity"]:
                risk_level = "high"
                is_suspicious = True
            elif event_type in ["successful_login", "logout"]:
                risk_level = "low"
            elif event_type in ["user_created", "session_created"]:
                risk_level = "medium"
            
            # Create security log
            log = SecurityLog(
                log_id=log_id,
                event_type=event_type,
                user_id=user_id,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                event_data=event_data,
                risk_level=risk_level,
                is_suspicious=is_suspicious
            )
            
            self.db.add(log)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def get_security_logs(self, limit: int = 100, offset: int = 0, event_type: str = None) -> List[Dict]:
        """Get security logs"""
        try:
            query = self.db.query(SecurityLog)
            
            if event_type:
                query = query.filter(SecurityLog.event_type == event_type)
            
            logs = query.order_by(SecurityLog.created_at.desc()).offset(offset).limit(limit).all()
            
            log_list = []
            for log in logs:
                log_list.append({
                    "log_id": log.log_id,
                    "event_type": log.event_type,
                    "user_id": log.user_id,
                    "session_id": log.session_id,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent,
                    "event_data": log.event_data,
                    "risk_level": log.risk_level,
                    "is_suspicious": log.is_suspicious,
                    "created_at": log.created_at.isoformat()
                })
            
            return log_list
            
        except Exception as e:
            logger.error(f"Error getting security logs: {e}")
            return []
    
    def get_active_sessions(self, user_id: str = None) -> List[Dict]:
        """Get active sessions"""
        try:
            query = self.db.query(UserSession).filter(
                UserSession.status == SessionStatus.ACTIVE,
                UserSession.expires_at > datetime.now()
            )
            
            if user_id:
                query = query.filter(UserSession.user_id == user_id)
            
            sessions = query.order_by(UserSession.last_activity.desc()).all()
            
            session_list = []
            for session in sessions:
                session_list.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "ip_address": session.ip_address,
                    "user_agent": session.user_agent,
                    "is_secure": session.is_secure,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "expires_at": session.expires_at.isoformat()
                })
            
            return session_list
            
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []
    
    def revoke_session(self, session_id: str) -> Dict:
        """Revoke specific session"""
        try:
            session = self.db.query(UserSession).filter(
                UserSession.session_id == session_id
            ).first()
            
            if not session:
                return {"error": "Session not found"}
            
            session.status = SessionStatus.REVOKED
            session.revoked_at = datetime.now()
            
            self.db.commit()
            
            # Log revocation
            self._log_security_event(
                event_type="session_revoked",
                user_id=session.user_id,
                session_id=session_id,
                event_data={"revoked_by": "admin"}
            )
            
            return {
                "message": "Session revoked successfully",
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error revoking session: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def revoke_all_sessions(self, user_id: str) -> Dict:
        """Revoke all sessions for a user"""
        try:
            sessions = self.db.query(UserSession).filter(
                UserSession.user_id == user_id,
                UserSession.status == SessionStatus.ACTIVE
            ).all()
            
            revoked_count = 0
            for session in sessions:
                session.status = SessionStatus.REVOKED
                session.revoked_at = datetime.now()
                revoked_count += 1
            
            self.db.commit()
            
            # Log revocation
            self._log_security_event(
                event_type="all_sessions_revoked",
                user_id=user_id,
                event_data={"revoked_count": revoked_count}
            )
            
            return {
                "message": f"Revoked {revoked_count} sessions successfully",
                "revoked_count": revoked_count
            }
            
        except Exception as e:
            logger.error(f"Error revoking all sessions: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_security_metrics(self, days: int = 7) -> Dict:
        """Get security metrics for the last N days"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Get metrics for the period
            metrics = self.db.query(SecurityMetrics).filter(
                SecurityMetrics.date >= start_date,
                SecurityMetrics.date <= end_date
            ).all()
            
            # Calculate totals
            total_logins = sum(m.total_logins for m in metrics)
            successful_logins = sum(m.successful_logins for m in metrics)
            failed_logins = sum(m.failed_logins for m in metrics)
            suspicious_activities = sum(m.suspicious_activities for m in metrics)
            blocked_attempts = sum(m.blocked_attempts for m in metrics)
            
            # Get current active sessions
            active_sessions = self.db.query(UserSession).filter(
                UserSession.status == SessionStatus.ACTIVE,
                UserSession.expires_at > datetime.now()
            ).count()
            
            return {
                "period_days": days,
                "total_logins": total_logins,
                "successful_logins": successful_logins,
                "failed_logins": failed_logins,
                "login_success_rate": (successful_logins / total_logins * 100) if total_logins > 0 else 0,
                "suspicious_activities": suspicious_activities,
                "blocked_attempts": blocked_attempts,
                "active_sessions": active_sessions,
                "security_score": self._calculate_security_score(successful_logins, failed_logins, suspicious_activities)
            }
            
        except Exception as e:
            logger.error(f"Error getting security metrics: {e}")
            return {"error": str(e)}
    
    def _calculate_security_score(self, successful_logins: int, failed_logins: int, suspicious_activities: int) -> int:
        """Calculate security score (0-100)"""
        try:
            if successful_logins == 0:
                return 0
            
            # Base score from login success rate
            success_rate = successful_logins / (successful_logins + failed_logins)
            base_score = int(success_rate * 100)
            
            # Penalty for suspicious activities
            penalty = min(suspicious_activities * 5, 50)  # Max 50 point penalty
            
            # Final score
            final_score = max(base_score - penalty, 0)
            
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating security score: {e}")
            return 0
    
    def cleanup_expired_sessions(self) -> Dict:
        """Clean up expired sessions"""
        try:
            # Mark expired sessions
            expired_count = self.db.query(UserSession).filter(
                UserSession.expires_at < datetime.now(),
                UserSession.status == SessionStatus.ACTIVE
            ).update({"status": SessionStatus.EXPIRED})
            
            self.db.commit()
            
            return {
                "expired_count": expired_count,
                "message": f"Cleaned up {expired_count} expired sessions"
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")
            self.db.rollback()
            return {"error": str(e)}
