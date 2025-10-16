#!/usr/bin/env python3
"""
Time Lapse Trading Simulation
============================

Script untuk melakukan simulasi trading selama 1 tahun dengan modal 10 juta.
Menampilkan langkah perhitungan, logika, alur dan hasil di terminal.

Author: AI Assistant
Date: 2025-01-17
"""

import mysql.connector
import random
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import math

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
    print("   Getting trading symbols...")
    try:
        cursor.execute("SELECT DISTINCT symbol FROM market_data ORDER BY symbol LIMIT 20")
        symbols = [row[0] for row in cursor.fetchall()]
        print(f"     [PASS] Found {len(symbols)} trading symbols: {', '.join(symbols[:5])}...")
        return symbols
    except mysql.connector.Error as err:
        print(f"     [ERROR] {err}")
        return ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]  # Fallback

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

def calculate_technical_indicators(prices):
    """Calculate technical indicators"""
    if len(prices) < 20:
        return {}
    
    # Simple Moving Average (SMA)
    sma_20 = sum(prices[-20:]) / 20
    sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else sma_20
    
    # RSI calculation
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
    
    if len(gains) >= 14:
        avg_gain = sum(gains[-14:]) / 14
        avg_loss = sum(losses[-14:]) / 14
        rs = avg_gain / avg_loss if avg_loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))
    else:
        rsi = 50
    
    # MACD calculation
    ema_12 = prices[-1]  # Simplified
    ema_26 = prices[-1]  # Simplified
    macd = ema_12 - ema_26
    
    return {
        'sma_20': sma_20,
        'sma_50': sma_50,
        'rsi': rsi,
        'macd': macd
    }

def generate_trading_signals(indicators, current_price):
    """Generate trading signals based on technical indicators"""
    signals = []
    
    # Check if indicators are available
    if not indicators or len(indicators) == 0:
        return signals
    
    # RSI signals
    if 'rsi' in indicators:
        if indicators['rsi'] < 30:
            signals.append('BUY_OVERSOLD')
        elif indicators['rsi'] > 70:
            signals.append('SELL_OVERBOUGHT')
    
    # Moving average signals
    if 'sma_20' in indicators and 'sma_50' in indicators:
        if indicators['sma_20'] > indicators['sma_50'] and current_price > indicators['sma_20']:
            signals.append('BUY_TREND_UP')
        elif indicators['sma_20'] < indicators['sma_50'] and current_price < indicators['sma_20']:
            signals.append('SELL_TREND_DOWN')
    
    # MACD signals
    if 'macd' in indicators:
        if indicators['macd'] > 0:
            signals.append('BUY_MACD_POSITIVE')
        else:
            signals.append('SELL_MACD_NEGATIVE')
    
    return signals

def calculate_position_size(account_balance, risk_per_trade=0.02, stock_price=0):
    """Calculate position size based on risk management"""
    if stock_price <= 0:
        return 0
    
    # Convert to float to avoid type errors
    stock_price = float(stock_price)
    
    max_risk_amount = account_balance * risk_per_trade
    max_shares = int(max_risk_amount / stock_price)
    
    # Limit position size to 10% of account balance
    max_position_value = account_balance * 0.1
    max_shares_by_value = int(max_position_value / stock_price)
    
    return min(max_shares, max_shares_by_value)

def execute_trade(symbol, action, quantity, price, commission_rate=0.001):
    """Execute a trade and return trade details"""
    commission = quantity * price * commission_rate
    total_cost = (quantity * price) + commission
    
    return {
        'symbol': symbol,
        'action': action,
        'quantity': quantity,
        'price': price,
        'commission': commission,
        'total_cost': total_cost,
        'timestamp': datetime.now()
    }

