"""
DATA QUALITY ANALYSIS
====================

Analisis kualitas data database dan perbandingan dengan Yahoo Finance
untuk mengidentifikasi masalah data yang menyebabkan kerugian.

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
import requests
from urllib.parse import quote

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataQualityAnalysis:
    """
    Data Quality Analysis - Periksa kualitas data database vs Yahoo Finance
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
        
        # Yahoo Finance configuration
        self.yahoo_base_url = "https://query1.finance.yahoo.com/v8/finance/chart/"
        self.rate_limit_delay = 1  # 1 second delay between requests
        
    async def run_data_quality_analysis(self) -> Dict[str, Any]:
        """Run comprehensive data quality analysis"""
        try:
            print("DATA QUALITY ANALYSIS")
            print("=" * 60)
            print("OBJECTIVE: Identify data quality issues causing trading losses")
            print("=" * 60)
            
            # Step 1: Analyze database data quality
            print("\nStep 1: Analyzing Database Data Quality...")
            db_analysis = await self._analyze_database_data_quality()
            
            # Step 2: Get sample symbols for comparison
            print("\nStep 2: Getting Sample Symbols...")
            sample_symbols = await self._get_sample_symbols()
            
            # Step 3: Compare with Yahoo Finance
            print("\nStep 3: Comparing with Yahoo Finance...")
            yahoo_comparison = await self._compare_with_yahoo_finance(sample_symbols)
            
            # Step 4: Identify data quality issues
            print("\nStep 4: Identifying Data Quality Issues...")
            quality_issues = await self._identify_data_quality_issues(db_analysis, yahoo_comparison)
            
            # Step 5: Generate recommendations
            print("\nStep 5: Generating Data Quality Recommendations...")
            recommendations = await self._generate_data_quality_recommendations(quality_issues)
            
            # Compile comprehensive results
            comprehensive_results = {
                'database_analysis': db_analysis,
                'yahoo_comparison': yahoo_comparison,
                'quality_issues': quality_issues,
                'recommendations': recommendations,
                'summary': self._generate_quality_summary(db_analysis, yahoo_comparison, quality_issues)
            }
            
            print("\n" + "=" * 60)
            print("DATA QUALITY ANALYSIS COMPLETED!")
            print("=" * 60)
            
            return comprehensive_results
            
        except Exception as e:
            logger.error(f"Error in data quality analysis: {e}")
            return {'error': str(e)}
    
    async def _analyze_database_data_quality(self) -> Dict[str, Any]:
        """Analyze database data quality"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Get database overview
            cursor.execute("SELECT COUNT(*) FROM market_data")
            total_records = cursor.fetchone()[0]
            
            # Get unique symbols
            cursor.execute("SELECT DISTINCT symbol FROM market_data")
            unique_symbols = [row[0] for row in cursor.fetchall()]
            
            # Get date range
            cursor.execute("SELECT MIN(date), MAX(date) FROM market_data")
            date_range = cursor.fetchone()
            
            # Analyze data completeness
            completeness_analysis = {}
            for symbol in unique_symbols[:10]:  # Analyze first 10 symbols
                cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN close IS NOT NULL THEN 1 END) as non_null_close,
                    COUNT(CASE WHEN volume IS NOT NULL THEN 1 END) as non_null_volume,
                    MIN(date) as min_date,
                    MAX(date) as max_date,
                    AVG(close) as avg_price,
                    STD(close) as price_volatility
                FROM market_data 
                WHERE symbol = %s
                """, (symbol,))
                
                result = cursor.fetchone()
                if result:
                    completeness_analysis[symbol] = {
                        'total_records': result[0],
                        'non_null_close': result[1],
                        'non_null_volume': result[2],
                        'min_date': result[3],
                        'max_date': result[4],
                        'avg_price': float(result[5]) if result[5] else 0,
                        'price_volatility': float(result[6]) if result[6] else 0,
                        'completeness_rate': result[1] / result[0] if result[0] > 0 else 0
                    }
            
            # Analyze price anomalies
            price_anomalies = {}
            for symbol in unique_symbols[:10]:
                cursor.execute("""
                SELECT close, date
                FROM market_data 
                WHERE symbol = %s AND close IS NOT NULL
                ORDER BY date
                """, (symbol,))
                
                prices = cursor.fetchall()
                if len(prices) > 1:
                    price_changes = []
                    for i in range(1, len(prices)):
                        prev_price = prices[i-1][0]
                        curr_price = prices[i][0]
                        if prev_price > 0:
                            change = (curr_price - prev_price) / prev_price
                            price_changes.append(change)
                    
                    if price_changes:
                        price_anomalies[symbol] = {
                            'max_daily_change': max(price_changes),
                            'min_daily_change': min(price_changes),
                            'avg_daily_change': np.mean(price_changes),
                            'extreme_changes': sum(1 for change in price_changes if abs(change) > 0.2)  # >20% change
                        }
            
            cursor.close()
            connection.close()
            
            return {
                'total_records': total_records,
                'unique_symbols': len(unique_symbols),
                'date_range': {
                    'start': date_range[0],
                    'end': date_range[1]
                },
                'completeness_analysis': completeness_analysis,
                'price_anomalies': price_anomalies,
                'data_quality_score': self._calculate_data_quality_score(completeness_analysis, price_anomalies)
            }
            
        except Error as e:
            logger.error(f"Error analyzing database data quality: {e}")
            return {'error': str(e)}
    
    async def _get_sample_symbols(self) -> List[str]:
        """Get sample symbols for comparison"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            # Get symbols with most data
            cursor.execute("""
            SELECT symbol, COUNT(*) as record_count
            FROM market_data 
            GROUP BY symbol 
            ORDER BY record_count DESC 
            LIMIT 5
            """)
            
            results = cursor.fetchall()
            sample_symbols = [row[0] for row in results]
            
            cursor.close()
            connection.close()
            
            return sample_symbols
            
        except Error as e:
            logger.error(f"Error getting sample symbols: {e}")
            return []
    
    async def _compare_with_yahoo_finance(self, sample_symbols: List[str]) -> Dict[str, Any]:
        """Compare database data with Yahoo Finance"""
        try:
            comparison_results = {}
            
            for symbol in sample_symbols:
                print(f"Comparing {symbol} with Yahoo Finance...")
                
                try:
                    # Get database data
                    db_data = await self._get_database_data(symbol)
                    
                    # Get Yahoo Finance data
                    yahoo_data = await self._get_yahoo_finance_data(symbol)
                    
                    if db_data and yahoo_data:
                        # Compare data
                        comparison = self._compare_data_sets(db_data, yahoo_data, symbol)
                        comparison_results[symbol] = comparison
                        
                        print(f"  {symbol}: {comparison['data_quality_score']:.2f} quality score")
                    
                    # Rate limiting
                    time.sleep(self.rate_limit_delay)
                    
                except Exception as e:
                    print(f"  Error comparing {symbol}: {e}")
                    comparison_results[symbol] = {'error': str(e)}
            
            return comparison_results
            
        except Exception as e:
            logger.error(f"Error comparing with Yahoo Finance: {e}")
            return {'error': str(e)}
    
    async def _get_database_data(self, symbol: str) -> pd.DataFrame:
        """Get data from database"""
        try:
            connection = mysql.connector.connect(**self.db_config)
            cursor = connection.cursor()
            
            query = """
            SELECT date, open, high, low, close, volume
            FROM market_data 
            WHERE symbol = %s 
            ORDER BY date
            """
            
            cursor.execute(query, (symbol,))
            data = cursor.fetchall()
            
            if data:
                df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                df['date'] = pd.to_datetime(df['date'])
                df['open'] = df['open'].astype(float)
                df['high'] = df['high'].astype(float)
                df['low'] = df['low'].astype(float)
                df['close'] = df['close'].astype(float)
                df['volume'] = df['volume'].astype(float)
                
                cursor.close()
                connection.close()
                
                return df
            
            cursor.close()
            connection.close()
            return None
            
        except Error as e:
            logger.error(f"Error getting database data for {symbol}: {e}")
            return None
    
    async def _get_yahoo_finance_data(self, symbol: str) -> pd.DataFrame:
        """Get data from Yahoo Finance"""
        try:
            # Convert symbol format (e.g., ELTY.JK -> ELTY.JK)
            yahoo_symbol = symbol
            
            # Get data from Yahoo Finance
            ticker = yf.Ticker(yahoo_symbol)
            hist = ticker.history(period="2y")  # 2 years of data
            
            if not hist.empty:
                # Reset index to get date as column
                hist = hist.reset_index()
                hist['date'] = hist['Date']
                hist = hist[['date', 'Open', 'High', 'Low', 'Close', 'Volume']]
                hist.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
                
                return hist
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting Yahoo Finance data for {symbol}: {e}")
            return None
    
    def _compare_data_sets(self, db_data: pd.DataFrame, yahoo_data: pd.DataFrame, symbol: str) -> Dict[str, Any]:
        """Compare database data with Yahoo Finance data"""
        try:
            # Find common date range
            db_start = db_data['date'].min()
            db_end = db_data['date'].max()
            yahoo_start = yahoo_data['date'].min()
            yahoo_end = yahoo_data['date'].max()
            
            common_start = max(db_start, yahoo_start)
            common_end = min(db_end, yahoo_end)
            
            # Filter data to common range
            db_filtered = db_data[(db_data['date'] >= common_start) & (db_data['date'] <= common_end)]
            yahoo_filtered = yahoo_data[(yahoo_data['date'] >= common_start) & (yahoo_data['date'] <= common_end)]
            
            if len(db_filtered) == 0 or len(yahoo_filtered) == 0:
                return {
                    'symbol': symbol,
                    'error': 'No common date range found',
                    'data_quality_score': 0
                }
            
            # Compare prices
            price_comparison = self._compare_prices(db_filtered, yahoo_filtered)
            
            # Compare volumes
            volume_comparison = self._compare_volumes(db_filtered, yahoo_filtered)
            
            # Calculate overall quality score
            quality_score = self._calculate_comparison_quality_score(price_comparison, volume_comparison)
            
            return {
                'symbol': symbol,
                'date_range': {
                    'common_start': common_start,
                    'common_end': common_end,
                    'db_records': len(db_filtered),
                    'yahoo_records': len(yahoo_filtered)
                },
                'price_comparison': price_comparison,
                'volume_comparison': volume_comparison,
                'data_quality_score': quality_score,
                'quality_assessment': self._assess_data_quality(quality_score)
            }
            
        except Exception as e:
            logger.error(f"Error comparing data sets for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'data_quality_score': 0
            }
    
    def _compare_prices(self, db_data: pd.DataFrame, yahoo_data: pd.DataFrame) -> Dict[str, Any]:
        """Compare price data between database and Yahoo Finance"""
        try:
            # Merge data on date
            merged = pd.merge(db_data, yahoo_data, on='date', suffixes=('_db', '_yahoo'))
            
            if len(merged) == 0:
                return {'error': 'No matching dates found'}
            
            # Calculate price differences
            close_diff = abs(merged['close_db'] - merged['close_yahoo']) / merged['close_yahoo']
            open_diff = abs(merged['open_db'] - merged['open_yahoo']) / merged['open_yahoo']
            high_diff = abs(merged['high_db'] - merged['high_yahoo']) / merged['high_yahoo']
            low_diff = abs(merged['low_db'] - merged['low_yahoo']) / merged['low_yahoo']
            
            return {
                'close_difference_avg': close_diff.mean(),
                'close_difference_max': close_diff.max(),
                'open_difference_avg': open_diff.mean(),
                'open_difference_max': open_diff.max(),
                'high_difference_avg': high_diff.mean(),
                'high_difference_max': high_diff.max(),
                'low_difference_avg': low_diff.mean(),
                'low_difference_max': low_diff.max(),
                'significant_differences': sum(close_diff > 0.05),  # >5% difference
                'total_comparisons': len(merged)
            }
            
        except Exception as e:
            logger.error(f"Error comparing prices: {e}")
            return {'error': str(e)}
    
    def _compare_volumes(self, db_data: pd.DataFrame, yahoo_data: pd.DataFrame) -> Dict[str, Any]:
        """Compare volume data between database and Yahoo Finance"""
        try:
            # Merge data on date
            merged = pd.merge(db_data, yahoo_data, on='date', suffixes=('_db', '_yahoo'))
            
            if len(merged) == 0:
                return {'error': 'No matching dates found'}
            
            # Calculate volume differences
            volume_diff = abs(merged['volume_db'] - merged['volume_yahoo']) / merged['volume_yahoo']
            
            return {
                'volume_difference_avg': volume_diff.mean(),
                'volume_difference_max': volume_diff.max(),
                'significant_differences': sum(volume_diff > 0.1),  # >10% difference
                'total_comparisons': len(merged)
            }
            
        except Exception as e:
            logger.error(f"Error comparing volumes: {e}")
            return {'error': str(e)}
    
    def _calculate_comparison_quality_score(self, price_comparison: Dict[str, Any], volume_comparison: Dict[str, Any]) -> float:
        """Calculate overall quality score"""
        try:
            if 'error' in price_comparison or 'error' in volume_comparison:
                return 0.0
            
            # Price quality (70% weight)
            price_score = 1.0
            if 'close_difference_avg' in price_comparison:
                close_diff = price_comparison['close_difference_avg']
                if close_diff > 0.1:  # >10% difference
                    price_score = 0.0
                elif close_diff > 0.05:  # >5% difference
                    price_score = 0.5
                else:
                    price_score = 1.0
            
            # Volume quality (30% weight)
            volume_score = 1.0
            if 'volume_difference_avg' in volume_comparison:
                volume_diff = volume_comparison['volume_difference_avg']
                if volume_diff > 0.5:  # >50% difference
                    volume_score = 0.0
                elif volume_diff > 0.2:  # >20% difference
                    volume_score = 0.5
                else:
                    volume_score = 1.0
            
            overall_score = (price_score * 0.7) + (volume_score * 0.3)
            return overall_score
            
        except Exception as e:
            logger.error(f"Error calculating quality score: {e}")
            return 0.0
    
    def _assess_data_quality(self, quality_score: float) -> str:
        """Assess data quality based on score"""
        if quality_score >= 0.9:
            return "EXCELLENT"
        elif quality_score >= 0.7:
            return "GOOD"
        elif quality_score >= 0.5:
            return "FAIR"
        elif quality_score >= 0.3:
            return "POOR"
        else:
            return "VERY POOR"
    
    def _calculate_data_quality_score(self, completeness_analysis: Dict[str, Any], price_anomalies: Dict[str, Any]) -> float:
        """Calculate overall database data quality score"""
        try:
            if not completeness_analysis:
                return 0.0
            
            # Calculate completeness score
            completeness_scores = [data['completeness_rate'] for data in completeness_analysis.values()]
            avg_completeness = np.mean(completeness_scores) if completeness_scores else 0
            
            # Calculate anomaly score
            anomaly_scores = []
            for symbol, data in price_anomalies.items():
                if data['extreme_changes'] > 0:
                    anomaly_score = max(0, 1 - (data['extreme_changes'] / data['total_comparisons']))
                else:
                    anomaly_score = 1.0
                anomaly_scores.append(anomaly_score)
            
            avg_anomaly_score = np.mean(anomaly_scores) if anomaly_scores else 1.0
            
            # Overall quality score
            overall_score = (avg_completeness * 0.6) + (avg_anomaly_score * 0.4)
            return overall_score
            
        except Exception as e:
            logger.error(f"Error calculating data quality score: {e}")
            return 0.0
    
    async def _identify_data_quality_issues(self, db_analysis: Dict[str, Any], yahoo_comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Identify specific data quality issues"""
        try:
            issues = {
                'completeness_issues': [],
                'accuracy_issues': [],
                'consistency_issues': [],
                'timeliness_issues': [],
                'overall_issues': []
            }
            
            # Analyze completeness issues
            if 'completeness_analysis' in db_analysis:
                for symbol, data in db_analysis['completeness_analysis'].items():
                    if data['completeness_rate'] < 0.9:
                        issues['completeness_issues'].append({
                            'symbol': symbol,
                            'completeness_rate': data['completeness_rate'],
                            'issue': 'Missing data points'
                        })
            
            # Analyze accuracy issues
            if yahoo_comparison:
                for symbol, comparison in yahoo_comparison.items():
                    if isinstance(comparison, dict) and 'price_comparison' in comparison:
                        price_comp = comparison['price_comparison']
                        if 'close_difference_avg' in price_comp and price_comp['close_difference_avg'] > 0.05:
                            issues['accuracy_issues'].append({
                                'symbol': symbol,
                                'price_difference': price_comp['close_difference_avg'],
                                'issue': 'Price data differs significantly from Yahoo Finance'
                            })
            
            # Analyze consistency issues
            if 'price_anomalies' in db_analysis:
                for symbol, data in db_analysis['price_anomalies'].items():
                    if data['extreme_changes'] > 5:
                        issues['consistency_issues'].append({
                            'symbol': symbol,
                            'extreme_changes': data['extreme_changes'],
                            'issue': 'Too many extreme price changes'
                        })
            
            # Overall assessment
            total_issues = (len(issues['completeness_issues']) + 
                          len(issues['accuracy_issues']) + 
                          len(issues['consistency_issues']))
            
            if total_issues > 10:
                issues['overall_issues'].append('CRITICAL: Multiple data quality issues detected')
            elif total_issues > 5:
                issues['overall_issues'].append('WARNING: Several data quality issues detected')
            elif total_issues > 0:
                issues['overall_issues'].append('NOTICE: Some data quality issues detected')
            else:
                issues['overall_issues'].append('GOOD: No significant data quality issues')
            
            return issues
            
        except Exception as e:
            logger.error(f"Error identifying data quality issues: {e}")
            return {'error': str(e)}
    
    async def _generate_data_quality_recommendations(self, quality_issues: Dict[str, Any]) -> List[str]:
        """Generate recommendations for improving data quality"""
        try:
            recommendations = []
            
            if quality_issues.get('completeness_issues'):
                recommendations.append("IMPLEMENT data validation to ensure complete data capture")
                recommendations.append("SET UP automated data quality monitoring")
            
            if quality_issues.get('accuracy_issues'):
                recommendations.append("VERIFY data sources and implement cross-validation with Yahoo Finance")
                recommendations.append("IMPLEMENT data correction algorithms for price discrepancies")
            
            if quality_issues.get('consistency_issues'):
                recommendations.append("IMPLEMENT outlier detection and filtering")
                recommendations.append("SET UP data smoothing algorithms for extreme price changes")
            
            if not recommendations:
                recommendations.append("MAINTAIN current data quality standards")
                recommendations.append("CONTINUE monitoring data quality")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ['Error generating recommendations']
    
    def _generate_quality_summary(self, db_analysis: Dict[str, Any], yahoo_comparison: Dict[str, Any], quality_issues: Dict[str, Any]) -> Dict[str, Any]:
        """Generate overall quality summary"""
        try:
            # Calculate overall quality metrics
            db_quality_score = db_analysis.get('data_quality_score', 0)
            
            yahoo_scores = []
            if yahoo_comparison:
                for symbol, comparison in yahoo_comparison.items():
                    if isinstance(comparison, dict) and 'data_quality_score' in comparison:
                        yahoo_scores.append(comparison['data_quality_score'])
            
            avg_yahoo_score = np.mean(yahoo_scores) if yahoo_scores else 0
            
            # Count issues
            total_issues = (len(quality_issues.get('completeness_issues', [])) +
                          len(quality_issues.get('accuracy_issues', [])) +
                          len(quality_issues.get('consistency_issues', [])))
            
            # Overall assessment
            if db_quality_score >= 0.8 and avg_yahoo_score >= 0.8 and total_issues == 0:
                overall_status = "EXCELLENT"
            elif db_quality_score >= 0.6 and avg_yahoo_score >= 0.6 and total_issues <= 2:
                overall_status = "GOOD"
            elif db_quality_score >= 0.4 and avg_yahoo_score >= 0.4 and total_issues <= 5:
                overall_status = "FAIR"
            else:
                overall_status = "POOR"
            
            return {
                'database_quality_score': db_quality_score,
                'yahoo_comparison_score': avg_yahoo_score,
                'total_issues': total_issues,
                'overall_status': overall_status,
                'data_quality_impact': 'HIGH' if total_issues > 5 else 'MODERATE' if total_issues > 2 else 'LOW'
            }
            
        except Exception as e:
            logger.error(f"Error generating quality summary: {e}")
            return {'error': str(e)}

