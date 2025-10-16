"""
SIMPLE DATA QUALITY CHECK
=========================

Pemeriksaan sederhana kualitas data database untuk mengidentifikasi masalah.

Author: AI Assistant
Date: 2025-01-17
"""

import asyncio
import logging
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import json
import mysql.connector
from mysql.connector import Error
import yfinance as yf
import time

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleDataQualityCheck:
    """
    Simple Data Quality Check - Pemeriksaan sederhana kualitas data
    """
    
    def __init__(self):
        # Database configuration
        self.db_config = {
            'host': 'localhost',
            'database': 'scalper',
            'user': 'root',
            'password': '',
            'port': 3306
        }
        
    async def run_simple_data_check(self) -> Dict[str, Any]:
        """Run simple data quality check"""
        try:
            print("SIMPLE DATA QUALITY CHECK")
            print("=" * 60)
            print("OBJECTIVE: Identify basic data quality issues")
            print("=" * 60)
            
            # Step 1: Check database overview
            print("\nStep 1: Checking Database Overview...")
            db_overview = await self._check_database_overview()
            
            # Step 2: Check sample data quality
            print("\nStep 2: Checking Sample Data Quality...")
            sample_quality = await self._check_sample_data_quality()
            
            # Step 3: Check specific symbols
            print("\nStep 3: Checking Specific Symbols...")
            symbol_analysis = await self._analyze_specific_symbols()
            
            # Step 4: Compare with Yahoo Finance (simple)
            print("\nStep 4: Simple Yahoo Finance Comparison...")
            yahoo_comparison = await self._simple_yahoo_comparison()
            
            # Step 5: Generate findings
            print("\nStep 5: Generating Findings...")
            findings = await self._generate_findings(db_overview, sample_quality, symbol_analysis, yahoo_comparison)
            
            print("\n" + "=" * 60)
            print("SIMPLE DATA QUALITY CHECK COMPLETED!")
            print("=" * 60)
            
            return {
                'database_overview': db_overview,
                'sample_quality': sample_quality,
                'symbol_analysis': symbol_analysis,
                'yahoo_comparison': yahoo_comparison,
                'findings': findings
            }
            
        except Exception as e:
            logger.error(f"Error in simple data check: {e}")
            return {'error': str(e)}
    
    async def _check_database_overview(self) -> Dict[str, Any]:
        """Check database overview"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Get basic statistics
            cursor.execute("SELECT COUNT(*) FROM market_data")
            total_records = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT symbol) FROM market_data")
            unique_symbols = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(date), MAX(date) FROM market_data")
            date_range = cursor.fetchone()
            
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE close IS NULL")
            null_closes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE volume IS NULL")
            null_volumes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE close <= 0")
            invalid_closes = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM market_data WHERE volume < 0")
            invalid_volumes = cursor.fetchone()[0]
            
            cursor.close()
            connection.close()
            
            return {
                'total_records': total_records,
                'unique_symbols': unique_symbols,
                'date_range': {
                    'start': date_range[0],
                    'end': date_range[1]
                },
                'data_quality_issues': {
                    'null_closes': null_closes,
                    'null_volumes': null_volumes,
                    'invalid_closes': invalid_closes,
                    'invalid_volumes': invalid_volumes
                },
                'completeness_rate': (total_records - null_closes) / total_records if total_records > 0 else 0
            }
            
        except Error as e:
            logger.error(f"Error checking database overview: {e}")
            return {'error': str(e)}
    
    async def _check_sample_data_quality(self) -> Dict[str, Any]:
        """Check sample data quality"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Get sample data
            cursor.execute("""
            SELECT symbol, date, open, high, low, close, volume
            FROM market_data 
            ORDER BY date DESC 
            LIMIT 100
            """)
            
            sample_data = cursor.fetchall()
            
            quality_issues = []
            
            for row in sample_data:
                symbol, date, open_price, high, low, close, volume = row
                
                # Check for data quality issues
                issues = []
                
                if close is None or close <= 0:
                    issues.append("Invalid close price")
                
                if open_price is None or open_price <= 0:
                    issues.append("Invalid open price")
                
                if high is None or high <= 0:
                    issues.append("Invalid high price")
                
                if low is None or low <= 0:
                    issues.append("Invalid low price")
                
                if volume is None or volume < 0:
                    issues.append("Invalid volume")
                
                if high < low:
                    issues.append("High < Low")
                
                if high < close or low > close:
                    issues.append("Close outside high/low range")
                
                if issues:
                    quality_issues.append({
                        'symbol': symbol,
                        'date': date,
                        'issues': issues
                    })
            
            cursor.close()
            connection.close()
            
            return {
                'sample_size': len(sample_data),
                'quality_issues_found': len(quality_issues),
                'quality_issues': quality_issues[:10],  # Show first 10 issues
                'quality_rate': (len(sample_data) - len(quality_issues)) / len(sample_data) if sample_data else 0
            }
            
        except Error as e:
            logger.error(f"Error checking sample data quality: {e}")
            return {'error': str(e)}
    
    async def _analyze_specific_symbols(self) -> Dict[str, Any]:
        """Analyze specific symbols"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Get symbols with most data
            cursor.execute("""
            SELECT symbol, COUNT(*) as record_count,
                   MIN(date) as first_date, MAX(date) as last_date,
                   AVG(close) as avg_price, STD(close) as price_std
            FROM market_data 
            GROUP BY symbol 
            ORDER BY record_count DESC 
            LIMIT 10
            """)
            
            symbol_stats = cursor.fetchall()
            
            analysis = {}
            
            for row in symbol_stats:
                symbol, count, first_date, last_date, avg_price, price_std = row
                
                # Get price range
                cursor.execute("""
                SELECT MIN(close), MAX(close) FROM market_data WHERE symbol = %s
                """, (symbol,))
                price_range = cursor.fetchone()
                
                # Get extreme price changes
                cursor.execute("""
                SELECT close, date FROM market_data 
                WHERE symbol = %s AND close IS NOT NULL 
                ORDER BY date
                """, (symbol,))
                
                prices = cursor.fetchall()
                extreme_changes = 0
                
                if len(prices) > 1:
                    for i in range(1, len(prices)):
                        prev_price = prices[i-1][0]
                        curr_price = prices[i][0]
                        if prev_price > 0:
                            change = abs(curr_price - prev_price) / prev_price
                            if change > 0.2:  # >20% change
                                extreme_changes += 1
                
                analysis[symbol] = {
                    'record_count': count,
                    'date_range': f"{first_date} to {last_date}",
                    'avg_price': float(avg_price) if avg_price else 0,
                    'price_std': float(price_std) if price_std else 0,
                    'price_range': f"{price_range[0]} to {price_range[1]}" if price_range else "N/A",
                    'extreme_changes': extreme_changes,
                    'data_quality_score': max(0, 1 - (extreme_changes / count)) if count > 0 else 0
                }
            
            cursor.close()
            connection.close()
            
            return analysis
            
        except Error as e:
            logger.error(f"Error analyzing specific symbols: {e}")
            return {'error': str(e)}
    
    async def _simple_yahoo_comparison(self) -> Dict[str, Any]:
        """Simple Yahoo Finance comparison"""
        try:
            # Test with a few symbols
            test_symbols = ['WIKA.JK', 'AALI.JK', 'ADRO.JK']
            comparison_results = {}
            
            for symbol in test_symbols:
                print(f"  Comparing {symbol}...")
                
                try:
                    # Get database data
                    db_data = await self._get_db_data_for_symbol(symbol)
                    
                    # Get Yahoo Finance data
                    yahoo_data = await self._get_yahoo_data_for_symbol(symbol)
                    
                    if db_data and yahoo_data:
                        # Simple comparison
                        comparison = self._simple_compare_data(db_data, yahoo_data, symbol)
                        comparison_results[symbol] = comparison
                        print(f"    {symbol}: {comparison['quality_score']:.2f} quality score")
                    else:
                        comparison_results[symbol] = {'error': 'No data available'}
                        print(f"    {symbol}: No data available")
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"    {symbol}: Error - {e}")
                    comparison_results[symbol] = {'error': str(e)}
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error in simple Yahoo comparison: {e}")
            return {'error': str(e)}
    
    async def _get_db_data_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Get database data for symbol"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            cursor.execute("""
            SELECT date, close FROM market_data 
            WHERE symbol = %s 
            ORDER BY date DESC 
            LIMIT 10
            """, (symbol,))
            
            data = cursor.fetchall()
            
            cursor.close()
            connection.close()
            
            if data:
                return {
                    'symbol': symbol,
                    'records': len(data),
                    'latest_date': data[0][0],
                    'latest_price': float(data[0][1]),
                    'price_range': f"{min(row[1] for row in data)} to {max(row[1] for row in data)}"
                }
            else:
                return None
                
        except Error as e:
            logger.error(f"Error getting DB data for {symbol}: {e}")
            return None
    
    async def _get_yahoo_data_for_symbol(self, symbol: str) -> Dict[str, Any]:
        """Get Yahoo Finance data for symbol"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")  # 1 month of data
            
            if not hist.empty:
                latest_price = hist['Close'].iloc[-1]
                price_range = f"{hist['Close'].min():.2f} to {hist['Close'].max():.2f}"
                
                return {
                    'symbol': symbol,
                    'records': len(hist),
                    'latest_date': hist.index[-1].strftime('%Y-%m-%d'),
                    'latest_price': float(latest_price),
                    'price_range': price_range
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting Yahoo data for {symbol}: {e}")
            return None
    
    def _simple_compare_data(self, db_data: Dict[str, Any], yahoo_data: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Simple data comparison"""
        try:
            if not db_data or not yahoo_data:
                return {'quality_score': 0, 'error': 'Missing data'}
            
            # Compare latest prices
            db_price = db_data['latest_price']
            yahoo_price = yahoo_data['latest_price']
            
            price_diff = abs(db_price - yahoo_price) / yahoo_price if yahoo_price > 0 else 1
            
            # Calculate quality score
            if price_diff < 0.01:  # <1% difference
                quality_score = 1.0
            elif price_diff < 0.05:  # <5% difference
                quality_score = 0.8
            elif price_diff < 0.1:  # <10% difference
                quality_score = 0.6
            else:
                quality_score = 0.2
            
            return {
                'symbol': symbol,
                'db_price': db_price,
                'yahoo_price': yahoo_price,
                'price_difference': price_diff,
                'quality_score': quality_score,
                'quality_assessment': 'EXCELLENT' if quality_score >= 0.9 else 'GOOD' if quality_score >= 0.7 else 'FAIR' if quality_score >= 0.5 else 'POOR'
            }
            
        except Exception as e:
            logger.error(f"Error comparing data for {symbol}: {e}")
            return {'quality_score': 0, 'error': str(e)}
    
    async def _generate_findings(self, db_overview: Dict[str, Any], sample_quality: Dict[str, Any], symbol_analysis: Dict[str, Any], yahoo_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Generate findings from all checks"""
        try:
            findings = {
                'database_issues': [],
                'data_quality_issues': [],
                'symbol_specific_issues': [],
                'yahoo_comparison_issues': [],
                'overall_assessment': {},
                'recommendations': []
            }
            
            # Database issues
            if db_overview.get('data_quality_issues', {}).get('null_closes', 0) > 0:
                findings['database_issues'].append(f"Found {db_overview['data_quality_issues']['null_closes']} null close prices")
            
            if db_overview.get('data_quality_issues', {}).get('invalid_closes', 0) > 0:
                findings['database_issues'].append(f"Found {db_overview['data_quality_issues']['invalid_closes']} invalid close prices")
            
            # Data quality issues
            if sample_quality.get('quality_issues_found', 0) > 0:
                findings['data_quality_issues'].append(f"Found {sample_quality['quality_issues_found']} quality issues in sample data")
            
            # Symbol specific issues
            for symbol, analysis in symbol_analysis.items():
                if analysis.get('extreme_changes', 0) > 10:
                    findings['symbol_specific_issues'].append(f"{symbol}: {analysis['extreme_changes']} extreme price changes")
            
            # Yahoo comparison issues
            for symbol, comparison in yahoo_comparison.items():
                if isinstance(comparison, dict) and 'quality_score' in comparison:
                    if comparison['quality_score'] < 0.5:
                        findings['yahoo_comparison_issues'].append(f"{symbol}: Poor data quality vs Yahoo Finance")
            
            # Overall assessment
            total_issues = (len(findings['database_issues']) + 
                          len(findings['data_quality_issues']) + 
                          len(findings['symbol_specific_issues']) + 
                          len(findings['yahoo_comparison_issues']))
            
            if total_issues == 0:
                findings['overall_assessment'] = {
                    'status': 'GOOD',
                    'message': 'No significant data quality issues found'
                }
            elif total_issues <= 3:
                findings['overall_assessment'] = {
                    'status': 'FAIR',
                    'message': 'Some data quality issues found'
                }
            else:
                findings['overall_assessment'] = {
                    'status': 'POOR',
                    'message': 'Multiple data quality issues found'
                }
            
            # Generate recommendations
            if findings['database_issues']:
                findings['recommendations'].append("Fix null and invalid price data")
            
            if findings['data_quality_issues']:
                findings['recommendations'].append("Implement data validation")
            
            if findings['symbol_specific_issues']:
                findings['recommendations'].append("Filter extreme price changes")
            
            if findings['yahoo_comparison_issues']:
                findings['recommendations'].append("Verify data sources against Yahoo Finance")
            
            if not findings['recommendations']:
                findings['recommendations'].append("Maintain current data quality standards")
            
            return findings
            
        except Exception as e:
            logger.error(f"Error generating findings: {e}")
            return {'error': str(e)}

async def main():
    """Main function untuk menjalankan simple data quality check"""
    try:
        quality_checker = SimpleDataQualityCheck()
        
        # Run simple data quality check
        results = await quality_checker.run_simple_data_check()
        
        if 'error' in results:
            print(f"\nError: {results['error']}")
            return results
        
        # Display results
        print("\nSIMPLE DATA QUALITY CHECK RESULTS:")
        print("=" * 60)
        
        # Database Overview
        print("\nDATABASE OVERVIEW:")
        db_overview = results['database_overview']
        print(f"  Total Records: {db_overview.get('total_records', 0):,}")
        print(f"  Unique Symbols: {db_overview.get('unique_symbols', 0)}")
        print(f"  Date Range: {db_overview.get('date_range', {}).get('start')} to {db_overview.get('date_range', {}).get('end')}")
        print(f"  Completeness Rate: {db_overview.get('completeness_rate', 0):.2%}")
        
        # Data Quality Issues
        print("\nDATA QUALITY ISSUES:")
        issues = db_overview.get('data_quality_issues', {})
        print(f"  Null Closes: {issues.get('null_closes', 0)}")
        print(f"  Null Volumes: {issues.get('null_volumes', 0)}")
        print(f"  Invalid Closes: {issues.get('invalid_closes', 0)}")
        print(f"  Invalid Volumes: {issues.get('invalid_volumes', 0)}")
        
        # Sample Quality
        print("\nSAMPLE DATA QUALITY:")
        sample_quality = results['sample_quality']
        print(f"  Sample Size: {sample_quality.get('sample_size', 0)}")
        print(f"  Quality Issues Found: {sample_quality.get('quality_issues_found', 0)}")
        print(f"  Quality Rate: {sample_quality.get('quality_rate', 0):.2%}")
        
        # Symbol Analysis
        print("\nSYMBOL ANALYSIS:")
        symbol_analysis = results['symbol_analysis']
        for symbol, analysis in list(symbol_analysis.items())[:5]:  # Show first 5
            print(f"  {symbol}: {analysis.get('record_count', 0)} records, {analysis.get('extreme_changes', 0)} extreme changes, Quality: {analysis.get('data_quality_score', 0):.2f}")
        
        # Yahoo Comparison
        print("\nYAHOO FINANCE COMPARISON:")
        yahoo_comparison = results['yahoo_comparison']
        for symbol, comparison in yahoo_comparison.items():
            if isinstance(comparison, dict) and 'quality_score' in comparison:
                print(f"  {symbol}: {comparison['quality_score']:.2f} ({comparison.get('quality_assessment', 'UNKNOWN')})")
        
        # Findings
        print("\nFINDINGS:")
        findings = results['findings']
        print(f"  Database Issues: {len(findings.get('database_issues', []))}")
        print(f"  Data Quality Issues: {len(findings.get('data_quality_issues', []))}")
        print(f"  Symbol Issues: {len(findings.get('symbol_specific_issues', []))}")
        print(f"  Yahoo Comparison Issues: {len(findings.get('yahoo_comparison_issues', []))}")
        
        print(f"\n  Overall Assessment: {findings.get('overall_assessment', {}).get('status', 'UNKNOWN')}")
        print(f"  Message: {findings.get('overall_assessment', {}).get('message', 'No message')}")
        
        print("\nRECOMMENDATIONS:")
        for recommendation in findings.get('recommendations', []):
            print(f"  - {recommendation}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    asyncio.run(main())
