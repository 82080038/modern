"""
Sentiment Scraping Service untuk Reddit, Twitter, Google Trends
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
import requests
import json
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
import praw
from pytrends.request import TrendReq

logger = logging.getLogger(__name__)

class SentimentScrapingService:
    """Service untuk sentiment scraping dari berbagai sumber"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize Reddit API (using free tier)
        self.reddit = praw.Reddit(
            client_id="your_client_id",
            client_secret="your_client_secret",
            user_agent="TradingPlatform/1.0"
        )
        
        # Initialize Google Trends
        self.pytrends = TrendReq(hl='en-US', tz=360)
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 1  # seconds
    
    def scrape_reddit_sentiment(self, symbol: str, subreddits: List[str] = None, limit: int = 100) -> Dict:
        """Scrape Reddit sentiment for a symbol"""
        try:
            if not subreddits:
                subreddits = ['wallstreetbets', 'stocks', 'investing', 'SecurityAnalysis']
            
            all_posts = []
            all_comments = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Search for posts about the symbol
                    search_query = f"{symbol} OR ${symbol}"
                    posts = subreddit.search(search_query, limit=limit//len(subreddits))
                    
                    for post in posts:
                        # Get post data
                        post_data = {
                            'id': post.id,
                            'title': post.title,
                            'text': post.selftext,
                            'score': post.score,
                            'upvote_ratio': post.upvote_ratio,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc),
                            'subreddit': subreddit_name,
                            'url': post.url,
                            'author': str(post.author) if post.author else 'deleted'
                        }
                        all_posts.append(post_data)
                        
                        # Get top comments
                        post.comments.replace_more(limit=0)
                        for comment in post.comments[:10]:  # Top 10 comments
                            if hasattr(comment, 'body') and comment.body != '[deleted]':
                                comment_data = {
                                    'id': comment.id,
                                    'body': comment.body,
                                    'score': comment.score,
                                    'created_utc': datetime.fromtimestamp(comment.created_utc),
                                    'post_id': post.id,
                                    'subreddit': subreddit_name
                                }
                                all_comments.append(comment_data)
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error scraping subreddit {subreddit_name}: {e}")
                    continue
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_reddit_sentiment(all_posts, all_comments)
            
            return {
                'symbol': symbol,
                'source': 'reddit',
                'total_posts': len(all_posts),
                'total_comments': len(all_comments),
                'subreddits_scraped': subreddits,
                'sentiment_analysis': sentiment_analysis,
                'posts': all_posts[:20],  # Return top 20 posts
                'comments': all_comments[:50],  # Return top 50 comments
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping Reddit sentiment: {e}")
            return {"error": str(e)}
    
    def scrape_google_trends(self, symbol: str, timeframe: str = '1m') -> Dict:
        """Scrape Google Trends data for a symbol"""
        try:
            # Build payload
            self.pytrends.build_payload([symbol], cat=0, timeframe=timeframe, geo='', gprop='')
            
            # Get interest over time
            interest_data = self.pytrends.interest_over_time()
            
            # Get related queries
            related_queries = self.pytrends.related_queries()
            
            # Get interest by region
            interest_by_region = self.pytrends.interest_by_region()
            
            # Process data
            trends_data = {
                'symbol': symbol,
                'timeframe': timeframe,
                'interest_over_time': interest_data.to_dict() if not interest_data.empty else {},
                'related_queries': related_queries,
                'interest_by_region': interest_by_region.to_dict() if not interest_by_region.empty else {},
                'scraped_at': datetime.now().isoformat()
            }
            
            return trends_data
            
        except Exception as e:
            logger.error(f"Error scraping Google Trends: {e}")
            return {"error": str(e)}
    
    def scrape_twitter_sentiment(self, symbol: str, limit: int = 100) -> Dict:
        """Scrape Twitter sentiment (using free methods)"""
        try:
            # Note: This is a simplified implementation
            # In production, you would use Twitter API v2 with proper authentication
            
            tweets = []
            
            # Search for tweets about the symbol
            search_terms = [f"${symbol}", f"#{symbol}", symbol]
            
            for term in search_terms:
                try:
                    # This is a placeholder - in reality you'd use Twitter API
                    # For now, we'll simulate the data structure
                    mock_tweets = self._get_mock_twitter_data(symbol, term, limit//len(search_terms))
                    tweets.extend(mock_tweets)
                    
                except Exception as e:
                    logger.error(f"Error searching for term {term}: {e}")
                    continue
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_twitter_sentiment(tweets)
            
            return {
                'symbol': symbol,
                'source': 'twitter',
                'total_tweets': len(tweets),
                'sentiment_analysis': sentiment_analysis,
                'tweets': tweets[:20],  # Return top 20 tweets
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping Twitter sentiment: {e}")
            return {"error": str(e)}
    
    def scrape_news_sentiment(self, symbol: str, limit: int = 50) -> Dict:
        """Scrape news sentiment from free sources"""
        try:
            news_articles = []
            
            # Search for news articles
            search_terms = [symbol, f"{symbol} stock", f"{symbol} earnings"]
            
            for term in search_terms:
                try:
                    # This is a placeholder - in reality you'd use news APIs
                    # For now, we'll simulate the data structure
                    mock_articles = self._get_mock_news_data(symbol, term, limit//len(search_terms))
                    news_articles.extend(mock_articles)
                    
                except Exception as e:
                    logger.error(f"Error searching for news term {term}: {e}")
                    continue
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_news_sentiment(news_articles)
            
            return {
                'symbol': symbol,
                'source': 'news',
                'total_articles': len(news_articles),
                'sentiment_analysis': sentiment_analysis,
                'articles': news_articles[:10],  # Return top 10 articles
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping news sentiment: {e}")
            return {"error": str(e)}
    
    def get_comprehensive_sentiment(self, symbol: str) -> Dict:
        """Get comprehensive sentiment from all sources"""
        try:
            # Scrape from all sources
            reddit_data = self.scrape_reddit_sentiment(symbol)
            trends_data = self.scrape_google_trends(symbol)
            twitter_data = self.scrape_twitter_sentiment(symbol)
            news_data = self.scrape_news_sentiment(symbol)
            
            # Combine sentiment analysis
            combined_sentiment = self._combine_sentiment_analysis([
                reddit_data.get('sentiment_analysis', {}),
                twitter_data.get('sentiment_analysis', {}),
                news_data.get('sentiment_analysis', {})
            ])
            
            return {
                'symbol': symbol,
                'comprehensive_sentiment': combined_sentiment,
                'sources': {
                    'reddit': reddit_data,
                    'google_trends': trends_data,
                    'twitter': twitter_data,
                    'news': news_data
                },
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive sentiment: {e}")
            return {"error": str(e)}
    
    def _analyze_reddit_sentiment(self, posts: List[Dict], comments: List[Dict]) -> Dict:
        """Analyze Reddit sentiment"""
        try:
            # Simple sentiment analysis based on upvotes and keywords
            positive_keywords = ['bull', 'moon', 'buy', 'long', 'profit', 'gain', 'up', 'rise', 'good', 'great']
            negative_keywords = ['bear', 'crash', 'sell', 'short', 'loss', 'down', 'fall', 'bad', 'terrible', 'dump']
            
            total_score = 0
            total_posts = len(posts)
            total_comments = len(comments)
            
            # Analyze posts
            for post in posts:
                text = f"{post['title']} {post['text']}".lower()
                score = post['score']
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in text)
                negative_count = sum(1 for keyword in negative_keywords if keyword in text)
                
                if positive_count > negative_count:
                    total_score += score
                elif negative_count > positive_count:
                    total_score -= score
            
            # Analyze comments
            for comment in comments:
                text = comment['body'].lower()
                score = comment['score']
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in text)
                negative_count = sum(1 for keyword in negative_keywords if keyword in text)
                
                if positive_count > negative_count:
                    total_score += score
                elif negative_count > positive_count:
                    total_score -= score
            
            # Calculate sentiment score
            if total_posts + total_comments > 0:
                sentiment_score = total_score / (total_posts + total_comments)
            else:
                sentiment_score = 0
            
            # Determine sentiment
            if sentiment_score > 0.1:
                sentiment = 'positive'
            elif sentiment_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'total_posts': total_posts,
                'total_comments': total_comments,
                'confidence': min(abs(sentiment_score), 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Reddit sentiment: {e}")
            return {"sentiment": "neutral", "sentiment_score": 0, "confidence": 0}
    
    def _analyze_twitter_sentiment(self, tweets: List[Dict]) -> Dict:
        """Analyze Twitter sentiment"""
        try:
            # Simple sentiment analysis based on keywords
            positive_keywords = ['bull', 'moon', 'buy', 'long', 'profit', 'gain', 'up', 'rise', 'good', 'great']
            negative_keywords = ['bear', 'crash', 'sell', 'short', 'loss', 'down', 'fall', 'bad', 'terrible', 'dump']
            
            total_score = 0
            total_tweets = len(tweets)
            
            for tweet in tweets:
                text = tweet['text'].lower()
                score = tweet.get('score', 1)
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in text)
                negative_count = sum(1 for keyword in negative_keywords if keyword in text)
                
                if positive_count > negative_count:
                    total_score += score
                elif negative_count > positive_count:
                    total_score -= score
            
            # Calculate sentiment score
            if total_tweets > 0:
                sentiment_score = total_score / total_tweets
            else:
                sentiment_score = 0
            
            # Determine sentiment
            if sentiment_score > 0.1:
                sentiment = 'positive'
            elif sentiment_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'total_tweets': total_tweets,
                'confidence': min(abs(sentiment_score), 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing Twitter sentiment: {e}")
            return {"sentiment": "neutral", "sentiment_score": 0, "confidence": 0}
    
    def _analyze_news_sentiment(self, articles: List[Dict]) -> Dict:
        """Analyze news sentiment"""
        try:
            # Simple sentiment analysis based on keywords
            positive_keywords = ['bull', 'moon', 'buy', 'long', 'profit', 'gain', 'up', 'rise', 'good', 'great']
            negative_keywords = ['bear', 'crash', 'sell', 'short', 'loss', 'down', 'fall', 'bad', 'terrible', 'dump']
            
            total_score = 0
            total_articles = len(articles)
            
            for article in articles:
                text = f"{article['title']} {article['content']}".lower()
                
                positive_count = sum(1 for keyword in positive_keywords if keyword in text)
                negative_count = sum(1 for keyword in negative_keywords if keyword in text)
                
                if positive_count > negative_count:
                    total_score += 1
                elif negative_count > positive_count:
                    total_score -= 1
            
            # Calculate sentiment score
            if total_articles > 0:
                sentiment_score = total_score / total_articles
            else:
                sentiment_score = 0
            
            # Determine sentiment
            if sentiment_score > 0.1:
                sentiment = 'positive'
            elif sentiment_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'sentiment_score': sentiment_score,
                'total_articles': total_articles,
                'confidence': min(abs(sentiment_score), 1.0)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing news sentiment: {e}")
            return {"sentiment": "neutral", "sentiment_score": 0, "confidence": 0}
    
    def _combine_sentiment_analysis(self, sentiment_analyses: List[Dict]) -> Dict:
        """Combine sentiment analysis from multiple sources"""
        try:
            if not sentiment_analyses:
                return {"sentiment": "neutral", "sentiment_score": 0, "confidence": 0}
            
            # Calculate weighted average
            total_score = 0
            total_confidence = 0
            total_sources = len(sentiment_analyses)
            
            for analysis in sentiment_analyses:
                if 'sentiment_score' in analysis and 'confidence' in analysis:
                    total_score += analysis['sentiment_score'] * analysis['confidence']
                    total_confidence += analysis['confidence']
            
            if total_confidence > 0:
                combined_score = total_score / total_confidence
                combined_confidence = total_confidence / total_sources
            else:
                combined_score = 0
                combined_confidence = 0
            
            # Determine combined sentiment
            if combined_score > 0.1:
                sentiment = 'positive'
            elif combined_score < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'sentiment_score': combined_score,
                'confidence': combined_confidence,
                'sources_analyzed': total_sources
            }
            
        except Exception as e:
            logger.error(f"Error combining sentiment analysis: {e}")
            return {"sentiment": "neutral", "sentiment_score": 0, "confidence": 0}
    
    def _get_mock_twitter_data(self, symbol: str, term: str, limit: int) -> List[Dict]:
        """Get mock Twitter data (placeholder)"""
        # This is a placeholder for Twitter data
        # In production, you would use Twitter API v2
        return [
            {
                'id': f"tweet_{i}",
                'text': f"Mock tweet about {symbol} - {term}",
                'score': 1,
                'created_at': datetime.now().isoformat(),
                'author': f"user_{i}"
            }
            for i in range(limit)
        ]
    
    def _get_mock_news_data(self, symbol: str, term: str, limit: int) -> List[Dict]:
        """Get mock news data (placeholder)"""
        # This is a placeholder for news data
        # In production, you would use news APIs
        return [
            {
                'id': f"article_{i}",
                'title': f"Mock news article about {symbol} - {term}",
                'content': f"Mock content about {symbol} and {term}",
                'url': f"https://example.com/article_{i}",
                'published_at': datetime.now().isoformat(),
                'source': 'Mock News'
            }
            for i in range(limit)
        ]
