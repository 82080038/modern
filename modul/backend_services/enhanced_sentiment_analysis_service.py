"""
Enhanced Sentiment Analysis Service
===================================

Service untuk sentiment analysis dengan implementasi algoritma terbukti
menggunakan transformers, NLTK, dan advanced NLP techniques.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import requests
import json
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob
import nltk
from app.models.sentiment import NewsSentiment, SocialSentiment, MarketSentiment
from app.models.market_data import MarketData

logger = logging.getLogger(__name__)

class EnhancedSentimentAnalysisService:
    """
    Enhanced Sentiment Analysis Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.sentiment_models = {}
        self._initialize_models()
        
        # Download required NLTK data
        try:
            nltk.download('vader_lexicon', quiet=True)
            nltk.download('punkt', quiet=True)
        except:
            pass
    
    def _initialize_models(self):
        """Initialize proven sentiment analysis models"""
        try:
            # Initialize VADER sentiment analyzer
            self.sentiment_models['vader'] = SentimentIntensityAnalyzer()
            
            # Initialize transformer models
            self.sentiment_models['finbert'] = pipeline(
                "sentiment-analysis",
                model="ProsusAI/finbert",
                tokenizer="ProsusAI/finbert"
            )
            
            # Initialize RoBERTa for general sentiment
            self.sentiment_models['roberta'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
            
            logger.info("Sentiment analysis models initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing sentiment models: {e}")
            # Fallback to basic models
            self.sentiment_models['vader'] = SentimentIntensityAnalyzer()
    
    async def analyze_news_sentiment(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """Analyze news sentiment untuk symbol dengan multiple algorithms"""
        try:
            # Get news data (simulated - in real implementation, fetch from news API)
            news_data = await self._get_news_data(symbol, days)
            
            if not news_data:
                return {'error': 'No news data available'}
            
            # Analyze sentiment dengan multiple models
            sentiment_results = {}
            
            for article in news_data:
                text = article.get('content', '') + ' ' + article.get('title', '')
                
                # VADER sentiment
                vader_scores = self._analyze_vader_sentiment(text)
                
                # FinBERT sentiment
                finbert_scores = self._analyze_finbert_sentiment(text)
                
                # RoBERTa sentiment
                roberta_scores = self._analyze_roberta_sentiment(text)
                
                # TextBlob sentiment
                textblob_scores = self._analyze_textblob_sentiment(text)
                
                # Combine results
                combined_sentiment = self._combine_sentiment_scores({
                    'vader': vader_scores,
                    'finbert': finbert_scores,
                    'roberta': roberta_scores,
                    'textblob': textblob_scores
                })
                
                sentiment_results[article['id']] = {
                    'title': article.get('title', ''),
                    'content': article.get('content', ''),
                    'published_at': article.get('published_at', ''),
                    'individual_scores': {
                        'vader': vader_scores,
                        'finbert': finbert_scores,
                        'roberta': roberta_scores,
                        'textblob': textblob_scores
                    },
                    'combined_sentiment': combined_sentiment
                }
            
            # Calculate aggregate sentiment
            aggregate_sentiment = self._calculate_aggregate_sentiment(sentiment_results)
            
            # Save to database
            await self._save_news_sentiment(symbol, sentiment_results, aggregate_sentiment)
            
            return {
                'success': True,
                'symbol': symbol,
                'articles_analyzed': len(news_data),
                'aggregate_sentiment': aggregate_sentiment,
                'individual_results': sentiment_results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {'error': str(e)}
    
    def _analyze_vader_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment menggunakan VADER"""
        try:
            if 'vader' not in self.sentiment_models:
                return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
            
            scores = self.sentiment_models['vader'].polarity_scores(text)
            return {
                'compound': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu']
            }
            
        except Exception as e:
            logger.error(f"Error in VADER sentiment analysis: {e}")
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 0.0}
    
    def _analyze_finbert_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment menggunakan FinBERT"""
        try:
            if 'finbert' not in self.sentiment_models:
                return {'label': 'NEUTRAL', 'score': 0.5}
            
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            result = self.sentiment_models['finbert'](text)
            
            # Convert to standardized format
            label = result[0]['label']
            score = result[0]['score']
            
            # Map FinBERT labels to sentiment scores
            if label == 'POSITIVE':
                return {'label': 'POSITIVE', 'score': score, 'sentiment_score': score}
            elif label == 'NEGATIVE':
                return {'label': 'NEGATIVE', 'score': score, 'sentiment_score': -score}
            else:
                return {'label': 'NEUTRAL', 'score': score, 'sentiment_score': 0.0}
                
        except Exception as e:
            logger.error(f"Error in FinBERT sentiment analysis: {e}")
            return {'label': 'NEUTRAL', 'score': 0.5, 'sentiment_score': 0.0}
    
    def _analyze_roberta_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment menggunakan RoBERTa"""
        try:
            if 'roberta' not in self.sentiment_models:
                return {'label': 'NEUTRAL', 'score': 0.5}
            
            # Truncate text if too long
            if len(text) > 512:
                text = text[:512]
            
            result = self.sentiment_models['roberta'](text)
            
            # Convert to standardized format
            label = result[0]['label']
            score = result[0]['score']
            
            # Map RoBERTa labels to sentiment scores
            if 'POSITIVE' in label or 'LABEL_2' in label:
                return {'label': 'POSITIVE', 'score': score, 'sentiment_score': score}
            elif 'NEGATIVE' in label or 'LABEL_0' in label:
                return {'label': 'NEGATIVE', 'score': score, 'sentiment_score': -score}
            else:
                return {'label': 'NEUTRAL', 'score': score, 'sentiment_score': 0.0}
                
        except Exception as e:
            logger.error(f"Error in RoBERTa sentiment analysis: {e}")
            return {'label': 'NEUTRAL', 'score': 0.5, 'sentiment_score': 0.0}
    
    def _analyze_textblob_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment menggunakan TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Convert polarity to sentiment scores
            if polarity > 0.1:
                sentiment_score = polarity
                label = 'POSITIVE'
            elif polarity < -0.1:
                sentiment_score = polarity
                label = 'NEGATIVE'
            else:
                sentiment_score = 0.0
                label = 'NEUTRAL'
            
            return {
                'label': label,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'sentiment_score': sentiment_score
            }
            
        except Exception as e:
            logger.error(f"Error in TextBlob sentiment analysis: {e}")
            return {'label': 'NEUTRAL', 'polarity': 0.0, 'subjectivity': 0.0, 'sentiment_score': 0.0}
    
    def _combine_sentiment_scores(self, individual_scores: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine sentiment scores dari multiple models"""
        try:
            # Extract sentiment scores
            sentiment_scores = []
            confidence_scores = []
            
            for model_name, scores in individual_scores.items():
                if 'sentiment_score' in scores:
                    sentiment_scores.append(scores['sentiment_score'])
                    confidence_scores.append(scores.get('score', 0.5))
                elif 'compound' in scores:
                    sentiment_scores.append(scores['compound'])
                    confidence_scores.append(abs(scores['compound']))
            
            if not sentiment_scores:
                return {
                    'combined_score': 0.0,
                    'confidence': 0.0,
                    'label': 'NEUTRAL'
                }
            
            # Weighted average based on confidence
            if confidence_scores and sum(confidence_scores) > 0:
                weights = np.array(confidence_scores) / sum(confidence_scores)
                combined_score = np.average(sentiment_scores, weights=weights)
                confidence = np.mean(confidence_scores)
            else:
                combined_score = np.mean(sentiment_scores)
                confidence = 0.5
            
            # Determine label
            if combined_score > 0.1:
                label = 'POSITIVE'
            elif combined_score < -0.1:
                label = 'NEGATIVE'
            else:
                label = 'NEUTRAL'
            
            return {
                'combined_score': combined_score,
                'confidence': confidence,
                'label': label,
                'model_count': len(sentiment_scores)
            }
            
        except Exception as e:
            logger.error(f"Error combining sentiment scores: {e}")
            return {
                'combined_score': 0.0,
                'confidence': 0.0,
                'label': 'NEUTRAL',
                'model_count': 0
            }
    
    def _calculate_aggregate_sentiment(self, sentiment_results: Dict[str, Dict]) -> Dict[str, Any]:
        """Calculate aggregate sentiment untuk all articles"""
        try:
            if not sentiment_results:
                return {
                    'overall_sentiment': 0.0,
                    'confidence': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_articles': 0
                }
            
            combined_scores = []
            confidence_scores = []
            label_counts = {'POSITIVE': 0, 'NEGATIVE': 0, 'NEUTRAL': 0}
            
            for article_id, result in sentiment_results.items():
                combined = result.get('combined_sentiment', {})
                if 'combined_score' in combined:
                    combined_scores.append(combined['combined_score'])
                    confidence_scores.append(combined.get('confidence', 0.5))
                    
                    label = combined.get('label', 'NEUTRAL')
                    if label in label_counts:
                        label_counts[label] += 1
            
            if not combined_scores:
                return {
                    'overall_sentiment': 0.0,
                    'confidence': 0.0,
                    'positive_count': 0,
                    'negative_count': 0,
                    'neutral_count': 0,
                    'total_articles': len(sentiment_results)
                }
            
            # Calculate weighted average
            if confidence_scores and sum(confidence_scores) > 0:
                weights = np.array(confidence_scores) / sum(confidence_scores)
                overall_sentiment = np.average(combined_scores, weights=weights)
                overall_confidence = np.mean(confidence_scores)
            else:
                overall_sentiment = np.mean(combined_scores)
                overall_confidence = 0.5
            
            return {
                'overall_sentiment': overall_sentiment,
                'confidence': overall_confidence,
                'positive_count': label_counts['POSITIVE'],
                'negative_count': label_counts['NEGATIVE'],
                'neutral_count': label_counts['NEUTRAL'],
                'total_articles': len(sentiment_results)
            }
            
        except Exception as e:
            logger.error(f"Error calculating aggregate sentiment: {e}")
            return {
                'overall_sentiment': 0.0,
                'confidence': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_articles': 0
            }
    
    async def _get_news_data(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Get news data untuk symbol (simulated)"""
        try:
            # In real implementation, this would fetch from news APIs
            # For now, return simulated data
            simulated_news = [
                {
                    'id': f'news_{symbol}_1',
                    'title': f'Positive outlook for {symbol} as earnings beat expectations',
                    'content': f'{symbol} reported strong quarterly earnings, beating analyst estimates by 15%. The company showed robust growth in key markets.',
                    'published_at': datetime.now() - timedelta(hours=2)
                },
                {
                    'id': f'news_{symbol}_2',
                    'title': f'{symbol} faces regulatory challenges in key markets',
                    'content': f'Regulatory concerns are mounting for {symbol} as new regulations could impact revenue streams in several key markets.',
                    'published_at': datetime.now() - timedelta(hours=5)
                },
                {
                    'id': f'news_{symbol}_3',
                    'title': f'Analysts upgrade {symbol} price target',
                    'content': f'Major investment banks have upgraded their price targets for {symbol} citing strong fundamentals and market position.',
                    'published_at': datetime.now() - timedelta(hours=8)
                }
            ]
            
            return simulated_news
            
        except Exception as e:
            logger.error(f"Error getting news data: {e}")
            return []
    
    async def _save_news_sentiment(
        self, 
        symbol: str, 
        sentiment_results: Dict[str, Dict], 
        aggregate_sentiment: Dict[str, Any]
    ):
        """Save news sentiment results ke database"""
        try:
            # Save aggregate sentiment
            news_sentiment = NewsSentiment(
                symbol=symbol,
                sentiment_score=aggregate_sentiment.get('overall_sentiment', 0.0),
                confidence=aggregate_sentiment.get('confidence', 0.0),
                positive_count=aggregate_sentiment.get('positive_count', 0),
                negative_count=aggregate_sentiment.get('negative_count', 0),
                neutral_count=aggregate_sentiment.get('neutral_count', 0),
                total_articles=aggregate_sentiment.get('total_articles', 0),
                created_at=datetime.now()
            )
            
            self.db.add(news_sentiment)
            self.db.commit()
            
            logger.info(f"Saved news sentiment for {symbol}")
            
        except Exception as e:
            logger.error(f"Error saving news sentiment: {e}")
            self.db.rollback()
    
    async def analyze_social_sentiment(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """Analyze social media sentiment untuk symbol"""
        try:
            # Get social media data (simulated)
            social_data = await self._get_social_data(symbol, days)
            
            if not social_data:
                return {'error': 'No social media data available'}
            
            # Analyze sentiment untuk each post
            sentiment_results = {}
            
            for post in social_data:
                text = post.get('content', '')
                
                # Analyze dengan multiple models
                vader_scores = self._analyze_vader_sentiment(text)
                roberta_scores = self._analyze_roberta_sentiment(text)
                textblob_scores = self._analyze_textblob_sentiment(text)
                
                # Combine results
                combined_sentiment = self._combine_sentiment_scores({
                    'vader': vader_scores,
                    'roberta': roberta_scores,
                    'textblob': textblob_scores
                })
                
                sentiment_results[post['id']] = {
                    'content': text,
                    'platform': post.get('platform', ''),
                    'created_at': post.get('created_at', ''),
                    'combined_sentiment': combined_sentiment
                }
            
            # Calculate aggregate sentiment
            aggregate_sentiment = self._calculate_aggregate_sentiment(sentiment_results)
            
            # Save to database
            await self._save_social_sentiment(symbol, sentiment_results, aggregate_sentiment)
            
            return {
                'success': True,
                'symbol': symbol,
                'posts_analyzed': len(social_data),
                'aggregate_sentiment': aggregate_sentiment,
                'individual_results': sentiment_results
            }
            
        except Exception as e:
            logger.error(f"Error analyzing social sentiment: {e}")
            return {'error': str(e)}
    
    async def _get_social_data(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Get social media data untuk symbol (simulated)"""
        try:
            # In real implementation, this would fetch from Twitter, Reddit, etc.
            # For now, return simulated data
            simulated_posts = [
                {
                    'id': f'social_{symbol}_1',
                    'content': f'Just bought more {symbol} shares! Great company with strong fundamentals.',
                    'platform': 'twitter',
                    'created_at': datetime.now() - timedelta(hours=1)
                },
                {
                    'id': f'social_{symbol}_2',
                    'content': f'{symbol} is overvalued right now. Waiting for a better entry point.',
                    'platform': 'reddit',
                    'created_at': datetime.now() - timedelta(hours=3)
                },
                {
                    'id': f'social_{symbol}_3',
                    'content': f'Excited about {symbol} earnings next week. Expecting positive results.',
                    'platform': 'twitter',
                    'created_at': datetime.now() - timedelta(hours=6)
                }
            ]
            
            return simulated_posts
            
        except Exception as e:
            logger.error(f"Error getting social data: {e}")
            return []
    
    async def _save_social_sentiment(
        self, 
        symbol: str, 
        sentiment_results: Dict[str, Dict], 
        aggregate_sentiment: Dict[str, Any]
    ):
        """Save social sentiment results ke database"""
        try:
            # Save aggregate sentiment
            social_sentiment = SocialSentiment(
                symbol=symbol,
                sentiment_score=aggregate_sentiment.get('overall_sentiment', 0.0),
                confidence=aggregate_sentiment.get('confidence', 0.0),
                positive_count=aggregate_sentiment.get('positive_count', 0),
                negative_count=aggregate_sentiment.get('negative_count', 0),
                neutral_count=aggregate_sentiment.get('neutral_count', 0),
                total_posts=aggregate_sentiment.get('total_articles', 0),
                created_at=datetime.now()
            )
            
            self.db.add(social_sentiment)
            self.db.commit()
            
            logger.info(f"Saved social sentiment for {symbol}")
            
        except Exception as e:
            logger.error(f"Error saving social sentiment: {e}")
            self.db.rollback()
    
    async def get_market_sentiment(self, symbols: List[str]) -> Dict[str, Any]:
        """Get overall market sentiment untuk multiple symbols"""
        try:
            market_sentiment_data = []
            
            for symbol in symbols:
                # Get latest news sentiment
                news_sentiment = self.db.query(NewsSentiment).filter(
                    NewsSentiment.symbol == symbol
                ).order_by(NewsSentiment.created_at.desc()).first()
                
                # Get latest social sentiment
                social_sentiment = self.db.query(SocialSentiment).filter(
                    SocialSentiment.symbol == symbol
                ).order_by(SocialSentiment.created_at.desc()).first()
                
                symbol_sentiment = {
                    'symbol': symbol,
                    'news_sentiment': news_sentiment.sentiment_score if news_sentiment else 0.0,
                    'social_sentiment': social_sentiment.sentiment_score if social_sentiment else 0.0,
                    'combined_sentiment': 0.0
                }
                
                # Combine news and social sentiment
                if news_sentiment and social_sentiment:
                    symbol_sentiment['combined_sentiment'] = (
                        news_sentiment.sentiment_score * 0.6 + 
                        social_sentiment.sentiment_score * 0.4
                    )
                elif news_sentiment:
                    symbol_sentiment['combined_sentiment'] = news_sentiment.sentiment_score
                elif social_sentiment:
                    symbol_sentiment['combined_sentiment'] = social_sentiment.sentiment_score
                
                market_sentiment_data.append(symbol_sentiment)
            
            # Calculate overall market sentiment
            if market_sentiment_data:
                overall_sentiment = np.mean([s['combined_sentiment'] for s in market_sentiment_data])
                
                # Save market sentiment
                market_sentiment = MarketSentiment(
                    sentiment_score=overall_sentiment,
                    symbol_count=len(symbols),
                    positive_symbols=len([s for s in market_sentiment_data if s['combined_sentiment'] > 0.1]),
                    negative_symbols=len([s for s in market_sentiment_data if s['combined_sentiment'] < -0.1]),
                    neutral_symbols=len([s for s in market_sentiment_data if -0.1 <= s['combined_sentiment'] <= 0.1]),
                    created_at=datetime.now()
                )
                
                self.db.add(market_sentiment)
                self.db.commit()
                
                return {
                    'success': True,
                    'overall_sentiment': overall_sentiment,
                    'symbol_sentiments': market_sentiment_data,
                    'market_sentiment_id': market_sentiment.id
                }
            else:
                return {'error': 'No sentiment data available'}
                
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {'error': str(e)}
