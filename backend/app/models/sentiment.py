"""
Sentiment Analysis Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, JSON, BigInteger
from sqlalchemy.sql import func
from app.database import Base

class NewsSentiment(Base):
    """News sentiment analysis"""
    __tablename__ = "news_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    news_date = Column(DateTime, nullable=False, index=True)
    source = Column(String(100), nullable=False)  # newsapi, gdelt, rss
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=True)
    url = Column(String(500), nullable=True)
    
    # Sentiment Scores
    polarity = Column(Float, nullable=True)  # -1 to +1
    subjectivity = Column(Float, nullable=True)  # 0 to 1
    confidence = Column(Float, nullable=True)  # 0 to 1
    
    # FinBERT Scores
    finbert_positive = Column(Float, nullable=True)
    finbert_negative = Column(Float, nullable=True)
    finbert_neutral = Column(Float, nullable=True)
    finbert_sentiment = Column(String(20), nullable=True)  # positive, negative, neutral
    
    # Keywords and Entities
    keywords = Column(JSON, nullable=True)
    entities = Column(JSON, nullable=True)
    topics = Column(JSON, nullable=True)
    
    # Impact Score
    impact_score = Column(Float, nullable=True)  # 0 to 1
    relevance_score = Column(Float, nullable=True)  # 0 to 1
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SocialSentiment(Base):
    """Social media sentiment analysis"""
    __tablename__ = "social_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    post_date = Column(DateTime, nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # twitter, reddit, facebook
    post_id = Column(String(100), nullable=False)
    username = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    
    # Sentiment Scores
    polarity = Column(Float, nullable=True)
    subjectivity = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)
    
    # Engagement Metrics
    likes = Column(Integer, nullable=True)
    retweets = Column(Integer, nullable=True)
    replies = Column(Integer, nullable=True)
    shares = Column(Integer, nullable=True)
    engagement_score = Column(Float, nullable=True)
    
    # Influence Score
    follower_count = Column(Integer, nullable=True)
    influence_score = Column(Float, nullable=True)
    verified = Column(Boolean, default=False)
    
    # Hashtags and Mentions
    hashtags = Column(JSON, nullable=True)
    mentions = Column(JSON, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MarketSentiment(Base):
    """Market-wide sentiment indicators"""
    __tablename__ = "market_sentiment"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    
    # Fear & Greed Index
    fear_greed_index = Column(Float, nullable=True)  # 0-100
    fear_greed_classification = Column(String(20), nullable=True)  # extreme_fear, fear, neutral, greed, extreme_greed
    
    # VIX-like Indicators
    market_volatility = Column(Float, nullable=True)
    put_call_ratio = Column(Float, nullable=True)
    vix_equivalent = Column(Float, nullable=True)
    
    # Market Breadth
    advancing_stocks = Column(Integer, nullable=True)
    declining_stocks = Column(Integer, nullable=True)
    unchanged_stocks = Column(Integer, nullable=True)
    advance_decline_ratio = Column(Float, nullable=True)
    
    # Volume Indicators
    total_volume = Column(BigInteger, nullable=True)
    volume_ratio = Column(Float, nullable=True)  # vs average
    money_flow_index = Column(Float, nullable=True)
    
    # News Sentiment Aggregation
    news_sentiment_avg = Column(Float, nullable=True)
    news_sentiment_std = Column(Float, nullable=True)
    news_volume = Column(Integer, nullable=True)
    
    # Social Sentiment Aggregation
    social_sentiment_avg = Column(Float, nullable=True)
    social_sentiment_std = Column(Float, nullable=True)
    social_volume = Column(Integer, nullable=True)
    
    # Composite Sentiment Score
    composite_sentiment = Column(Float, nullable=True)  # -1 to +1
    sentiment_trend = Column(String(20), nullable=True)  # improving, declining, stable
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class InsiderTrading(Base):
    """Insider trading activity"""
    __tablename__ = "insider_trading"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    transaction_date = Column(Date, nullable=False, index=True)
    insider_name = Column(String(200), nullable=True)
    insider_title = Column(String(100), nullable=True)
    transaction_type = Column(String(20), nullable=False)  # buy, sell, option_exercise
    
    # Transaction Details
    shares_traded = Column(Integer, nullable=True)
    price_per_share = Column(Float, nullable=True)
    total_value = Column(BigInteger, nullable=True)
    
    # Ownership
    shares_owned_after = Column(Integer, nullable=True)
    ownership_percentage = Column(Float, nullable=True)
    
    # Sentiment Impact
    insider_sentiment_score = Column(Float, nullable=True)  # -1 to +1
    confidence_level = Column(Float, nullable=True)  # 0 to 1
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SentimentAggregation(Base):
    """Aggregated sentiment scores by symbol and timeframe"""
    __tablename__ = "sentiment_aggregation"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)  # daily, weekly, monthly
    
    # News Sentiment Aggregation
    news_count = Column(Integer, nullable=True)
    news_sentiment_avg = Column(Float, nullable=True)
    news_sentiment_std = Column(Float, nullable=True)
    news_sentiment_weighted = Column(Float, nullable=True)
    
    # Social Sentiment Aggregation
    social_count = Column(Integer, nullable=True)
    social_sentiment_avg = Column(Float, nullable=True)
    social_sentiment_std = Column(Float, nullable=True)
    social_sentiment_weighted = Column(Float, nullable=True)
    
    # Market Sentiment
    market_sentiment = Column(Float, nullable=True)
    fear_greed_index = Column(Float, nullable=True)
    volatility_index = Column(Float, nullable=True)
    
    # Insider Activity
    insider_buy_ratio = Column(Float, nullable=True)
    insider_sentiment = Column(Float, nullable=True)
    
    # Composite Scores
    composite_sentiment = Column(Float, nullable=True)  # -1 to +1
    sentiment_confidence = Column(Float, nullable=True)  # 0 to 1
    sentiment_trend = Column(String(20), nullable=True)  # bullish, bearish, neutral
    
    # Technical Sentiment
    technical_sentiment = Column(Float, nullable=True)
    momentum_sentiment = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SentimentAlerts(Base):
    """Sentiment-based alerts and signals"""
    __tablename__ = "sentiment_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    alert_date = Column(DateTime, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # news_surge, social_buzz, sentiment_shift
    
    # Alert Details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    
    # Trigger Values
    trigger_value = Column(Float, nullable=True)
    threshold_value = Column(Float, nullable=True)
    change_pct = Column(Float, nullable=True)
    
    # Context
    news_count = Column(Integer, nullable=True)
    social_volume = Column(Integer, nullable=True)
    sentiment_score = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
