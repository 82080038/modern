"""
Web Scraping Service untuk Robust Data Collection
"""
from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date, timedelta
import logging
import requests
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse
import json
import re
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ScrapingStatus(Enum):
    """Scraping status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

@dataclass
class ScrapingResult:
    """Scraping result"""
    url: str
    status: ScrapingStatus
    data: Dict
    error: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class WebScrapingService:
    """Service untuk robust web scraping"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # User agents for rotation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        
        # Rate limiting
        self.request_delays = {
            'default': 1.0,
            'fast': 0.5,
            'slow': 2.0
        }
        
        # Session for connection pooling
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def scrape_url(self, url: str, delay: float = None, retries: int = 3) -> ScrapingResult:
        """Scrape a single URL with error handling and retries"""
        try:
            if delay is None:
                delay = self.request_delays['default']
            
            # Rate limiting
            time.sleep(delay)
            
            # Rotate user agent
            user_agent = random.choice(self.user_agents)
            headers = {'User-Agent': user_agent}
            
            # Make request with retries
            for attempt in range(retries):
                try:
                    response = self.session.get(url, headers=headers, timeout=30)
                    response.raise_for_status()
                    
                    # Parse content
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Extract data
                    data = self._extract_data_from_soup(soup, url)
                    
                    return ScrapingResult(
                        url=url,
                        status=ScrapingStatus.COMPLETED,
                        data=data
                    )
                    
                except requests.exceptions.RequestException as e:
                    if attempt == retries - 1:
                        return ScrapingResult(
                            url=url,
                            status=ScrapingStatus.FAILED,
                            data={},
                            error=str(e)
                        )
                    else:
                        # Exponential backoff
                        time.sleep(2 ** attempt)
                        continue
            
            return ScrapingResult(
                url=url,
                status=ScrapingStatus.FAILED,
                data={},
                error="Max retries exceeded"
            )
            
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {e}")
            return ScrapingResult(
                url=url,
                status=ScrapingStatus.FAILED,
                data={},
                error=str(e)
            )
    
    def scrape_multiple_urls(self, urls: List[str], delay: float = None, max_concurrent: int = 5) -> List[ScrapingResult]:
        """Scrape multiple URLs with concurrency control"""
        try:
            results = []
            
            for i, url in enumerate(urls):
                # Add delay between requests
                if i > 0 and delay:
                    time.sleep(delay)
                
                result = self.scrape_url(url, delay=0.1)  # Minimal delay for concurrent requests
                results.append(result)
                
                # Check if we need to slow down
                if result.status == ScrapingStatus.RATE_LIMITED:
                    time.sleep(5)  # Wait longer if rate limited
            
            return results
            
        except Exception as e:
            logger.error(f"Error scraping multiple URLs: {e}")
            return []
    
    def scrape_idx_data(self, symbol: str = None) -> Dict:
        """Scrape IDX data from idx.co.id"""
        try:
            base_url = "https://www.idx.co.id"
            
            if symbol:
                # Scrape specific symbol
                url = f"{base_url}/en-us/listed-companies/company-profile?stock_code={symbol}"
                result = self.scrape_url(url)
                
                if result.status == ScrapingStatus.COMPLETED:
                    return {
                        'symbol': symbol,
                        'data': result.data,
                        'source': 'idx.co.id',
                        'scraped_at': result.timestamp.isoformat()
                    }
                else:
                    return {"error": result.error}
            else:
                # Scrape market overview
                urls = [
                    f"{base_url}/en-us/listed-companies/company-profile",
                    f"{base_url}/en-us/market-data/stock-summary"
                ]
                
                results = self.scrape_multiple_urls(urls)
                
                market_data = {}
                for result in results:
                    if result.status == ScrapingStatus.COMPLETED:
                        market_data.update(result.data)
                
                return {
                    'market_data': market_data,
                    'source': 'idx.co.id',
                    'scraped_at': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error scraping IDX data: {e}")
            return {"error": str(e)}
    
    def scrape_investing_com(self, symbol: str = None) -> Dict:
        """Scrape data from investing.com"""
        try:
            base_url = "https://www.investing.com"
            
            if symbol:
                # Scrape specific symbol
                url = f"{base_url}/equities/{symbol.lower()}"
                result = self.scrape_url(url)
                
                if result.status == ScrapingStatus.COMPLETED:
                    return {
                        'symbol': symbol,
                        'data': result.data,
                        'source': 'investing.com',
                        'scraped_at': result.timestamp.isoformat()
                    }
                else:
                    return {"error": result.error}
            else:
                # Scrape market overview
                urls = [
                    f"{base_url}/indices/indonesia",
                    f"{base_url}/equities/indonesia"
                ]
                
                results = self.scrape_multiple_urls(urls)
                
                market_data = {}
                for result in results:
                    if result.status == ScrapingStatus.COMPLETED:
                        market_data.update(result.data)
                
                return {
                    'market_data': market_data,
                    'source': 'investing.com',
                    'scraped_at': datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error scraping investing.com: {e}")
            return {"error": str(e)}
    
    def scrape_financial_statements(self, symbol: str, source: str = "idx") -> Dict:
        """Scrape financial statements for a symbol"""
        try:
            if source == "idx":
                url = f"https://www.idx.co.id/en-us/listed-companies/company-profile?stock_code={symbol}"
                result = self.scrape_url(url)
                
                if result.status == ScrapingStatus.COMPLETED:
                    # Extract financial data
                    financial_data = self._extract_financial_statements(result.data)
                    
                    return {
                        'symbol': symbol,
                        'financial_statements': financial_data,
                        'source': 'idx.co.id',
                        'scraped_at': result.timestamp.isoformat()
                    }
                else:
                    return {"error": result.error}
            
            elif source == "investing":
                url = f"https://www.investing.com/equities/{symbol.lower()}"
                result = self.scrape_url(url)
                
                if result.status == ScrapingStatus.COMPLETED:
                    # Extract financial data
                    financial_data = self._extract_financial_statements(result.data)
                    
                    return {
                        'symbol': symbol,
                        'financial_statements': financial_data,
                        'source': 'investing.com',
                        'scraped_at': result.timestamp.isoformat()
                    }
                else:
                    return {"error": result.error}
            
            else:
                return {"error": f"Unsupported source: {source}"}
            
        except Exception as e:
            logger.error(f"Error scraping financial statements: {e}")
            return {"error": str(e)}
    
    def scrape_news_articles(self, symbol: str, limit: int = 20) -> Dict:
        """Scrape news articles for a symbol"""
        try:
            # Search for news articles
            search_terms = [symbol, f"{symbol} stock", f"{symbol} news"]
            articles = []
            
            for term in search_terms:
                try:
                    # This is a placeholder - in production you would use news APIs
                    mock_articles = self._get_mock_news_articles(symbol, term, limit//len(search_terms))
                    articles.extend(mock_articles)
                    
                except Exception as e:
                    logger.error(f"Error searching for term {term}: {e}")
                    continue
            
            return {
                'symbol': symbol,
                'articles': articles,
                'total_articles': len(articles),
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping news articles: {e}")
            return {"error": str(e)}
    
    def scrape_economic_calendar(self, start_date: date = None, end_date: date = None) -> Dict:
        """Scrape economic calendar data"""
        try:
            if not start_date:
                start_date = date.today()
            if not end_date:
                end_date = start_date + timedelta(days=30)
            
            # Scrape from multiple sources
            sources = [
                "https://www.investing.com/economic-calendar/",
                "https://www.forexfactory.com/calendar"
            ]
            
            results = self.scrape_multiple_urls(sources)
            
            events = []
            for result in results:
                if result.status == ScrapingStatus.COMPLETED:
                    events.extend(result.data.get('events', []))
            
            return {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'events': events,
                'total_events': len(events),
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error scraping economic calendar: {e}")
            return {"error": str(e)}
    
    def _extract_data_from_soup(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract structured data from BeautifulSoup object"""
        try:
            data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'meta_description': '',
                'headings': [],
                'links': [],
                'tables': [],
                'text_content': ''
            }
            
            # Extract meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc:
                data['meta_description'] = meta_desc.get('content', '')
            
            # Extract headings
            for level in range(1, 7):
                headings = soup.find_all(f'h{level}')
                for heading in headings:
                    data['headings'].append({
                        'level': level,
                        'text': heading.get_text().strip()
                    })
            
            # Extract links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    absolute_url = urljoin(url, href)
                    data['links'].append({
                        'text': link.get_text().strip(),
                        'url': absolute_url
                    })
            
            # Extract tables
            tables = soup.find_all('table')
            for table in tables:
                table_data = self._extract_table_data(table)
                if table_data:
                    data['tables'].append(table_data)
            
            # Extract text content
            text_content = soup.get_text()
            data['text_content'] = ' '.join(text_content.split())
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting data from soup: {e}")
            return {}
    
    def _extract_table_data(self, table) -> Dict:
        """Extract data from HTML table"""
        try:
            rows = table.find_all('tr')
            table_data = {
                'headers': [],
                'rows': []
            }
            
            for i, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                cell_data = [cell.get_text().strip() for cell in cells]
                
                if i == 0:  # First row as headers
                    table_data['headers'] = cell_data
                else:
                    table_data['rows'].append(cell_data)
            
            return table_data
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return {}
    
    def _extract_financial_statements(self, data: Dict) -> Dict:
        """Extract financial statements from scraped data"""
        try:
            # This is a placeholder - in production you would parse financial data
            financial_data = {
                'income_statement': {},
                'balance_sheet': {},
                'cash_flow': {},
                'ratios': {}
            }
            
            # Mock financial data
            financial_data['income_statement'] = {
                'revenue': 1000000,
                'net_income': 100000,
                'eps': 1.0
            }
            
            financial_data['balance_sheet'] = {
                'total_assets': 5000000,
                'total_liabilities': 2000000,
                'shareholders_equity': 3000000
            }
            
            financial_data['cash_flow'] = {
                'operating_cash_flow': 150000,
                'investing_cash_flow': -50000,
                'financing_cash_flow': -25000
            }
            
            financial_data['ratios'] = {
                'pe_ratio': 15.0,
                'pb_ratio': 2.0,
                'debt_to_equity': 0.67
            }
            
            return financial_data
            
        except Exception as e:
            logger.error(f"Error extracting financial statements: {e}")
            return {}
    
    def _get_mock_news_articles(self, symbol: str, term: str, limit: int) -> List[Dict]:
        """Get mock news articles (placeholder)"""
        articles = []
        
        for i in range(limit):
            articles.append({
                'id': f"article_{i}",
                'title': f"Mock news article about {symbol} - {term}",
                'content': f"Mock content about {symbol} and {term}",
                'url': f"https://example.com/article_{i}",
                'published_at': datetime.now().isoformat(),
                'source': 'Mock News',
                'sentiment': 'neutral'
            })
        
        return articles
    
    def get_scraping_status(self) -> Dict:
        """Get current scraping status and statistics"""
        try:
            # This would query database for scraping statistics in production
            status = {
                'total_requests': 1000,
                'successful_requests': 950,
                'failed_requests': 50,
                'rate_limited_requests': 10,
                'average_response_time': 1.5,
                'last_scraped': datetime.now().isoformat(),
                'active_sources': ['idx.co.id', 'investing.com', 'forexfactory.com']
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting scraping status: {e}")
            return {"error": str(e)}
    
    def cleanup_session(self):
        """Cleanup session and connections"""
        try:
            self.session.close()
        except Exception as e:
            logger.error(f"Error cleaning up session: {e}")
