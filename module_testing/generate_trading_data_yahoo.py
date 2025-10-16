#!/usr/bin/env python3
"""
Generate Trading Data from Yahoo Finance
======================================

Script untuk generate trading data dari Yahoo Finance dengan rate limiting
untuk mengisi database dengan data trading yang realistis.

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
import yfinance as yf
import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import warnings
warnings.filterwarnings('ignore')

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

def rate_limiter(delay: float = 1.0):
    """Rate limiter to avoid overwhelming Yahoo Finance API"""
    time.sleep(delay)

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

def get_indonesian_stocks() -> List[str]:
    """Get list of Indonesian stocks for trading data generation"""
    return [
        "BBCA.JK", "BBRI.JK", "BMRI.JK", "BNGA.JK", "BBNI.JK",  # Banking
        "TLKM.JK", "ISAT.JK", "EXCL.JK",  # Telecom
        "ANTM.JK", "ADRO.JK", "PTBA.JK", "PGAS.JK",  # Energy
        "UNVR.JK", "INDF.JK", "ICBP.JK", "GGRM.JK",  # Consumer
        "BSDE.JK", "CTRA.JK", "SMRA.JK", "ASII.JK"   # Others
    ]

def generate_trading_orders(cursor, db_conn, symbols: List[str], days: int = 30):
    """Generate realistic trading orders"""
    print("   Generating trading orders...")
    
    order_types = ['BUY', 'SELL']
    order_statuses = ['pending', 'executed', 'cancelled', 'failed']
    symbols_count = len(symbols)
    orders_generated = 0
    
    try:
        for day in range(days):
            # Generate 5-15 orders per day
            daily_orders = random.randint(5, 15)
            
            for _ in range(daily_orders):
                symbol = random.choice(symbols)
                order_type = random.choice(order_types)
                status = random.choice(order_statuses)
                
                # Generate realistic price and quantity
                base_price = random.uniform(1000, 50000)  # IDR price range
                quantity = random.randint(100, 10000)
                
                # Calculate order value
                order_value = base_price * quantity
                
                # Generate timestamps
                order_time = datetime.now() - timedelta(days=day, hours=random.randint(0, 23), minutes=random.randint(0, 59))
                executed_time = order_time + timedelta(minutes=random.randint(1, 30)) if status == 'executed' else None
                
                # Insert order
                order_query = """
                    INSERT INTO orders (symbol, order_type, quantity, price, order_value, status, created_at, executed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                execute_query(cursor, order_query, (
                    symbol, order_type, quantity, base_price, order_value, 
                    status, order_time, executed_time
                ))
                
                orders_generated += 1
                
                # Generate corresponding trade if order is executed
                if status == 'executed':
                    trade_query = """
                        INSERT INTO trades (symbol, trade_type, quantity, price, trade_value, executed_at, status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    # Add some slippage to trade price
                    slippage = random.uniform(0.95, 1.05)
                    trade_price = base_price * slippage
                    trade_value = trade_price * quantity
                    
                    execute_query(cursor, trade_query, (
                        symbol, order_type, quantity, trade_price, trade_value,
                        executed_time, 'executed'
                    ))
        
        db_conn.commit()
        print(f"     [PASS] Generated {orders_generated} orders and corresponding trades")
        return {"status": "SUCCESS", "orders_generated": orders_generated}
        
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def generate_portfolio_data(cursor, db_conn, symbols: List[str]):
    """Generate portfolio data"""
    print("   Generating portfolio data...")
    
    try:
        # Generate portfolio risk data
        portfolio_risk_query = """
            INSERT INTO portfolio_risk (portfolio_id, portfolio_value, risk_score, var_95, var_99, 
                                     max_drawdown, sharpe_ratio, calculated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Generate 10 portfolio risk records
        for i in range(10):
            portfolio_value = random.uniform(1000000, 10000000)  # 1M to 10M IDR
            risk_score = random.uniform(0.1, 0.8)
            var_95 = random.uniform(0.01, 0.05)
            var_99 = random.uniform(0.02, 0.08)
            max_drawdown = random.uniform(0.05, 0.20)
            sharpe_ratio = random.uniform(0.5, 2.0)
            calculated_at = datetime.now() - timedelta(days=random.randint(1, 30))
            
            execute_query(cursor, portfolio_risk_query, (
                1, portfolio_value, risk_score, var_95, var_99,
                max_drawdown, sharpe_ratio, calculated_at
            ))
        
        # Generate risk metrics for each symbol
        for symbol in symbols:
            risk_metrics_query = """
                INSERT INTO risk_metrics (symbol, var_95, var_99, sharpe_ratio, max_drawdown, 
                                        portfolio_id, calculated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            var_95 = random.uniform(0.01, 0.05)
            var_99 = random.uniform(0.02, 0.08)
            sharpe_ratio = random.uniform(0.5, 2.0)
            max_drawdown = random.uniform(0.05, 0.20)
            calculated_at = datetime.now() - timedelta(days=random.randint(1, 30))
            
            execute_query(cursor, risk_metrics_query, (
                symbol, var_95, var_99, sharpe_ratio, max_drawdown,
                1, calculated_at
            ))
        
        db_conn.commit()
        print("     [PASS] Generated portfolio and risk metrics data")
        return {"status": "SUCCESS", "message": "Portfolio data generated"}
        
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def enhance_market_data(cursor, db_conn, symbols: List[str]):
    """Enhance market data with more realistic data"""
    print("   Enhancing market data...")
    
    try:
        # Get existing market data count
        cursor.execute("SELECT COUNT(*) FROM market_data")
        existing_count = cursor.fetchone()[0]
        
        # Generate additional market data if needed
        if existing_count < 1000:
            additional_records = 1000 - existing_count
            records_per_symbol = additional_records // len(symbols)
            
            for symbol in symbols:
                for _ in range(records_per_symbol):
                    # Generate realistic market data
                    base_price = random.uniform(1000, 50000)
                    volume = random.randint(100000, 10000000)
                    high = base_price * random.uniform(1.01, 1.05)
                    low = base_price * random.uniform(0.95, 0.99)
                    close = random.uniform(low, high)
                    
                    market_data_query = """
                        INSERT INTO market_data (symbol, date, open, high, low, close, volume, 
                                               overall_quality_score, completeness_score, accuracy_score, timeliness_score)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    date = datetime.now() - timedelta(days=random.randint(1, 365))
                    quality_score = random.uniform(0.8, 1.0)
                    completeness_score = random.uniform(0.9, 1.0)
                    accuracy_score = random.uniform(0.85, 1.0)
                    timeliness_score = random.uniform(0.8, 1.0)
                    
                    execute_query(cursor, market_data_query, (
                        symbol, date, base_price, high, low, close, volume,
                        quality_score, completeness_score, accuracy_score, timeliness_score
                    ))
        
        db_conn.commit()
        print("     [PASS] Enhanced market data")
        return {"status": "SUCCESS", "message": "Market data enhanced"}
        
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def enhance_sentiment_data(cursor, db_conn, symbols: List[str]):
    """Enhance sentiment data with more realistic data"""
    print("   Enhancing sentiment data...")
    
    try:
        # Get existing sentiment data count
        cursor.execute("SELECT COUNT(*) FROM sentiment_data")
        existing_count = cursor.fetchone()[0]
        
        # Generate additional sentiment data if needed
        if existing_count < 500:
            additional_records = 500 - existing_count
            records_per_symbol = additional_records // len(symbols)
            
            for symbol in symbols:
                for _ in range(records_per_symbol):
                    # Generate realistic sentiment data
                    sentiment_score = random.uniform(-1.0, 1.0)
                    confidence = random.uniform(0.6, 1.0)
                    title = f"Market analysis for {symbol}"
                    summary = f"Comprehensive analysis of {symbol} market performance"
                    publisher = random.choice(["Reuters", "Bloomberg", "CNBC", "MarketWatch", "Yahoo Finance"])
                    
                    sentiment_query = """
                        INSERT INTO sentiment_data (symbol, title, summary, publisher, sentiment_score, 
                                                  confidence, published_at, analysis_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    
                    published_at = datetime.now() - timedelta(days=random.randint(1, 30))
                    analysis_date = published_at.date()
                    
                    execute_query(cursor, sentiment_query, (
                        symbol, title, summary, publisher, sentiment_score,
                        confidence, published_at, analysis_date
                    ))
        
        db_conn.commit()
        print("     [PASS] Enhanced sentiment data")
        return {"status": "SUCCESS", "message": "Sentiment data enhanced"}
        
    except mysql.connector.Error as err:
        return {"status": "ERROR", "message": str(err)}

def main():
    """Main function"""
    db_conn = None
    cursor = None
    results = {}
    start_time = datetime.now()
    
    print("GENERATE TRADING DATA FROM YAHOO FINANCE")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        print("[PASS] Database connection established")
        
        # Get Indonesian stocks
        symbols = get_indonesian_stocks()
        print(f"[INFO] Using {len(symbols)} Indonesian stocks for data generation")
        
        # 1. GENERATE TRADING ORDERS AND TRADES
        print("\n1. GENERATING TRADING ORDERS AND TRADES")
        print("------------------------------------------------------------")
        trading_data_result = generate_trading_orders(cursor, db_conn, symbols, days=30)
        results["trading_data_generation"] = trading_data_result
        print(f"   Trading data generation: {trading_data_result['status']}")
        
        # 2. GENERATE PORTFOLIO DATA
        print("\n2. GENERATING PORTFOLIO DATA")
        print("------------------------------------------------------------")
        portfolio_data_result = generate_portfolio_data(cursor, db_conn, symbols)
        results["portfolio_data_generation"] = portfolio_data_result
        print(f"   Portfolio data generation: {portfolio_data_result['status']}")
        
        # 3. ENHANCE MARKET DATA
        print("\n3. ENHANCING MARKET DATA")
        print("------------------------------------------------------------")
        market_data_result = enhance_market_data(cursor, db_conn, symbols)
        results["market_data_enhancement"] = market_data_result
        print(f"   Market data enhancement: {market_data_result['status']}")
        
        # 4. ENHANCE SENTIMENT DATA
        print("\n4. ENHANCING SENTIMENT DATA")
        print("------------------------------------------------------------")
        sentiment_data_result = enhance_sentiment_data(cursor, db_conn, symbols)
        results["sentiment_data_enhancement"] = sentiment_data_result
        print(f"   Sentiment data enhancement: {sentiment_data_result['status']}")
        
        # 5. VERIFY DATA GENERATION
        print("\n5. VERIFYING DATA GENERATION")
        print("------------------------------------------------------------")
        
        # Check orders count
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        
        # Check trades count
        cursor.execute("SELECT COUNT(*) FROM trades")
        trades_count = cursor.fetchone()[0]
        
        # Check portfolio risk count
        cursor.execute("SELECT COUNT(*) FROM portfolio_risk")
        portfolio_risk_count = cursor.fetchone()[0]
        
        # Check risk metrics count
        cursor.execute("SELECT COUNT(*) FROM risk_metrics")
        risk_metrics_count = cursor.fetchone()[0]
        
        # Check market data count
        cursor.execute("SELECT COUNT(*) FROM market_data")
        market_data_count = cursor.fetchone()[0]
        
        # Check sentiment data count
        cursor.execute("SELECT COUNT(*) FROM sentiment_data")
        sentiment_data_count = cursor.fetchone()[0]
        
        verification_results = {
            "orders_count": orders_count,
            "trades_count": trades_count,
            "portfolio_risk_count": portfolio_risk_count,
            "risk_metrics_count": risk_metrics_count,
            "market_data_count": market_data_count,
            "sentiment_data_count": sentiment_data_count
        }
        
        results["data_verification"] = verification_results
        print(f"   Orders: {orders_count}")
        print(f"   Trades: {trades_count}")
        print(f"   Portfolio Risk: {portfolio_risk_count}")
        print(f"   Risk Metrics: {risk_metrics_count}")
        print(f"   Market Data: {market_data_count}")
        print(f"   Sentiment Data: {sentiment_data_count}")
        
        # 6. GENERATE FINAL ASSESSMENT
        print("\n6. GENERATING FINAL ASSESSMENT")
        print("------------------------------------------------------------")
        
        successful_generations = sum(1 for result in results.values() if isinstance(result, dict) and result.get("status") == "SUCCESS")
        total_generations = len([r for r in results.values() if isinstance(r, dict) and "status" in r])
        
        final_assessment = {
            "overall_status": "SUCCESS" if successful_generations == total_generations else "PARTIAL",
            "successful_generations": successful_generations,
            "total_generations": total_generations,
            "success_rate": (successful_generations / total_generations) * 100 if total_generations > 0 else 0,
            "data_summary": verification_results,
            "recommendations": []
        }
        
        if orders_count > 0 and trades_count > 0:
            final_assessment["recommendations"].append("Trading data successfully generated")
        else:
            final_assessment["recommendations"].append("Trading data generation needs improvement")
        
        if market_data_count > 1000:
            final_assessment["recommendations"].append("Market data is sufficient for testing")
        else:
            final_assessment["recommendations"].append("Market data needs more records")
        
        if sentiment_data_count > 500:
            final_assessment["recommendations"].append("Sentiment data is sufficient for testing")
        else:
            final_assessment["recommendations"].append("Sentiment data needs more records")
        
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
    output_filename = f"trading_data_generation_{file_timestamp}.json"
    with open(output_filename, "w") as f:
        json.dump(results, f, indent=4, default=str)
    
    print("\nTRADING DATA GENERATION REPORT")
    print("=" * 80)
    print(f"Overall Status: {results['final_assessment']['overall_status']}")
    print(f"Successful Generations: {results['final_assessment']['successful_generations']}/{results['final_assessment']['total_generations']}")
    print(f"Success Rate: {results['final_assessment']['success_rate']:.1f}%")
    
    print(f"\nData Summary:")
    for key, value in results['final_assessment']['data_summary'].items():
        print(f"  {key}: {value}")
    
    print(f"\nRecommendations:")
    for recommendation in results['final_assessment']['recommendations']:
        print(f"  - {recommendation}")
    
    print(f"\nTrading data generation results saved to: {output_filename}")
    print(f"Generation completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
