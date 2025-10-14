"""
Configuration settings for Trading Platform Modern
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database Configuration
    DATABASE_URL: str = "mysql+pymysql://root:@localhost:3306/scalper"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Data Sources
    YFINANCE_ENABLED: bool = True
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None
    TWITTER_API_KEY: Optional[str] = None
    REDDIT_CLIENT_ID: Optional[str] = None
    REDDIT_CLIENT_SECRET: Optional[str] = None
    
    # Trading Configuration
    PAPER_TRADING_MODE: bool = True
    VIRTUAL_BALANCE: float = 10000000.0  # 10M IDR
    COMMISSION_RATE: float = 0.0015  # 0.15%
    SLIPPAGE_RATE: float = 0.0005  # 0.05%
    
    # Risk Management
    MAX_POSITION_SIZE: float = 0.1  # 10% of portfolio
    MAX_DAILY_LOSS: float = 0.02  # 2% daily loss limit
    MAX_DRAWDOWN: float = 0.15  # 15% max drawdown
    
    # ML Configuration
    MODEL_RETRAIN_DAYS: int = 30
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.7
    WALK_FORWARD_TRAIN_DAYS: int = 365
    WALK_FORWARD_TEST_DAYS: int = 90
    
    # Data Quality (IDX Specific)
    MIN_ADV_THRESHOLD: float = 1000000000.0  # 1B IDR
    TIMEZONE: str = "Asia/Jakarta"
    MARKET_HOURS_START: str = "09:00"
    MARKET_HOURS_END: str = "16:00"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/trading_platform.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()