async def main():
    """Main function untuk menjalankan data quality analysis"""
    try:
        quality_analyzer = DataQualityAnalysis()
        
        # Run data quality analysis
        results = await quality_analyzer.run_data_quality_analysis()
        
        if 'error' in results:
            print(f"\nError: {results['error']}")
            return results
        
        # Display results
        print("\nDATA QUALITY ANALYSIS RESULTS:")
        print("=" * 60)
        
        # Database Analysis
        print("\nDATABASE DATA QUALITY:")
        db_analysis = results['database_analysis']
        print(f"  Total Records: {db_analysis.get('total_records', 0):,}")
        print(f"  Unique Symbols: {db_analysis.get('unique_symbols', 0)}")
        print(f"  Date Range: {db_analysis.get('date_range', {}).get('start')} to {db_analysis.get('date_range', {}).get('end')}")
        print(f"  Data Quality Score: {db_analysis.get('data_quality_score', 0):.2f}")
        
        # Yahoo Finance Comparison
        print("\nYAHOO FINANCE COMPARISON:")
        yahoo_comparison = results['yahoo_comparison']
        for symbol, comparison in yahoo_comparison.items():
            if isinstance(comparison, dict) and 'data_quality_score' in comparison:
                print(f"  {symbol}: {comparison['data_quality_score']:.2f} ({comparison.get('quality_assessment', 'UNKNOWN')})")
        
        # Quality Issues
        print("\nDATA QUALITY ISSUES:")
        quality_issues = results['quality_issues']
        print(f"  Completeness Issues: {len(quality_issues.get('completeness_issues', []))}")
        print(f"  Accuracy Issues: {len(quality_issues.get('accuracy_issues', []))}")
        print(f"  Consistency Issues: {len(quality_issues.get('consistency_issues', []))}")
        
        for issue_type, issues in quality_issues.items():
            if issues and issue_type != 'overall_issues':
                print(f"\n  {issue_type.upper()}:")
                for issue in issues[:3]:  # Show first 3 issues
                    print(f"    - {issue}")
        
        # Recommendations
        print("\nRECOMMENDATIONS:")
        for recommendation in results['recommendations']:
            print(f"  - {recommendation}")
        
        # Summary
        print("\nOVERALL SUMMARY:")
        summary = results['summary']
        print(f"  Database Quality Score: {summary.get('database_quality_score', 0):.2f}")
        print(f"  Yahoo Comparison Score: {summary.get('yahoo_comparison_score', 0):.2f}")
        print(f"  Total Issues: {summary.get('total_issues', 0)}")
        print(f"  Overall Status: {summary.get('overall_status', 'UNKNOWN')}")
        print(f"  Data Quality Impact: {summary.get('data_quality_impact', 'UNKNOWN')}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    asyncio.run(main())
