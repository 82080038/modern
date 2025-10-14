"""
Sentiment Analysis Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from app.models.sentiment import (
    NewsSentiment, SocialSentiment, MarketSentiment, 
    InsiderTrading, SentimentAggregation, SentimentAlerts
)
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class SentimentAnalysisEngine:
    """Core engine for sentiment analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def aggregate_news_sentiment(self, symbol: str, days: int = 7) -> Dict:
        """Aggregate news sentiment for a symbol"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get news sentiment data
            news_data = self.db.query(NewsSentiment).filter(
                NewsSentiment.symbol == symbol,
                NewsSentiment.news_date >= start_date,
                NewsSentiment.news_date <= end_date
            ).all()
            
            if not news_data:
                return {"error": "No news sentiment data found"}
            
            # Calculate aggregated metrics
            polarities = [n.polarity for n in news_data if n.polarity is not None]
            confidences = [n.confidence for n in news_data if n.confidence is not None]
            impact_scores = [n.impact_score for n in news_data if n.impact_score is not None]
            
            if not polarities:
                return {"error": "No valid sentiment scores found"}
            
            # Basic statistics
            avg_polarity = np.mean(polarities)
            std_polarity = np.std(polarities)
            median_polarity = np.median(polarities)
            
            # Weighted by confidence and impact
            if confidences and impact_scores:
                weights = [c * i for c, i in zip(confidences, impact_scores)]
                weighted_polarity = np.average(polarities, weights=weights)
            else:
                weighted_polarity = avg_polarity
            
            # Sentiment classification
            if weighted_polarity > 0.1:
                sentiment_class = "positive"
            elif weighted_polarity < -0.1:
                sentiment_class = "negative"
            else:
                sentiment_class = "neutral"
            
            # Volume metrics
            total_news = len(news_data)
            positive_news = len([p for p in polarities if p > 0.1])
            negative_news = len([p for p in polarities if p < -0.1])
            neutral_news = total_news - positive_news - negative_news
            
            return {
                "symbol": symbol,
                "period_days": days,
                "total_news": total_news,
                "avg_polarity": avg_polarity,
                "weighted_polarity": weighted_polarity,
                "std_polarity": std_polarity,
                "sentiment_class": sentiment_class,
                "positive_news": positive_news,
                "negative_news": negative_news,
                "neutral_news": neutral_news,
                "confidence_avg": np.mean(confidences) if confidences else 0,
                "impact_avg": np.mean(impact_scores) if impact_scores else 0
            }
            
        except Exception as e:
            logger.error(f"Error aggregating news sentiment for {symbol}: {e}")
            return {"error": str(e)}
    
    def aggregate_social_sentiment(self, symbol: str, days: int = 7) -> Dict:
        """Aggregate social media sentiment for a symbol"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get social sentiment data
            social_data = self.db.query(SocialSentiment).filter(
                SocialSentiment.symbol == symbol,
                SocialSentiment.post_date >= start_date,
                SocialSentiment.post_date <= end_date
            ).all()
            
            if not social_data:
                return {"error": "No social sentiment data found"}
            
            # Calculate aggregated metrics
            polarities = [s.polarity for s in social_data if s.polarity is not None]
            engagement_scores = [s.engagement_score for s in social_data if s.engagement_score is not None]
            influence_scores = [s.influence_score for s in social_data if s.influence_score is not None]
            
            if not polarities:
                return {"error": "No valid sentiment scores found"}
            
            # Basic statistics
            avg_polarity = np.mean(polarities)
            std_polarity = np.std(polarities)
            
            # Weighted by engagement and influence
            if engagement_scores and influence_scores:
                weights = [e * i for e, i in zip(engagement_scores, influence_scores)]
                weighted_polarity = np.average(polarities, weights=weights)
            else:
                weighted_polarity = avg_polarity
            
            # Sentiment classification
            if weighted_polarity > 0.1:
                sentiment_class = "positive"
            elif weighted_polarity < -0.1:
                sentiment_class = "negative"
            else:
                sentiment_class = "neutral"
            
            # Volume and engagement metrics
            total_posts = len(social_data)
            total_engagement = sum([s.likes or 0 + s.retweets or 0 + s.replies or 0 for s in social_data])
            avg_engagement = total_engagement / total_posts if total_posts > 0 else 0
            
            # Platform breakdown
            platforms = {}
            for post in social_data:
                platform = post.platform
                if platform not in platforms:
                    platforms[platform] = {"count": 0, "avg_sentiment": 0}
                platforms[platform]["count"] += 1
                if post.polarity is not None:
                    platforms[platform]["avg_sentiment"] += post.polarity
            
            for platform in platforms:
                platforms[platform]["avg_sentiment"] /= platforms[platform]["count"]
            
            return {
                "symbol": symbol,
                "period_days": days,
                "total_posts": total_posts,
                "avg_polarity": avg_polarity,
                "weighted_polarity": weighted_polarity,
                "std_polarity": std_polarity,
                "sentiment_class": sentiment_class,
                "total_engagement": total_engagement,
                "avg_engagement": avg_engagement,
                "platforms": platforms
            }
            
        except Exception as e:
            logger.error(f"Error aggregating social sentiment for {symbol}: {e}")
            return {"error": str(e)}
    
    def calculate_market_sentiment(self, date: date = None) -> Dict:
        """Calculate market-wide sentiment indicators"""
        try:
            if not date:
                date = datetime.now().date()
            
            # Get market sentiment data
            market_data = self.db.query(MarketSentiment).filter(
                MarketSentiment.date == date
            ).first()
            
            if not market_data:
                return {"error": "No market sentiment data found"}
            
            # Fear & Greed Index interpretation
            fg_index = market_data.fear_greed_index
            if fg_index >= 80:
                fg_classification = "extreme_greed"
            elif fg_index >= 60:
                fg_classification = "greed"
            elif fg_index >= 40:
                fg_classification = "neutral"
            elif fg_index >= 20:
                fg_classification = "fear"
            else:
                fg_classification = "extreme_fear"
            
            # Market breadth analysis
            advancing = market_data.advancing_stocks or 0
            declining = market_data.declining_stocks or 0
            total_stocks = advancing + declining + (market_data.unchanged_stocks or 0)
            
            breadth_ratio = advancing / declining if declining > 0 else float('inf')
            
            # Volume analysis
            volume_ratio = market_data.volume_ratio or 1.0
            volume_classification = "high" if volume_ratio > 1.5 else "normal" if volume_ratio > 0.8 else "low"
            
            # Composite sentiment score
            composite_score = market_data.composite_sentiment or 0
            if composite_score > 0.2:
                market_sentiment = "bullish"
            elif composite_score < -0.2:
                market_sentiment = "bearish"
            else:
                market_sentiment = "neutral"
            
            return {
                "date": date.isoformat(),
                "fear_greed_index": fg_index,
                "fear_greed_classification": fg_classification,
                "market_volatility": market_data.market_volatility,
                "put_call_ratio": market_data.put_call_ratio,
                "advancing_stocks": advancing,
                "declining_stocks": declining,
                "breadth_ratio": breadth_ratio,
                "volume_ratio": volume_ratio,
                "volume_classification": volume_classification,
                "composite_sentiment": composite_score,
                "market_sentiment": market_sentiment,
                "news_sentiment_avg": market_data.news_sentiment_avg,
                "social_sentiment_avg": market_data.social_sentiment_avg
            }
            
        except Exception as e:
            logger.error(f"Error calculating market sentiment: {e}")
            return {"error": str(e)}
    
    def analyze_insider_activity(self, symbol: str, days: int = 30) -> Dict:
        """Analyze insider trading activity"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get insider trading data
            insider_data = self.db.query(InsiderTrading).filter(
                InsiderTrading.symbol == symbol,
                InsiderTrading.transaction_date >= start_date.date(),
                InsiderTrading.transaction_date <= end_date.date()
            ).all()
            
            if not insider_data:
                return {"error": "No insider trading data found"}
            
            # Analyze buy vs sell activity
            buy_transactions = [t for t in insider_data if t.transaction_type == 'buy']
            sell_transactions = [t for t in insider_data if t.transaction_type == 'sell']
            
            buy_value = sum([t.total_value for t in buy_transactions if t.total_value])
            sell_value = sum([t.total_value for t in sell_transactions if t.total_value])
            
            net_insider_activity = buy_value - sell_value
            insider_ratio = buy_value / sell_value if sell_value > 0 else float('inf')
            
            # Calculate sentiment score
            if insider_ratio > 2:
                insider_sentiment = "very_bullish"
                sentiment_score = 0.8
            elif insider_ratio > 1.5:
                insider_sentiment = "bullish"
                sentiment_score = 0.6
            elif insider_ratio > 1:
                insider_sentiment = "slightly_bullish"
                sentiment_score = 0.3
            elif insider_ratio > 0.5:
                insider_sentiment = "slightly_bearish"
                sentiment_score = -0.3
            else:
                insider_sentiment = "bearish"
                sentiment_score = -0.6
            
            return {
                "symbol": symbol,
                "period_days": days,
                "total_transactions": len(insider_data),
                "buy_transactions": len(buy_transactions),
                "sell_transactions": len(sell_transactions),
                "buy_value": buy_value,
                "sell_value": sell_value,
                "net_activity": net_insider_activity,
                "insider_ratio": insider_ratio,
                "insider_sentiment": insider_sentiment,
                "sentiment_score": sentiment_score
            }
            
        except Exception as e:
            logger.error(f"Error analyzing insider activity for {symbol}: {e}")
            return {"error": str(e)}
    
    def calculate_composite_sentiment(self, symbol: str, days: int = 7) -> Dict:
        """Calculate composite sentiment score from all sources"""
        try:
            # Get individual sentiment components
            news_sentiment = self.aggregate_news_sentiment(symbol, days)
            social_sentiment = self.aggregate_social_sentiment(symbol, days)
            insider_activity = self.analyze_insider_activity(symbol, days * 4)  # Longer period for insider data
            market_sentiment = self.calculate_market_sentiment()
            
            # Initialize composite score
            composite_score = 0
            confidence = 0
            components = {}
            
            # News sentiment (weight: 0.3)
            if "weighted_polarity" in news_sentiment:
                news_score = news_sentiment["weighted_polarity"]
                composite_score += news_score * 0.3
                confidence += 0.3
                components["news"] = {
                    "score": news_score,
                    "weight": 0.3,
                    "count": news_sentiment.get("total_news", 0)
                }
            
            # Social sentiment (weight: 0.25)
            if "weighted_polarity" in social_sentiment:
                social_score = social_sentiment["weighted_polarity"]
                composite_score += social_score * 0.25
                confidence += 0.25
                components["social"] = {
                    "score": social_score,
                    "weight": 0.25,
                    "count": social_sentiment.get("total_posts", 0)
                }
            
            # Insider activity (weight: 0.2)
            if "sentiment_score" in insider_activity:
                insider_score = insider_activity["sentiment_score"]
                composite_score += insider_score * 0.2
                confidence += 0.2
                components["insider"] = {
                    "score": insider_score,
                    "weight": 0.2,
                    "transactions": insider_activity.get("total_transactions", 0)
                }
            
            # Market sentiment (weight: 0.25)
            if "composite_sentiment" in market_sentiment:
                market_score = market_sentiment["composite_sentiment"]
                composite_score += market_score * 0.25
                confidence += 0.25
                components["market"] = {
                    "score": market_score,
                    "weight": 0.25,
                    "fear_greed": market_sentiment.get("fear_greed_index", 50)
                }
            
            # Normalize by confidence
            if confidence > 0:
                composite_score = composite_score / confidence
            
            # Determine sentiment classification
            if composite_score > 0.3:
                sentiment_class = "very_bullish"
            elif composite_score > 0.1:
                sentiment_class = "bullish"
            elif composite_score > -0.1:
                sentiment_class = "neutral"
            elif composite_score > -0.3:
                sentiment_class = "bearish"
            else:
                sentiment_class = "very_bearish"
            
            # Calculate trend
            # This would require historical data comparison
            trend = "stable"  # Placeholder
            
            return {
                "symbol": symbol,
                "composite_score": composite_score,
                "sentiment_class": sentiment_class,
                "confidence": confidence,
                "trend": trend,
                "components": components,
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"Error calculating composite sentiment for {symbol}: {e}")
            return {"error": str(e)}
    
    def generate_sentiment_alerts(self, symbol: str, threshold: float = 0.5) -> List[Dict]:
        """Generate sentiment-based alerts"""
        try:
            alerts = []
            
            # Get recent sentiment data
            composite_sentiment = self.calculate_composite_sentiment(symbol, 1)  # Last 24 hours
            
            if "error" in composite_sentiment:
                return alerts
            
            score = composite_sentiment["composite_score"]
            confidence = composite_sentiment["confidence"]
            
            # Check for significant sentiment shifts
            if abs(score) > threshold and confidence > 0.5:
                if score > threshold:
                    alert_type = "sentiment_surge_positive"
                    severity = "high" if score > 0.7 else "medium"
                    title = f"Positive Sentiment Surge for {symbol}"
                    description = f"Strong positive sentiment detected (score: {score:.2f})"
                else:
                    alert_type = "sentiment_surge_negative"
                    severity = "high" if score < -0.7 else "medium"
                    title = f"Negative Sentiment Surge for {symbol}"
                    description = f"Strong negative sentiment detected (score: {score:.2f})"
                
                alerts.append({
                    "alert_type": alert_type,
                    "title": title,
                    "description": description,
                    "severity": severity,
                    "symbol": symbol,
                    "trigger_value": score,
                    "threshold": threshold,
                    "confidence": confidence
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating sentiment alerts for {symbol}: {e}")
            return []
