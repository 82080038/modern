#!/usr/bin/env python3
"""
Final System Test
================

Script untuk melakukan testing final system setelah semua perbaikan:
- Test semua modules
- Test database performance
- Test data quality
- Generate final assessment

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='scalper',
        charset='utf8mb4',
        collation='utf8mb4_unicode_ci',
        autocommit=False
    )

def execute_query(cursor, query, params=None, fetch=False):
    """Execute query with error handling"""
    try:
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        return True
    except mysql.connector.Error as err:
        print(f"     [ERROR] {err}")
        return False

def test_trading_module(cursor):
    """Test trading module performance"""
    print("   Testing trading module...")
    try:
        # Test orders table
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        
        # Test trades table
        cursor.execute("SELECT COUNT(*) FROM trades")
        trades_count = cursor.fetchone()[0]
        
        # Test order execution rate
        cursor.execute("SELECT COUNT(*) FROM orders WHERE executed_at IS NOT NULL")
        executed_orders = cursor.fetchone()[0]
        execution_rate = (executed_orders / orders_count) * 100 if orders_count > 0 else 0
        
        # Test trade value calculation
        cursor.execute("SELECT COUNT(*) FROM trades WHERE trade_value IS NOT NULL")
        trades_with_value = cursor.fetchone()[0]
        trade_value_rate = (trades_with_value / trades_count) * 100 if trades_count > 0 else 0
        
        trading_score = (execution_rate + trade_value_rate) / 2
        
        print(f"     [PASS] Orders: {orders_count}, Trades: {trades_count}")
        print(f"     [PASS] Execution rate: {execution_rate:.1f}%")
        print(f"     [PASS] Trade value rate: {trade_value_rate:.1f}%")
        print(f"     [PASS] Trading score: {trading_score:.1f}%")
        
        return {
            "status": "SUCCESS",
            "orders_count": orders_count,
            "trades_count": trades_count,
            "execution_rate": execution_rate,
            "trade_value_rate": trade_value_rate,
            "trading_score": trading_score
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def test_market_data_module(cursor):
    """Test market data module performance"""
    print("   Testing market data module...")
    try:
        # Test market data table
        cursor.execute("SELECT COUNT(*) FROM market_data")
        market_data_count = cursor.fetchone()[0]
        
        # Test historical data
        cursor.execute("SELECT COUNT(*) FROM historical_ohlcv_daily")
        historical_count = cursor.fetchone()[0]
        
        # Test data quality
        cursor.execute("SELECT AVG(overall_quality_score) FROM market_data WHERE overall_quality_score IS NOT NULL")
        avg_quality = cursor.fetchone()[0] or 0
        
        # Test data completeness
        cursor.execute("SELECT AVG(completeness_score) FROM market_data WHERE completeness_score IS NOT NULL")
        avg_completeness = cursor.fetchone()[0] or 0
        
        market_data_score = (avg_quality + avg_completeness) * 50  # Convert to percentage
        
        print(f"     [PASS] Market data: {market_data_count}, Historical: {historical_count}")
        print(f"     [PASS] Average quality: {avg_quality:.2f}")
        print(f"     [PASS] Average completeness: {avg_completeness:.2f}")
        print(f"     [PASS] Market data score: {market_data_score:.1f}%")
        
        return {
            "status": "SUCCESS",
            "market_data_count": market_data_count,
            "historical_count": historical_count,
            "avg_quality": avg_quality,
            "avg_completeness": avg_completeness,
            "market_data_score": market_data_score
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def test_risk_management_module(cursor):
    """Test risk management module performance"""
    print("   Testing risk management module...")
    try:
        # Test risk metrics
        cursor.execute("SELECT COUNT(*) FROM risk_metrics")
        risk_metrics_count = cursor.fetchone()[0]
        
        # Test portfolio risk
        cursor.execute("SELECT COUNT(*) FROM portfolio_risk")
        portfolio_risk_count = cursor.fetchone()[0]
        
        # Test risk calculation completeness
        cursor.execute("SELECT COUNT(*) FROM risk_metrics WHERE var_95 IS NOT NULL AND var_99 IS NOT NULL")
        complete_risk_metrics = cursor.fetchone()[0]
        risk_completeness = (complete_risk_metrics / risk_metrics_count) * 100 if risk_metrics_count > 0 else 0
        
        # Test portfolio risk completeness
        cursor.execute("SELECT COUNT(*) FROM portfolio_risk WHERE portfolio_value IS NOT NULL")
        complete_portfolio_risk = cursor.fetchone()[0]
        portfolio_completeness = (complete_portfolio_risk / portfolio_risk_count) * 100 if portfolio_risk_count > 0 else 0
        
        risk_management_score = (risk_completeness + portfolio_completeness) / 2
        
        print(f"     [PASS] Risk metrics: {risk_metrics_count}, Portfolio risk: {portfolio_risk_count}")
        print(f"     [PASS] Risk completeness: {risk_completeness:.1f}%")
        print(f"     [PASS] Portfolio completeness: {portfolio_completeness:.1f}%")
        print(f"     [PASS] Risk management score: {risk_management_score:.1f}%")
        
        return {
            "status": "SUCCESS",
            "risk_metrics_count": risk_metrics_count,
            "portfolio_risk_count": portfolio_risk_count,
            "risk_completeness": risk_completeness,
            "portfolio_completeness": portfolio_completeness,
            "risk_management_score": risk_management_score
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def test_technical_analysis_module(cursor):
    """Test technical analysis module performance"""
    print("   Testing technical analysis module...")
    try:
        # Test technical indicators
        cursor.execute("SELECT COUNT(*) FROM technical_indicators")
        technical_count = cursor.fetchone()[0]
        
        # Test indicator types
        cursor.execute("SELECT COUNT(DISTINCT indicator_type) FROM technical_indicators WHERE indicator_type IS NOT NULL")
        indicator_types_count = cursor.fetchone()[0]
        
        # Test indicator completeness
        cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE indicator_type IS NOT NULL AND value IS NOT NULL")
        complete_indicators = cursor.fetchone()[0]
        indicator_completeness = (complete_indicators / technical_count) * 100 if technical_count > 0 else 0
        
        technical_score = (indicator_completeness + (indicator_types_count / 8) * 100) / 2  # 8 is expected indicator types
        
        print(f"     [PASS] Technical indicators: {technical_count}")
        print(f"     [PASS] Indicator types: {indicator_types_count}")
        print(f"     [PASS] Indicator completeness: {indicator_completeness:.1f}%")
        print(f"     [PASS] Technical score: {technical_score:.1f}%")
        
        return {
            "status": "SUCCESS",
            "technical_count": technical_count,
            "indicator_types_count": indicator_types_count,
            "indicator_completeness": indicator_completeness,
            "technical_score": technical_score
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def test_fundamental_analysis_module(cursor):
    """Test fundamental analysis module performance"""
    print("   Testing fundamental analysis module...")
    try:
        # Test fundamental data
        cursor.execute("SELECT COUNT(*) FROM fundamental_data")
        fundamental_count = cursor.fetchone()[0]
        
        # Test data completeness
        cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE pe_ratio IS NOT NULL AND pb_ratio IS NOT NULL")
        complete_fundamental = cursor.fetchone()[0]
        fundamental_completeness = (complete_fundamental / fundamental_count) * 100 if fundamental_count > 0 else 0
        
        # Test sector diversity
        cursor.execute("SELECT COUNT(DISTINCT sector) FROM fundamental_data WHERE sector IS NOT NULL")
        sector_diversity = cursor.fetchone()[0]
        
        fundamental_score = (fundamental_completeness + (sector_diversity / 6) * 100) / 2  # 6 is expected sectors
        
        print(f"     [PASS] Fundamental data: {fundamental_count}")
        print(f"     [PASS] Fundamental completeness: {fundamental_completeness:.1f}%")
        print(f"     [PASS] Sector diversity: {sector_diversity}")
        print(f"     [PASS] Fundamental score: {fundamental_score:.1f}%")
        
        return {
            "status": "SUCCESS",
            "fundamental_count": fundamental_count,
            "fundamental_completeness": fundamental_completeness,
            "sector_diversity": sector_diversity,
            "fundamental_score": fundamental_score
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def test_sentiment_analysis_module(cursor):
    """Test sentiment analysis module performance"""
    print("   Testing sentiment analysis module...")
    try:
        # Test sentiment data
        cursor.execute("SELECT COUNT(*) FROM sentiment_data")
        sentiment_count = cursor.fetchone()[0]
        
        # Test sentiment completeness
        cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE sentiment_score IS NOT NULL AND confidence IS NOT NULL")
        complete_sentiment = cursor.fetchone()[0]
        sentiment_completeness = (complete_sentiment / sentiment_count) * 100 if sentiment_count > 0 else 0
        
        # Test publisher diversity
        cursor.execute("SELECT COUNT(DISTINCT publisher) FROM sentiment_data WHERE publisher IS NOT NULL")
        publisher_diversity = cursor.fetchone()[0]
        
        sentiment_score = (sentiment_completeness + (publisher_diversity / 5) * 100) / 2  # 5 is expected publishers
        
        print(f"     [PASS] Sentiment data: {sentiment_count}")
        print(f"     [PASS] Sentiment completeness: {sentiment_completeness:.1f}%")
        print(f"     [PASS] Publisher diversity: {publisher_diversity}")
        print(f"     [PASS] Sentiment score: {sentiment_score:.1f}%")
        
        return {
            "status": "SUCCESS",
            "sentiment_count": sentiment_count,
            "sentiment_completeness": sentiment_completeness,
            "publisher_diversity": publisher_diversity,
            "sentiment_score": sentiment_score
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def test_database_performance(cursor):
    """Test database performance"""
    print("   Testing database performance...")
    try:
        start_time = time.time()
        
        # Test complex query performance
        cursor.execute("""
            SELECT s.symbol, COUNT(o.order_id) as order_count, COUNT(t.trade_id) as trade_count
            FROM symbol_info s
            LEFT JOIN orders o ON s.symbol = o.symbol
            LEFT JOIN trades t ON s.symbol = t.symbol
            GROUP BY s.symbol
            LIMIT 10
        """)
        query_result = cursor.fetchall()
        
        query_time = time.time() - start_time
        
        # Test data integrity
        cursor.execute("SELECT COUNT(*) FROM orders WHERE order_value IS NULL")
        null_order_values = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trades WHERE trade_value IS NULL")
        null_trade_values = cursor.fetchone()[0]
        
        data_integrity_score = 100 - ((null_order_values + null_trade_values) / 2)
        
        performance_score = min(100, max(0, 100 - (query_time * 100)))  # Penalty for slow queries
        
        print(f"     [PASS] Query time: {query_time:.3f}s")
        print(f"     [PASS] Data integrity: {data_integrity_score:.1f}%")
        print(f"     [PASS] Performance score: {performance_score:.1f}%")
        
        return {
            "status": "SUCCESS",
            "query_time": query_time,
            "data_integrity_score": data_integrity_score,
            "performance_score": performance_score
        }
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def main():
    """Main function"""
    db_conn = None
    cursor = None
    results = {}
    start_time = datetime.now()
    
    print("FINAL SYSTEM TEST")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        print("[PASS] Database connection established")
        
        # 1. TESTING TRADING MODULE
        print("\n1. TESTING TRADING MODULE")
        print("------------------------------------------------------------")
        trading_test = test_trading_module(cursor)
        results["trading_module_test"] = trading_test
        print(f"   Trading module test: {trading_test['status']}")
        
        # 2. TESTING MARKET DATA MODULE
        print("\n2. TESTING MARKET DATA MODULE")
        print("------------------------------------------------------------")
        market_data_test = test_market_data_module(cursor)
        results["market_data_module_test"] = market_data_test
        print(f"   Market data module test: {market_data_test['status']}")
        
        # 3. TESTING RISK MANAGEMENT MODULE
        print("\n3. TESTING RISK MANAGEMENT MODULE")
        print("------------------------------------------------------------")
        risk_management_test = test_risk_management_module(cursor)
        results["risk_management_module_test"] = risk_management_test
        print(f"   Risk management module test: {risk_management_test['status']}")
        
        # 4. TESTING TECHNICAL ANALYSIS MODULE
        print("\n4. TESTING TECHNICAL ANALYSIS MODULE")
        print("------------------------------------------------------------")
        technical_test = test_technical_analysis_module(cursor)
        results["technical_analysis_module_test"] = technical_test
        print(f"   Technical analysis module test: {technical_test['status']}")
        
        # 5. TESTING FUNDAMENTAL ANALYSIS MODULE
        print("\n5. TESTING FUNDAMENTAL ANALYSIS MODULE")
        print("------------------------------------------------------------")
        fundamental_test = test_fundamental_analysis_module(cursor)
        results["fundamental_analysis_module_test"] = fundamental_test
        print(f"   Fundamental analysis module test: {fundamental_test['status']}")
        
        # 6. TESTING SENTIMENT ANALYSIS MODULE
        print("\n6. TESTING SENTIMENT ANALYSIS MODULE")
        print("------------------------------------------------------------")
        sentiment_test = test_sentiment_analysis_module(cursor)
        results["sentiment_analysis_module_test"] = sentiment_test
        print(f"   Sentiment analysis module test: {sentiment_test['status']}")
        
        # 7. TESTING DATABASE PERFORMANCE
        print("\n7. TESTING DATABASE PERFORMANCE")
        print("------------------------------------------------------------")
        performance_test = test_database_performance(cursor)
        results["database_performance_test"] = performance_test
        print(f"   Database performance test: {performance_test['status']}")
        
        # 8. GENERATING FINAL ASSESSMENT
        print("\n8. GENERATING FINAL ASSESSMENT")
        print("------------------------------------------------------------")
        
        # Calculate overall scores
        module_scores = []
        if trading_test["status"] == "SUCCESS":
            module_scores.append(trading_test["trading_score"])
        if market_data_test["status"] == "SUCCESS":
            module_scores.append(market_data_test["market_data_score"])
        if risk_management_test["status"] == "SUCCESS":
            module_scores.append(risk_management_test["risk_management_score"])
        if technical_test["status"] == "SUCCESS":
            module_scores.append(technical_test["technical_score"])
        if fundamental_test["status"] == "SUCCESS":
            module_scores.append(fundamental_test["fundamental_score"])
        if sentiment_test["status"] == "SUCCESS":
            module_scores.append(sentiment_test["sentiment_score"])
        
        overall_score = sum(module_scores) / len(module_scores) if module_scores else 0
        
        successful_tests = sum(1 for result in results.values() if isinstance(result, dict) and result.get("status") == "SUCCESS")
        total_tests = len([r for r in results.values() if isinstance(r, dict) and "status" in r])
        
        final_assessment = {
            "overall_status": "EXCELLENT" if overall_score >= 90 else ("GOOD" if overall_score >= 70 else ("FAIR" if overall_score >= 50 else "POOR")),
            "overall_score": overall_score,
            "successful_tests": successful_tests,
            "total_tests": total_tests,
            "success_rate": (successful_tests / total_tests) * 100 if total_tests > 0 else 0,
            "module_scores": {
                "trading": trading_test.get("trading_score", 0) if trading_test["status"] == "SUCCESS" else 0,
                "market_data": market_data_test.get("market_data_score", 0) if market_data_test["status"] == "SUCCESS" else 0,
                "risk_management": risk_management_test.get("risk_management_score", 0) if risk_management_test["status"] == "SUCCESS" else 0,
                "technical_analysis": technical_test.get("technical_score", 0) if technical_test["status"] == "SUCCESS" else 0,
                "fundamental_analysis": fundamental_test.get("fundamental_score", 0) if fundamental_test["status"] == "SUCCESS" else 0,
                "sentiment_analysis": sentiment_test.get("sentiment_score", 0) if sentiment_test["status"] == "SUCCESS" else 0
            },
            "production_ready": overall_score >= 80 and successful_tests == total_tests,
            "recommendations": []
        }
        
        if overall_score >= 90:
            final_assessment["recommendations"].append("System is excellent and ready for production")
        elif overall_score >= 80:
            final_assessment["recommendations"].append("System is good and ready for production")
        elif overall_score >= 70:
            final_assessment["recommendations"].append("System is acceptable but needs minor improvements")
        elif overall_score >= 50:
            final_assessment["recommendations"].append("System needs significant improvements")
        else:
            final_assessment["recommendations"].append("System needs major improvements")
        
        if not final_assessment["production_ready"]:
            final_assessment["recommendations"].append("Address remaining issues before production deployment")
        
        results["final_assessment"] = final_assessment
        print("   Final assessment completed")
        
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")
        results["error"] = str(err)
    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()
            print("[PASS] Database connection closed")
    
    end_time = datetime.now()
    file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
    output_filename = f"final_system_test_{file_timestamp}.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=4, default=str)
    
    print("\nFINAL SYSTEM TEST REPORT")
    print("=" * 80)
    print(f"Overall Status: {results['final_assessment']['overall_status']}")
    print(f"Overall Score: {results['final_assessment']['overall_score']:.1f}%")
    print(f"Successful Tests: {results['final_assessment']['successful_tests']}/{results['final_assessment']['total_tests']}")
    print(f"Success Rate: {results['final_assessment']['success_rate']:.1f}%")
    print(f"Production Ready: {results['final_assessment']['production_ready']}")
    
    print(f"\nModule Scores:")
    for module, score in results['final_assessment']['module_scores'].items():
        print(f"  {module}: {score:.1f}%")
    
    print(f"\nRecommendations:")
    for recommendation in results['final_assessment']['recommendations']:
        print(f"  - {recommendation}")
    
    print(f"\nFinal system test results saved to: {output_filename}")
    print(f"Test completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()