def simulate_monthly_trading(cursor, symbols, account_balance, month, year):
    """Simulate trading for one month"""
    print(f"\n   === MONTH {month:02d}/{year} ===")
    
    monthly_start_balance = account_balance
    monthly_trades = []
    monthly_pnl = 0
    
    # Get trading days in month (simplified - 20 trading days)
    trading_days = 20
    
    for day in range(1, trading_days + 1):
        print(f"     Day {day:2d}: ", end="")
        
        # Select random symbol for the day
        symbol = random.choice(symbols)
        
        # Get historical data for the symbol
        start_date = datetime(year, month, 1)
        end_date = start_date + timedelta(days=31)
        historical_data = get_historical_data(cursor, symbol, start_date, end_date)
        
        # Get current price (simulate with historical data or generate synthetic)
        if historical_data:
            current_data = random.choice(historical_data)
            current_price = float(current_data[4])  # close price
            # Calculate technical indicators from historical data
            prices = [float(row[4]) for row in historical_data]  # close prices
            indicators = calculate_technical_indicators(prices)
        else:
            # Generate synthetic price and indicators if no historical data
            current_price = random.uniform(1000, 50000)
            # Generate synthetic price history for indicators
            synthetic_prices = [current_price * random.uniform(0.95, 1.05) for _ in range(50)]
            indicators = calculate_technical_indicators(synthetic_prices)
        
        # Generate trading signals
        signals = generate_trading_signals(indicators, current_price)
        
        # Determine action based on signals
        buy_signals = [s for s in signals if 'BUY' in s]
        sell_signals = [s for s in signals if 'SELL' in s]
        
        action = None
        if len(buy_signals) >= 2:  # Need at least 2 buy signals
            action = 'BUY'
        elif len(sell_signals) >= 2:  # Need at least 2 sell signals
            action = 'SELL'
        
        if action:
            # Calculate position size
            quantity = calculate_position_size(account_balance, 0.02, current_price)
            
            if quantity > 0:
                # Execute trade
                trade = execute_trade(symbol, action, quantity, current_price)
                monthly_trades.append(trade)
                
                if action == 'BUY':
                    account_balance -= trade['total_cost']
                    print(f"BUY {quantity} {symbol} @ {current_price:.2f} = -{trade['total_cost']:,.0f}")
                else:  # SELL
                    account_balance += (quantity * current_price) - trade['commission']
                    print(f"SELL {quantity} {symbol} @ {current_price:.2f} = +{quantity * current_price - trade['commission']:,.0f}")
            else:
                print(f"No position size for {symbol}")
        else:
            print(f"No signal for {symbol}")
    
    monthly_end_balance = account_balance
    monthly_pnl = monthly_end_balance - monthly_start_balance
    monthly_return = (monthly_pnl / monthly_start_balance) * 100 if monthly_start_balance > 0 else 0
    
    print(f"     Monthly P&L: {monthly_pnl:+,.0f} ({monthly_return:+.2f}%)")
    print(f"     Monthly Balance: {monthly_end_balance:,.0f}")
    print(f"     Monthly Trades: {len(monthly_trades)}")
    
    return {
        'month': month,
        'start_balance': monthly_start_balance,
        'end_balance': monthly_end_balance,
        'pnl': monthly_pnl,
        'return_pct': monthly_return,
        'trades_count': len(monthly_trades),
        'trades': monthly_trades
    }

