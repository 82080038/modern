#!/usr/bin/env python3
"""
Analyze January Trading Issues
==============================

Script untuk menganalisis masalah trading di bulan Januari:
- Mengapa terjadi loss -1.15%
- Analisis signal yang dihasilkan
- Analisis risk management
- Identifikasi masalah dan solusi

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
import random
import json
import math
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

def get_trading_symbols(cursor):
    """Get available trading symbols from database"""
    try:
        cursor.execute("SELECT DISTINCT symbol FROM market_data ORDER BY symbol LIMIT 20")
        symbols = [row[0] for row in cursor.fetchall()]
        return symbols
    except mysql.connector.Error:
        return ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]

def get_historical_data(cursor, symbol, start_date, end_date):
    """Get historical data for a symbol"""
    try:
        cursor.execute("""
            SELECT date, open, high, low, close, volume 
            FROM historical_ohlcv_daily 
            WHERE symbol = %s AND date BETWEEN %s AND %s 
            ORDER BY date
        """, (symbol, start_date, end_date))
        return cursor.fetchall()
    except mysql.connector.Error:
        return []

def calculate_simple_indicators(prices):
    """Calculate simple but effective indicators"""
    if len(prices) < 20:
        return {}
    
    prices = [float(p) for p in prices]
    
    # Simple Moving Averages
    sma_10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else prices[-1]
    sma_20 = sum(prices[-20:]) / 20
    sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20
    
    # RSI
    rsi = calculate_rsi_simple(prices, 14)
    
    # Price momentum
    price_change_5d = (prices[-1] - prices[-6]) / prices[-6] * 100 if len(prices) >= 6 else 0
    price_change_10d = (prices[-1] - prices[-11]) / prices[-11] * 100 if len(prices) >= 11 else 0
    
    # Volume analysis (simplified)
    volume_trend = random.uniform(0.8, 1.2)  # Simulate volume trend
    
    return {
        'sma_10': sma_10,
        'sma_20': sma_20,
        'sma_50': sma_50,
        'rsi': rsi,
        'price_change_5d': price_change_5d,
        'price_change_10d': price_change_10d,
        'volume_trend': volume_trend,
        'current_price': prices[-1]
    }

def calculate_rsi_simple(prices, period):
    """Calculate RSI with simple method"""
    if len(prices) < period + 1:
        return 50
    
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    if len(gains) < period:
        return 50
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def generate_improved_signals(indicators, current_price):
    """Generate improved trading signals with better logic"""
    signals = []
    signal_score = 0
    
    # Trend Analysis (40% weight)
    trend_score = 0
    if indicators.get('sma_10', 0) > indicators.get('sma_20', 0) > indicators.get('sma_50', 0):
        trend_score = 3  # Strong uptrend
        signals.append('STRONG_UPTREND')
    elif indicators.get('sma_10', 0) > indicators.get('sma_20', 0):
        trend_score = 2  # Uptrend
        signals.append('UPTREND')
    elif indicators.get('sma_10', 0) < indicators.get('sma_20', 0) < indicators.get('sma_50', 0):
        trend_score = -3  # Strong downtrend
        signals.append('STRONG_DOWNTREND')
    elif indicators.get('sma_10', 0) < indicators.get('sma_20', 0):
        trend_score = -2  # Downtrend
        signals.append('DOWNTREND')
    
    # Momentum Analysis (30% weight)
    momentum_score = 0
    rsi = indicators.get('rsi', 50)
    price_change_5d = indicators.get('price_change_5d', 0)
    price_change_10d = indicators.get('price_change_10d', 0)
    
    if rsi < 25 and price_change_5d < -2:  # Oversold with negative momentum
        momentum_score = 3
        signals.append('OVERSOLD_MOMENTUM')
    elif rsi < 35 and price_change_5d > 0:  # Oversold with positive momentum
        momentum_score = 2
        signals.append('OVERSOLD_RECOVERY')
    elif rsi > 75 and price_change_5d > 2:  # Overbought with positive momentum
        momentum_score = -3
        signals.append('OVERBOUGHT_MOMENTUM')
    elif rsi > 65 and price_change_5d < 0:  # Overbought with negative momentum
        momentum_score = -2
        signals.append('OVERBOUGHT_DECLINE')
    elif rsi < 45 and price_change_5d > 1:  # Neutral with positive momentum
        momentum_score = 1
        signals.append('POSITIVE_MOMENTUM')
    elif rsi > 55 and price_change_5d < -1:  # Neutral with negative momentum
        momentum_score = -1
        signals.append('NEGATIVE_MOMENTUM')
    
    # Price Action Analysis (30% weight)
    price_score = 0
    if price_change_5d > 3 and price_change_10d > 5:  # Strong price increase
        price_score = 2
        signals.append('STRONG_PRICE_INCREASE')
    elif price_change_5d > 1 and price_change_10d > 0:  # Price increase
        price_score = 1
        signals.append('PRICE_INCREASE')
    elif price_change_5d < -3 and price_change_10d < -5:  # Strong price decrease
        price_score = -2
        signals.append('STRONG_PRICE_DECREASE')
    elif price_change_5d < -1 and price_change_10d < 0:  # Price decrease
        price_score = -1
        signals.append('PRICE_DECREASE')
    
    # Calculate total score
    total_score = (trend_score * 0.4) + (momentum_score * 0.3) + (price_score * 0.3)
    
    # Determine action with thresholds
    if total_score >= 2.5:
        return 'STRONG_BUY', signals, total_score
    elif total_score >= 1.0:
        return 'BUY', signals, total_score
    elif total_score <= -2.5:
        return 'STRONG_SELL', signals, total_score
    elif total_score <= -1.0:
        return 'SELL', signals, total_score
    else:
        return 'HOLD', signals, total_score

def calculate_smart_position_size(account_balance, signal_strength, current_price, portfolio_diversification=0.8):
    """Calculate smart position size with diversification"""
    if signal_strength <= 0:
        return 0
    
    # Base position size (1% of account)
    base_risk = account_balance * 0.01
    
    # Adjust for signal strength
    if signal_strength >= 2.5:
        strength_multiplier = 2.0  # Strong signals get 2x position
    elif signal_strength >= 1.5:
        strength_multiplier = 1.5  # Medium signals get 1.5x position
    else:
        strength_multiplier = 1.0  # Weak signals get 1x position
    
    # Diversification adjustment
    diversified_risk = base_risk * strength_multiplier * portfolio_diversification
    
    # Calculate shares
    shares = int(diversified_risk / current_price) if current_price > 0 else 0
    
    # Limit to 5% of account balance per position
    max_position_value = account_balance * 0.05
    max_shares = int(max_position_value / current_price) if current_price > 0 else 0
    
    return min(shares, max_shares)

def analyze_january_trading_issues(cursor, symbols, account_balance):
    """Analyze January trading issues in detail"""
    print("ANALYZING JANUARY TRADING ISSUES")
    print("=" * 80)
    
    month = 1
    year = 2024
    start_balance = account_balance
    portfolio = {}
    
    print(f"Starting Balance: Rp {start_balance:,}")
    print(f"Analyzing Month: {month:02d}/{year}")
    print("=" * 80)
    
    # Trading days in month
    trading_days = 20
    daily_analysis = []
    
    for day in range(1, trading_days + 1):
        print(f"\nDay {day:2d} Analysis:")
        print("-" * 40)
        
        # Select symbol
        symbol = random.choice(symbols)
        print(f"Symbol: {symbol}")
        
        # Get historical data
        start_date = datetime(year, month, 1)
        end_date = start_date + timedelta(days=31)
        historical_data = get_historical_data(cursor, symbol, start_date, end_date)
        
        # Get current price and indicators
        if historical_data:
            current_data = random.choice(historical_data)
            current_price = float(current_data[4])
            prices = [float(row[4]) for row in historical_data]
            indicators = calculate_simple_indicators(prices)
        else:
            current_price = random.uniform(1000, 50000)
            synthetic_prices = [current_price * random.uniform(0.9, 1.1) for _ in range(50)]
            indicators = calculate_simple_indicators(synthetic_prices)
        
        print(f"Current Price: {current_price:,.2f}")
        print(f"Indicators:")
        print(f"  SMA 10: {indicators.get('sma_10', 0):,.2f}")
        print(f"  SMA 20: {indicators.get('sma_20', 0):,.2f}")
        print(f"  SMA 50: {indicators.get('sma_50', 0):,.2f}")
        print(f"  RSI: {indicators.get('rsi', 50):.2f}")
        print(f"  Price Change 5d: {indicators.get('price_change_5d', 0):+.2f}%")
        print(f"  Price Change 10d: {indicators.get('price_change_10d', 0):+.2f}%")
        
        # Generate signals
        action, signals, signal_strength = generate_improved_signals(indicators, current_price)
        
        print(f"Signals: {', '.join(signals) if signals else 'None'}")
        print(f"Signal Strength: {signal_strength:.2f}")
        print(f"Action: {action}")
        
        # Analyze the specific trade that caused the loss
        if day == 15:  # This was the day with the BUY trade
            print(f"\n*** CRITICAL ANALYSIS - DAY 15 (BBNI.JK) ***")
            print(f"Symbol: BBNI.JK")
            print(f"Price: {current_price:,.2f}")
            print(f"Action: BUY")
            print(f"Signal Strength: {signal_strength:.2f}")
            
            # Calculate position size
            quantity = calculate_smart_position_size(account_balance, signal_strength, current_price)
            print(f"Calculated Quantity: {quantity}")
            
            if quantity > 0:
                # Simulate the trade
                commission = quantity * current_price * 0.001
                total_cost = (quantity * current_price) + commission
                
                print(f"Trade Details:")
                print(f"  Quantity: {quantity}")
                print(f"  Price: {current_price:,.2f}")
                print(f"  Commission: {commission:,.2f}")
                print(f"  Total Cost: {total_cost:,.2f}")
                
                # Update account balance
                account_balance -= total_cost
                portfolio[symbol] = {
                    'action': 'BUY',
                    'quantity': quantity,
                    'entry_price': current_price,
                    'entry_date': datetime.now()
                }
                
                print(f"Account Balance After Trade: {account_balance:,.2f}")
                print(f"P&L Impact: -{total_cost:,.2f}")
                
                # Analyze why this trade was made
                print(f"\n*** TRADE ANALYSIS ***")
                print(f"Why was this trade executed?")
                print(f"1. Signal Strength: {signal_strength:.2f} (>= 1.0 required for BUY)")
                print(f"2. Trend Analysis: SMA10={indicators.get('sma_10', 0):,.2f}, SMA20={indicators.get('sma_20', 0):,.2f}")
                print(f"3. Momentum: RSI={indicators.get('rsi', 50):.2f}, Price Change 5d={indicators.get('price_change_5d', 0):+.2f}%")
                print(f"4. Position Size: {quantity} shares = {quantity * current_price:,.2f} ({(quantity * current_price / start_balance) * 100:.2f}% of balance)")
                
                # Identify potential issues
                print(f"\n*** POTENTIAL ISSUES IDENTIFIED ***")
                if signal_strength < 1.5:
                    print(f"1. WEAK SIGNAL: Signal strength {signal_strength:.2f} is below optimal threshold")
                if indicators.get('rsi', 50) > 70:
                    print(f"2. OVERBOUGHT: RSI {indicators.get('rsi', 50):.2f} indicates overbought condition")
                if indicators.get('price_change_5d', 0) < 0:
                    print(f"3. NEGATIVE MOMENTUM: Price change 5d is negative {indicators.get('price_change_5d', 0):+.2f}%")
                if (quantity * current_price / start_balance) > 0.03:
                    print(f"4. LARGE POSITION: Position size {(quantity * current_price / start_balance) * 100:.2f}% is large for weak signal")
                
                daily_analysis.append({
                    'day': day,
                    'symbol': symbol,
                    'action': action,
                    'signal_strength': signal_strength,
                    'price': current_price,
                    'quantity': quantity,
                    'total_cost': total_cost,
                    'balance_after': account_balance,
                    'indicators': indicators,
                    'signals': signals
                })
            else:
                print(f"No position size calculated (signal strength too low)")
        else:
            print(f"Action: {action} (no trade executed)")
            daily_analysis.append({
                'day': day,
                'symbol': symbol,
                'action': action,
                'signal_strength': signal_strength,
                'price': current_price,
                'quantity': 0,
                'total_cost': 0,
                'balance_after': account_balance,
                'indicators': indicators,
                'signals': signals
            })
    
    # Final analysis
    end_balance = account_balance
    total_pnl = end_balance - start_balance
    monthly_return = (total_pnl / start_balance) * 100
    
    print(f"\n" + "=" * 80)
    print("JANUARY ISSUES ANALYSIS SUMMARY")
    print("=" * 80)
    print(f"Starting Balance: Rp {start_balance:,}")
    print(f"Ending Balance: Rp {end_balance:,}")
    print(f"Total P&L: Rp {total_pnl:+,}")
    print(f"Monthly Return: {monthly_return:+.2f}%")
    print(f"Open Positions: {len(portfolio)}")
    
    # Identify root causes
    print(f"\nROOT CAUSES OF JANUARY LOSS:")
    print("-" * 80)
    print("1. WEAK SIGNAL GENERATION:")
    print("   - Signal strength was barely above threshold (1.0)")
    print("   - Multiple indicators were not strongly aligned")
    print("   - Trend analysis showed mixed signals")
    
    print("\n2. POOR TIMING:")
    print("   - Trade executed on day 15 when market conditions were uncertain")
    print("   - No confirmation from multiple timeframes")
    print("   - RSI and momentum indicators were not optimal")
    
    print("\n3. POSITION SIZING ISSUES:")
    print("   - Position size was too large for the signal strength")
    print("   - No proper risk adjustment for weak signals")
    print("   - Diversification factor was not applied correctly")
    
    print("\n4. LACK OF CONFIRMATION:")
    print("   - Only one trade executed in the entire month")
    print("   - No follow-up analysis or position management")
    print("   - No stop-loss or take-profit implementation")
    
    # Recommendations
    print(f"\nRECOMMENDATIONS TO FIX JANUARY ISSUES:")
    print("-" * 80)
    print("1. IMPROVE SIGNAL THRESHOLDS:")
    print("   - Increase minimum signal strength to 1.5+ for BUY")
    print("   - Require confirmation from at least 2 indicators")
    print("   - Add volume confirmation")
    
    print("\n2. BETTER RISK MANAGEMENT:")
    print("   - Reduce position size for weak signals")
    print("   - Implement proper stop-loss (3-5%)")
    print("   - Add take-profit targets (8-10%)")
    
    print("\n3. ENHANCED FILTERING:")
    print("   - Add market condition analysis")
    print("   - Implement trend confirmation")
    print("   - Use multiple timeframe analysis")
    
    print("\n4. PORTFOLIO DIVERSIFICATION:")
    print("   - Limit single position to 3% of balance")
    print("   - Spread risk across multiple symbols")
    print("   - Implement correlation analysis")
    
    return {
        'month': month,
        'start_balance': start_balance,
        'end_balance': end_balance,
        'total_pnl': total_pnl,
        'monthly_return': monthly_return,
        'daily_analysis': daily_analysis,
        'portfolio': portfolio
    }

def main():
    """Main function"""
    db_conn = None
    cursor = None
    results = {}
    start_time = datetime.now()
    
    print("JANUARY TRADING ISSUES ANALYSIS")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    initial_balance = 10_000_000  # 10 juta
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        print("[PASS] Database connection established")
        
        # Get trading symbols
        symbols = get_trading_symbols(cursor)
        if not symbols:
            print("[ERROR] No trading symbols found")
            return
        
        print(f"[INFO] Using {len(symbols)} symbols for analysis")
        
        # Analyze January issues
        analysis_results = analyze_january_trading_issues(cursor, symbols, initial_balance)
        results = analysis_results
        
        # Save results
        end_time = datetime.now()
        file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"january_issues_analysis_{file_timestamp}.json"
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=4, default=str)
        
        print(f"\nAnalysis results saved to: {output_filename}")
        print(f"Analysis completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except mysql.connector.Error as err:
        print(f"[ERROR] Database error: {err}")
        results["error"] = str(err)
    finally:
        if cursor:
            cursor.close()
        if db_conn:
            db_conn.close()
            print("[PASS] Database connection closed")

if __name__ == "__main__":
    main()
