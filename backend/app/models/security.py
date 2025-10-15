"""
Security Models untuk Development (Single User)
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, Enum
from sqlalchemy.sql import func
from app.database import Base
import enum
from datetime import datetime, timedelta
import hashlib
import secrets

class UserRole(enum.Enum):
    """User roles"""
    ADMIN = "admin"
    USER = "user"

class SessionStatus(enum.Enum):
    """Session status"""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"

class User(Base):
    """User model for single user development"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    
    # Authentication
    password_hash = Column(String(255), nullable=False)
    salt = Column(String(32), nullable=False)
    
    # User info
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    
    # Security settings
    failed_login_attempts = Column(Integer, default=0)
    last_failed_login = Column(DateTime, nullable=True)
    account_locked_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

class TwoFactorAuth(Base):
    """Two-Factor Authentication model"""
    __tablename__ = "two_factor_auth"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    secret = Column(String(32), nullable=False)  # TOTP secret
    is_enabled = Column(Boolean, default=False)
    backup_codes = Column(JSON, nullable=True)  # List of backup codes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserSession(Base):
    """User session tracking"""
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    
    # Session details
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(Text, nullable=True)
    status = Column(Enum(SessionStatus), default=SessionStatus.ACTIVE)
    
    # Security
    is_secure = Column(Boolean, default=False)  # HTTPS
    fingerprint = Column(String(64), nullable=True)  # Browser fingerprint
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, server_default=func.now())
    revoked_at = Column(DateTime, nullable=True)

class SecurityLog(Base):
    """Security event logging"""
    __tablename__ = "security_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, nullable=False, index=True)
    
    # Event details
    event_type = Column(String(50), nullable=False, index=True)  # login, logout, failed_login, etc.
    user_id = Column(String(50), nullable=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    
    # Event data
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    event_data = Column(JSON, nullable=True)  # Additional event data
    
    # Risk assessment
    risk_level = Column(String(20), default="low")  # low, medium, high, critical
    is_suspicious = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

class SecuritySettings(Base):
    """Security configuration"""
    __tablename__ = "security_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False, index=True)
    setting_value = Column(Text, nullable=False)
    setting_type = Column(String(20), default="string")  # string, int, bool, json
    
    # Metadata
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False)  # Whether to mask in logs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class IPWhitelist(Base):
    """IP whitelist for development"""
    __tablename__ = "ip_whitelist"
    
    id = Column(Integer, primary_key=True, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    description = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime, nullable=True)  # Optional expiry

class SecurityMetrics(Base):
    """Security metrics and monitoring"""
    __tablename__ = "security_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Login metrics
    total_logins = Column(Integer, default=0)
    successful_logins = Column(Integer, default=0)
    failed_logins = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    
    # Security events
    suspicious_activities = Column(Integer, default=0)
    blocked_attempts = Column(Integer, default=0)
    account_lockouts = Column(Integer, default=0)
    
    # Session metrics
    active_sessions = Column(Integer, default=0)
    expired_sessions = Column(Integer, default=0)
    revoked_sessions = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
