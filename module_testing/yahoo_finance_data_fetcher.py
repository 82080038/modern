#!/usr/bin/env python3
"""
Yahoo Finance Data Fetcher
==========================

Script untuk mengambil data saham dari Yahoo Finance dengan rate limiter
dan fokus pada saham Indonesia (IDX) terlebih dahulu.

Author: AI Assistant
Date: 2025-01-16
"""

import sys
import os
import json
import time
import mysql.connector
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class YahooFinanceDataFetcher:
    """Yahoo Finance Data Fetcher with Rate Limiter"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.connection = None
        self.cursor = None
        
        # Rate limiting configuration
        self.request_delay = 1.0  # 1 second between requests
        self.batch_delay = 5.0    # 5 seconds between batches
        self.max_retries = 3
        self.timeout = 30
        
        # Indonesian stock symbols (IDX)
        self.indonesian_stocks = [
            # Banking
            'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BNGA.JK', 'BBNI.JK',
            'BTPN.JK', 'BJB.JK', 'BKSW.JK', 'BJTM.JK', 'BACA.JK',
            
            # Technology
            'TLKM.JK', 'ISAT.JK', 'EXCL.JK', 'FREN.JK', 'SIDO.JK',
            'GOTO.JK', 'TOWR.JK', 'TCOM.JK', 'TINS.JK', 'TSPC.JK',
            
            # Mining & Energy
            'ANTM.JK', 'ADRO.JK', 'PTBA.JK', 'PGAS.JK', 'PTPP.JK',
            'PTRO.JK', 'PTRS.JK', 'PTRM.JK', 'PTRK.JK', 'PTRP.JK',
            
            # Consumer Goods
            'UNVR.JK', 'INDF.JK', 'ICBP.JK', 'GGRM.JK', 'MLBI.JK',
            'MYOR.JK', 'SCMA.JK', 'SIDO.JK', 'TSPC.JK', 'UNVR.JK',
            
            # Property & Real Estate
            'BSDE.JK', 'CTRA.JK', 'LPPI.JK', 'SMRA.JK', 'ASRI.JK',
            'BAPA.JK', 'BIPP.JK', 'BPTR.JK', 'BSIM.JK', 'BUMI.JK',
            
            # Automotive
            'ASII.JK', 'AUTO.JK', 'BOLT.JK', 'INCO.JK', 'META.JK',
            'PTPP.JK', 'PTRO.JK', 'PTRS.JK', 'PTRM.JK', 'PTRK.JK',
            
            # Infrastructure
            'ADHI.JK', 'WIKA.JK', 'JSMR.JK', 'PTPP.JK', 'PTRO.JK',
            'PTRS.JK', 'PTRM.JK', 'PTRK.JK', 'PTRP.JK', 'PTRO.JK',
            
            # Healthcare
            'KLBF.JK', 'SIDO.JK', 'TSPC.JK', 'UNVR.JK', 'ICBP.JK',
            'GGRM.JK', 'MLBI.JK', 'MYOR.JK', 'SCMA.JK', 'SIDO.JK',
            
            # Agriculture
            'AALI.JK', 'ADRO.JK', 'ANTM.JK', 'INCO.JK', 'PTBA.JK',
            'PGAS.JK', 'PTPP.JK', 'PTRO.JK', 'PTRS.JK', 'PTRM.JK',
            
            # Finance
            'BBCA.JK', 'BBRI.JK', 'BMRI.JK', 'BNGA.JK', 'BBNI.JK',
            'BTPN.JK', 'BJB.JK', 'BKSW.JK', 'BJTM.JK', 'BACA.JK'
        ]
        
        # Remove duplicates and limit to 50 stocks for initial testing
        self.indonesian_stocks = list(set(self.indonesian_stocks))[:50]
        
        # Setup session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def connect_database(self):
        """Connect to database"""
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor()
            print("[PASS] Database connection established")
            return True
        except Exception as e:
            print(f"[FAIL] Database connection failed: {e}")
            return False
    
    def disconnect_database(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("[PASS] Database connection closed")
    
    def fetch_stock_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """Fetch stock data for a symbol with rate limiting"""
        try:
            print(f"   Fetching data for {symbol}...")
            
            # Rate limiting
            time.sleep(self.request_delay)
            
            # Fetch data from Yahoo Finance
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            
            if data.empty:
                print(f"     [WARN] No data found for {symbol}")
                return None
            
            # Add symbol column
            data['symbol'] = symbol
            data['date'] = data.index.date
            
            print(f"     [PASS] Fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            print(f"     [ERROR] Failed to fetch data for {symbol}: {e}")
            return None
    
    def fetch_fundamental_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch fundamental data for a symbol"""
        try:
            print(f"   Fetching fundamental data for {symbol}...")
            
            # Rate limiting
            time.sleep(self.request_delay)
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info:
                print(f"     [WARN] No fundamental data found for {symbol}")
                return None
            
            # Extract relevant fundamental data
            fundamental_data = {
                'symbol': symbol,
                'pe_ratio': info.get('trailingPE', None),
                'pb_ratio': info.get('priceToBook', None),
                'roe': info.get('returnOnEquity', None),
                'roa': info.get('returnOnAssets', None),
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'market_cap': info.get('marketCap', None),
                'enterprise_value': info.get('enterpriseValue', None),
                'revenue': info.get('totalRevenue', None),
                'profit_margin': info.get('profitMargins', None),
                'dividend_yield': info.get('dividendYield', None),
                'beta': info.get('beta', None),
                'sector': info.get('sector', None),
                'industry': info.get('industry', None)
            }
            
            print(f"     [PASS] Fetched fundamental data for {symbol}")
            return fundamental_data
            
        except Exception as e:
            print(f"     [ERROR] Failed to fetch fundamental data for {symbol}: {e}")
            return None
    
    def fetch_news_sentiment(self, symbol: str) -> Optional[List[Dict[str, Any]]]:
        """Fetch news sentiment for a symbol"""
        try:
            print(f"   Fetching news sentiment for {symbol}...")
            
            # Rate limiting
            time.sleep(self.request_delay)
            
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            if not news:
                print(f"     [WARN] No news found for {symbol}")
                return None
            
            # Process news data
            sentiment_data = []
            for article in news[:10]:  # Limit to 10 most recent articles
                sentiment_data.append({
                    'symbol': symbol,
                    'title': article.get('title', ''),
                    'summary': article.get('summary', ''),
                    'publisher': article.get('publisher', ''),
                    'published_at': datetime.fromtimestamp(article.get('providerPublishTime', 0)),
                    'sentiment_score': 0.0,  # Placeholder - would need sentiment analysis
                    'confidence': 0.5  # Placeholder
                })
            
            print(f"     [PASS] Fetched {len(sentiment_data)} news articles for {symbol}")
            return sentiment_data
            
        except Exception as e:
            print(f"     [ERROR] Failed to fetch news sentiment for {symbol}: {e}")
            return None
    
    def populate_historical_data(self, data: pd.DataFrame) -> bool:
        """Populate historical data into database"""
        try:
            if data is None or data.empty:
                return False
            
            symbol = data['symbol'].iloc[0]
            print(f"   Populating historical data for {symbol}...")
            
            # Prepare data for insertion
            records = []
            for _, row in data.iterrows():
                records.append((
                    symbol,
                    row['date'],
                    float(row['Open']) if pd.notna(row['Open']) else None,
                    float(row['High']) if pd.notna(row['High']) else None,
                    float(row['Low']) if pd.notna(row['Low']) else None,
                    float(row['Close']) if pd.notna(row['Close']) else None,
                    int(row['Volume']) if pd.notna(row['Volume']) else None,
                    datetime.now()
                ))
            
            # Insert into historical_ohlcv_daily
            insert_query = """
                INSERT INTO historical_ohlcv_daily (symbol, date, open, high, low, close, volume, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                open = VALUES(open),
                high = VALUES(high),
                low = VALUES(low),
                close = VALUES(close),
                volume = VALUES(volume),
                created_at = VALUES(created_at)
            """
            
            self.cursor.executemany(insert_query, records)
            self.connection.commit()
            
            print(f"     [PASS] Inserted {len(records)} historical records for {symbol}")
            return True
            
        except Exception as e:
            print(f"     [ERROR] Failed to populate historical data for {symbol}: {e}")
            return False
    
    def populate_market_data(self, data: pd.DataFrame) -> bool:
        """Populate market data into database"""
        try:
            if data is None or data.empty:
                return False
            
            symbol = data['symbol'].iloc[0]
            print(f"   Populating market data for {symbol}...")
            
            # Prepare data for insertion
            records = []
            for _, row in data.iterrows():
                records.append((
                    symbol,
                    row.name,  # timestamp
                    float(row['Close']) if pd.notna(row['Close']) else None,
                    int(row['Volume']) if pd.notna(row['Volume']) else None,
                    float(row['High']) if pd.notna(row['High']) else None,
                    float(row['Low']) if pd.notna(row['Low']) else None,
                    float(row['Open']) if pd.notna(row['Open']) else None,
                    float(row['Close']) if pd.notna(row['Close']) else None,
                    datetime.now()
                ))
            
            # Insert into market_data
            insert_query = """
                INSERT INTO market_data (symbol, timestamp, price, volume, high, low, open, close, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                price = VALUES(price),
                volume = VALUES(volume),
                high = VALUES(high),
                low = VALUES(low),
                open = VALUES(open),
                close = VALUES(close),
                created_at = VALUES(created_at)
            """
            
            self.cursor.executemany(insert_query, records)
            self.connection.commit()
            
            print(f"     [PASS] Inserted {len(records)} market data records for {symbol}")
            return True
            
        except Exception as e:
            print(f"     [ERROR] Failed to populate market data for {symbol}: {e}")
            return False
    
    def populate_fundamental_data(self, fundamental_data: Dict[str, Any]) -> bool:
        """Populate fundamental data into database"""
        try:
            if not fundamental_data:
                return False
            
            symbol = fundamental_data['symbol']
            print(f"   Populating fundamental data for {symbol}...")
            
            # Insert into fundamental_data
            insert_query = """
                INSERT INTO fundamental_data (
                    symbol, date, pe_ratio, pb_ratio, roe, roa, debt_to_equity, 
                    current_ratio, market_cap, enterprise_value, revenue, 
                    profit_margin, dividend_yield, beta, sector, industry, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                pe_ratio = VALUES(pe_ratio),
                pb_ratio = VALUES(pb_ratio),
                roe = VALUES(roe),
                roa = VALUES(roa),
                debt_to_equity = VALUES(debt_to_equity),
                current_ratio = VALUES(current_ratio),
                market_cap = VALUES(market_cap),
                enterprise_value = VALUES(enterprise_value),
                revenue = VALUES(revenue),
                profit_margin = VALUES(profit_margin),
                dividend_yield = VALUES(dividend_yield),
                beta = VALUES(beta),
                sector = VALUES(sector),
                industry = VALUES(industry),
                created_at = VALUES(created_at)
            """
            
            record = (
                symbol,
                datetime.now().date(),
                fundamental_data.get('pe_ratio'),
                fundamental_data.get('pb_ratio'),
                fundamental_data.get('roe'),
                fundamental_data.get('roa'),
                fundamental_data.get('debt_to_equity'),
                fundamental_data.get('current_ratio'),
                fundamental_data.get('market_cap'),
                fundamental_data.get('enterprise_value'),
                fundamental_data.get('revenue'),
                fundamental_data.get('profit_margin'),
                fundamental_data.get('dividend_yield'),
                fundamental_data.get('beta'),
                fundamental_data.get('sector'),
                fundamental_data.get('industry'),
                datetime.now()
            )
            
            self.cursor.execute(insert_query, record)
            self.connection.commit()
            
            print(f"     [PASS] Inserted fundamental data for {symbol}")
            return True
            
        except Exception as e:
            print(f"     [ERROR] Failed to populate fundamental data for {symbol}: {e}")
            return False
    
    def populate_sentiment_data(self, sentiment_data: List[Dict[str, Any]]) -> bool:
        """Populate sentiment data into database"""
        try:
            if not sentiment_data:
                return False
            
            symbol = sentiment_data[0]['symbol']
            print(f"   Populating sentiment data for {symbol}...")
            
            # Insert into sentiment_data
            insert_query = """
                INSERT INTO sentiment_data (
                    symbol, title, summary, publisher, published_at, 
                    sentiment_score, confidence, created_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                title = VALUES(title),
                summary = VALUES(summary),
                publisher = VALUES(publisher),
                published_at = VALUES(published_at),
                sentiment_score = VALUES(sentiment_score),
                confidence = VALUES(confidence),
                created_at = VALUES(created_at)
            """
            
            records = []
            for article in sentiment_data:
                records.append((
                    article['symbol'],
                    article['title'],
                    article['summary'],
                    article['publisher'],
                    article['published_at'],
                    article['sentiment_score'],
                    article['confidence'],
                    datetime.now()
                ))
            
            self.cursor.executemany(insert_query, records)
            self.connection.commit()
            
            print(f"     [PASS] Inserted {len(records)} sentiment records for {symbol}")
            return True
            
        except Exception as e:
            print(f"     [ERROR] Failed to populate sentiment data for {symbol}: {e}")
            return False
    
    def fetch_all_indonesian_stocks(self) -> Dict[str, Any]:
        """Fetch data for all Indonesian stocks"""
        print("FETCHING INDONESIAN STOCK DATA")
        print("=" * 80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total stocks: {len(self.indonesian_stocks)}")
        print("=" * 80)
        
        results = {
            'test_type': 'yahoo_finance_data_fetch',
            'test_start': datetime.now().isoformat(),
            'database_connection': False,
            'stocks_processed': 0,
            'stocks_successful': 0,
            'stocks_failed': 0,
            'data_fetched': {},
            'errors': [],
            'summary': {}
        }
        
        # Connect to database
        if not self.connect_database():
            results['errors'].append('Database connection failed')
            return results
        
        results['database_connection'] = True
        
        # Process each stock
        for i, symbol in enumerate(self.indonesian_stocks, 1):
            print(f"\n{i}/{len(self.indonesian_stocks)} Processing {symbol}")
            print("-" * 60)
            
            try:
                results['stocks_processed'] += 1
                
                # Fetch historical data
                historical_data = self.fetch_stock_data(symbol)
                if historical_data is not None:
                    self.populate_historical_data(historical_data)
                    self.populate_market_data(historical_data)
                
                # Fetch fundamental data
                fundamental_data = self.fetch_fundamental_data(symbol)
                if fundamental_data is not None:
                    self.populate_fundamental_data(fundamental_data)
                
                # Fetch sentiment data
                sentiment_data = self.fetch_news_sentiment(symbol)
                if sentiment_data is not None:
                    self.populate_sentiment_data(sentiment_data)
                
                results['stocks_successful'] += 1
                print(f"   [PASS] Successfully processed {symbol}")
                
            except Exception as e:
                results['stocks_failed'] += 1
                results['errors'].append(f"Error processing {symbol}: {e}")
                print(f"   [ERROR] Failed to process {symbol}: {e}")
            
            # Batch delay
            if i % 10 == 0:
                print(f"   [INFO] Processed {i} stocks, waiting {self.batch_delay} seconds...")
                time.sleep(self.batch_delay)
        
        # Generate summary
        results['summary'] = {
            'total_stocks': len(self.indonesian_stocks),
            'stocks_processed': results['stocks_processed'],
            'stocks_successful': results['stocks_successful'],
            'stocks_failed': results['stocks_failed'],
            'success_rate': (results['stocks_successful'] / results['stocks_processed'] * 100) if results['stocks_processed'] > 0 else 0
        }
        
        # Disconnect from database
        self.disconnect_database()
        
        # Generate report
        self.generate_fetch_report(results)
        
        return results
    
    def generate_fetch_report(self, results: Dict[str, Any]) -> None:
        """Generate fetch report"""
        print("\nYAHOO FINANCE DATA FETCH REPORT")
        print("=" * 80)
        
        summary = results.get('summary', {})
        print(f"Summary:")
        print(f"  Total Stocks: {summary.get('total_stocks', 0)}")
        print(f"  Stocks Processed: {summary.get('stocks_processed', 0)}")
        print(f"  Stocks Successful: {summary.get('stocks_successful', 0)}")
        print(f"  Stocks Failed: {summary.get('stocks_failed', 0)}")
        print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")
        
        errors = results.get('errors', [])
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for error in errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(errors) > 10:
                print(f"  ... and {len(errors) - 10} more errors")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"yahoo_finance_fetch_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nFetch results saved to: {results_file}")
        print(f"Fetch completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'scalper',
        'port': 3306
    }
    
    # Create fetcher instance
    fetcher = YahooFinanceDataFetcher(db_config)
    
    # Fetch all Indonesian stocks
    results = fetcher.fetch_all_indonesian_stocks()
    
    return results

if __name__ == "__main__":
    main()