def main():
    """Main function"""
    db_conn = None
    cursor = None
    results = {}
    start_time = datetime.now()
    
    print("TIME LAPSE TRADING SIMULATION")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Simulation parameters
    initial_balance = 10_000_000  # 10 juta
    simulation_year = 2024
    account_balance = initial_balance
    
    print(f"Initial Balance: Rp {initial_balance:,}")
    print(f"Simulation Year: {simulation_year}")
    print(f"Risk per Trade: 2%")
    print(f"Max Position Size: 10% of balance")
    print("=" * 80)
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        print("[PASS] Database connection established")
        
        # Get trading symbols
        symbols = get_trading_symbols(cursor)
        if not symbols:
            print("[ERROR] No trading symbols found")
            return
        
        print(f"[INFO] Using {len(symbols)} symbols for trading")
        
        # Monthly results storage
        monthly_results = []
        total_trades = 0
        total_commission = 0
        
        # Simulate 12 months
        for month in range(1, 13):
            print(f"\nSIMULATING MONTH {month:02d}/{simulation_year}")
            print("-" * 60)
            
            month_result = simulate_monthly_trading(cursor, symbols, account_balance, month, simulation_year)
            monthly_results.append(month_result)
            
            # Update account balance
            account_balance = month_result['end_balance']
            total_trades += month_result['trades_count']
            
            # Calculate commission
            for trade in month_result['trades']:
                total_commission += trade['commission']
            
            print(f"     Month {month:02d} Summary:")
            print(f"       Start: Rp {month_result['start_balance']:,}")
            print(f"       End:   Rp {month_result['end_balance']:,}")
            print(f"       P&L:   Rp {month_result['pnl']:+,}")
            print(f"       Return: {month_result['return_pct']:+.2f}%")
            print(f"       Trades: {month_result['trades_count']}")
        
        # Calculate final results
        final_balance = account_balance
        total_pnl = final_balance - initial_balance
        total_return = (total_pnl / initial_balance) * 100
        
        # Calculate monthly averages
        monthly_returns = [result['return_pct'] for result in monthly_results]
        avg_monthly_return = sum(monthly_returns) / len(monthly_returns)
        
        # Calculate best and worst months
        best_month = max(monthly_results, key=lambda x: x['return_pct'])
        worst_month = min(monthly_results, key=lambda x: x['return_pct'])
        
        # Calculate Sharpe ratio (simplified)
        if len(monthly_returns) > 1:
            monthly_std = math.sqrt(sum([(r - avg_monthly_return) ** 2 for r in monthly_returns]) / (len(monthly_returns) - 1))
            sharpe_ratio = avg_monthly_return / monthly_std if monthly_std > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Generate final report
        results = {
            'simulation_period': f"1 year ({simulation_year})",
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_pnl': total_pnl,
            'total_return_pct': total_return,
            'avg_monthly_return': avg_monthly_return,
            'total_trades': total_trades,
            'total_commission': total_commission,
            'best_month': {
                'month': best_month['month'],
                'return_pct': best_month['return_pct'],
                'pnl': best_month['pnl']
            },
            'worst_month': {
                'month': worst_month['month'],
                'return_pct': worst_month['return_pct'],
                'pnl': worst_month['pnl']
            },
            'sharpe_ratio': sharpe_ratio,
            'monthly_results': monthly_results
        }
        
        # Display final results
        print("\n" + "=" * 80)
        print("FINAL TRADING SIMULATION RESULTS")
        print("=" * 80)
        print(f"Simulation Period: 1 year ({simulation_year})")
        print(f"Initial Balance: Rp {initial_balance:,}")
        print(f"Final Balance: Rp {final_balance:,}")
        print(f"Total P&L: Rp {total_pnl:+,}")
        print(f"Total Return: {total_return:+.2f}%")
        print(f"Average Monthly Return: {avg_monthly_return:+.2f}%")
        print(f"Total Trades: {total_trades}")
        print(f"Total Commission: Rp {total_commission:,.0f}")
        print(f"Best Month: {best_month['month']:02d} ({best_month['return_pct']:+.2f}%)")
        print(f"Worst Month: {worst_month['month']:02d} ({worst_month['return_pct']:+.2f}%)")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        
        print("\nMONTHLY BREAKDOWN:")
        print("-" * 80)
        for result in monthly_results:
            print(f"Month {result['month']:02d}: {result['return_pct']:+6.2f}% | "
                  f"P&L: Rp {result['pnl']:+8,.0f} | "
                  f"Balance: Rp {result['end_balance']:8,.0f} | "
                  f"Trades: {result['trades_count']:3d}")
        
        # Performance analysis
        print("\nPERFORMANCE ANALYSIS:")
        print("-" * 80)
        if total_return > 0:
            print("[PASS] PROFITABLE TRADING")
            print(f"   Annual Return: {total_return:.2f}%")
            print(f"   Monthly Average: {avg_monthly_return:.2f}%")
        else:
            print("[FAIL] LOSS-MAKING TRADING")
            print(f"   Annual Loss: {total_return:.2f}%")
            print(f"   Monthly Average: {avg_monthly_return:.2f}%")
        
        if sharpe_ratio > 1:
            print("[PASS] GOOD RISK-ADJUSTED RETURNS")
        elif sharpe_ratio > 0:
            print("[WARN] MODERATE RISK-ADJUSTED RETURNS")
        else:
            print("[FAIL] POOR RISK-ADJUSTED RETURNS")
        
        # Save results
        end_time = datetime.now()
        file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"time_lapse_simulation_{file_timestamp}.json"
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=4, default=str)
        
        print(f"\nResults saved to: {output_filename}")
        print(f"Simulation completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
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
