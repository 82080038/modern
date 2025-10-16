#!/usr/bin/env python3
"""
Test Optimized System
=====================

Sistem untuk menguji performa sistem trading yang telah dioptimasi
dengan parameter dan modul yang telah diperbaiki.

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

def load_optimized_parameters(cursor):
    """Load optimized parameters from database"""
    print("Loading optimized parameters...")
    
    try:
        cursor.execute("SELECT parameter_name, parameter_value FROM trading_parameters")
        params = cursor.fetchall()
        
        optimized_params = {}
        for param_name, param_value in params:
            optimized_params[param_name] = float(param_value)
        
        print(f"[PASS] Loaded {len(optimized_params)} optimized parameters")
        return optimized_params
    except mysql.connector.Error as err:
        print(f"[ERROR] Could not load optimized parameters: {err}")
        return {}

def get_trading_symbols(cursor):
    """Get available trading symbols"""
    try:
        cursor.execute("SELECT DISTINCT symbol FROM market_data ORDER BY symbol LIMIT 20")
        symbols = [row[0] for row in cursor.fetchall()]
        return symbols
    except mysql.connector.Error:
        return ["BBCA.JK", "BBRI.JK", "BMRI.JK", "TLKM.JK", "ASII.JK"]

def calculate_enhanced_indicators(prices, volume_data=None):
    """Calculate enhanced technical indicators"""
    if len(prices) < 100:
        base_price = prices[-1] if prices else 1000
        synthetic_prices = [base_price * random.uniform(0.95, 1.05) for _ in range(200)]
        prices = synthetic_prices
    
    prices = [float(p) for p in prices]
    
    # Enhanced Moving Averages
    sma_5 = sum(prices[-5:]) / 5 if len(prices) >= 5 else prices[-1]
    sma_10 = sum(prices[-10:]) / 10 if len(prices) >= 10 else prices[-1]
    sma_20 = sum(prices[-20:]) / 20 if len(prices) >= 20 else prices[-1]
    sma_50 = sum(prices[-50:]) / 50 if len(prices) >= 50 else prices[-1]
    sma_200 = sum(prices[-200:]) / 200 if len(prices) >= 200 else prices[-1]
    
    # Enhanced RSI
    rsi_14 = calculate_rsi(prices, 14)
    rsi_21 = calculate_rsi(prices, 21)
    rsi_50 = calculate_rsi(prices, 50)
    
    # Enhanced MACD
    macd_line, macd_signal, macd_hist = calculate_macd(prices, 12, 26, 9)
    
    # Enhanced Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(prices, 20, 2)
    
    # Enhanced Stochastic
    stoch_k, stoch_d = calculate_stochastic(prices, 14, 3)
    
    # Enhanced Williams %R
    williams_r = calculate_williams_r(prices, 14)
    
    # Enhanced CCI
    cci = calculate_cci(prices, 20)
    
    # Enhanced ATR
    atr = calculate_atr(prices, 14)
    
    # Volume analysis
    volume_ratio = random.uniform(0.8, 1.2) if volume_data else 1.0
    
    # Price momentum
    price_change_1d = (prices[-1] - prices[-2]) / prices[-2] * 100 if len(prices) >= 2 else 0
    price_change_5d = (prices[-1] - prices[-6]) / prices[-6] * 100 if len(prices) >= 6 else 0
    price_change_20d = (prices[-1] - prices[-21]) / prices[-21] * 100 if len(prices) >= 21 else 0
    
    # Volatility analysis
    volatility_20d = calculate_volatility(prices, 20)
    
    # Trend strength
    trend_strength = calculate_trend_strength(prices, 20)
    
    return {
        'sma_5': sma_5, 'sma_10': sma_10, 'sma_20': sma_20, 'sma_50': sma_50, 'sma_200': sma_200,
        'rsi_14': rsi_14, 'rsi_21': rsi_21, 'rsi_50': rsi_50,
        'macd_line': macd_line, 'macd_signal': macd_signal, 'macd_hist': macd_hist,
        'bb_upper': bb_upper, 'bb_middle': bb_middle, 'bb_lower': bb_lower,
        'stoch_k': stoch_k, 'stoch_d': stoch_d,
        'williams_r': williams_r, 'cci': cci, 'atr': atr,
        'volume_ratio': volume_ratio,
        'price_change_1d': price_change_1d, 'price_change_5d': price_change_5d, 'price_change_20d': price_change_20d,
        'volatility_20d': volatility_20d, 'trend_strength': trend_strength,
        'current_price': prices[-1]
    }

def calculate_rsi(prices, period):
    """Calculate RSI"""
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

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """Calculate MACD"""
    if len(prices) < slow:
        return 0, 0, 0
    
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd_line = ema_fast - ema_slow
    macd_signal = calculate_ema([macd_line] * len(prices), signal)
    macd_histogram = macd_line - macd_signal
    
    return macd_line, macd_signal, macd_histogram

def calculate_ema(prices, period):
    """Calculate EMA"""
    if len(prices) < period:
        return prices[-1]
    
    multiplier = 2 / (period + 1)
    ema = prices[0]
    
    for price in prices[1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema

def calculate_bollinger_bands(prices, period, std_dev):
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return prices[-1], prices[-1], prices[-1]
    
    sma = sum(prices[-period:]) / period
    variance = sum((x - sma) ** 2 for x in prices[-period:]) / period
    std = math.sqrt(variance)
    
    upper = sma + (std * std_dev)
    lower = sma - (std * std_dev)
    
    return upper, sma, lower

def calculate_stochastic(prices, k_period=14, d_period=3):
    """Calculate Stochastic Oscillator"""
    if len(prices) < k_period:
        return 50, 50
    
    recent_prices = prices[-k_period:]
    highest_high = max(recent_prices)
    lowest_low = min(recent_prices)
    
    if highest_high == lowest_low:
        return 50, 50
    
    k_percent = ((prices[-1] - lowest_low) / (highest_high - lowest_low)) * 100
    d_percent = k_percent  # Simplified
    
    return k_percent, d_percent

def calculate_williams_r(prices, period=14):
    """Calculate Williams %R"""
    if len(prices) < period:
        return -50
    
    recent_prices = prices[-period:]
    highest_high = max(recent_prices)
    lowest_low = min(recent_prices)
    
    if highest_high == lowest_low:
        return -50
    
    williams_r = ((highest_high - prices[-1]) / (highest_high - lowest_low)) * -100
    return williams_r

def calculate_cci(prices, period=20):
    """Calculate CCI"""
    if len(prices) < period:
        return 0
    
    recent_prices = prices[-period:]
    typical_price = recent_prices  # Simplified
    sma_tp = sum(typical_price) / len(typical_price)
    mean_deviation = sum(abs(x - sma_tp) for x in typical_price) / len(typical_price)
    
    if mean_deviation == 0:
        return 0
    
    cci = (typical_price[-1] - sma_tp) / (0.015 * mean_deviation)
    return cci

def calculate_atr(prices, period=14):
    """Calculate ATR"""
    if len(prices) < period + 1:
        return 0
    
    true_ranges = []
    for i in range(1, len(prices)):
        high = prices[i]
        low = prices[i-1]
        close = prices[i-1]
        
        tr1 = high - low
        tr2 = abs(high - close)
        tr3 = abs(low - close)
        
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)
    
    if len(true_ranges) < period:
        return 0
    
    atr = sum(true_ranges[-period:]) / period
    return atr

def calculate_volatility(prices, period):
    """Calculate volatility"""
    if len(prices) < period:
        return 0
    
    returns = []
    for i in range(1, len(prices)):
        returns.append((prices[i] - prices[i-1]) / prices[i-1])
    
    if len(returns) < period:
        return 0
    
    avg_return = sum(returns[-period:]) / period
    variance = sum((r - avg_return) ** 2 for r in returns[-period:]) / period
    volatility = math.sqrt(variance) * 100
    
    return volatility

def calculate_trend_strength(prices, period):
    """Calculate trend strength"""
    if len(prices) < period:
        return 0
    
    recent_prices = prices[-period:]
    slope = (recent_prices[-1] - recent_prices[0]) / len(recent_prices)
    trend_strength = slope / recent_prices[-1] * 100
    
    return trend_strength

def generate_enhanced_signals(indicators, optimized_params):
    """Generate enhanced signals with optimized parameters"""
    signals = []
    signal_score = 0
    
    # Get optimized thresholds
    buy_threshold = optimized_params.get('signal_threshold_buy', 2.0)
    strong_buy_threshold = optimized_params.get('signal_threshold_strong_buy', 3.0)
    very_strong_buy_threshold = optimized_params.get('signal_threshold_very_strong_buy', 4.0)
    
    # Technical Analysis (40% weight)
    technical_score = 0
    
    # Multi-timeframe trend analysis
    sma_5 = indicators.get('sma_5', 0)
    sma_10 = indicators.get('sma_10', 0)
    sma_20 = indicators.get('sma_20', 0)
    sma_50 = indicators.get('sma_50', 0)
    sma_200 = indicators.get('sma_200', 0)
    
    if sma_5 > sma_10 > sma_20 > sma_50 > sma_200:
        technical_score += 4
        signals.append('VERY_STRONG_UPTREND')
    elif sma_5 > sma_10 > sma_20 > sma_50:
        technical_score += 3
        signals.append('STRONG_UPTREND')
    elif sma_5 > sma_10 > sma_20:
        technical_score += 2
        signals.append('UPTREND')
    elif sma_5 < sma_10 < sma_20 < sma_50 < sma_200:
        technical_score -= 4
        signals.append('VERY_STRONG_DOWNTREND')
    elif sma_5 < sma_10 < sma_20 < sma_50:
        technical_score -= 3
        signals.append('STRONG_DOWNTREND')
    elif sma_5 < sma_10 < sma_20:
        technical_score -= 2
        signals.append('DOWNTREND')
    
    # Enhanced RSI analysis
    rsi_14 = indicators.get('rsi_14', 50)
    rsi_21 = indicators.get('rsi_21', 50)
    rsi_50 = indicators.get('rsi_50', 50)
    
    if rsi_14 < 20 and rsi_21 < 25 and rsi_50 < 30:
        technical_score += 3
        signals.append('VERY_OVERSOLD')
    elif rsi_14 < 30 and rsi_21 < 35:
        technical_score += 2
        signals.append('OVERSOLD')
    elif rsi_14 > 80 and rsi_21 > 75 and rsi_50 > 70:
        technical_score -= 3
        signals.append('VERY_OVERBOUGHT')
    elif rsi_14 > 70 and rsi_21 > 65:
        technical_score -= 2
        signals.append('OVERBOUGHT')
    
    # Enhanced MACD analysis
    macd_line = indicators.get('macd_line', 0)
    macd_signal = indicators.get('macd_signal', 0)
    macd_hist = indicators.get('macd_hist', 0)
    
    if macd_line > macd_signal and macd_hist > 0:
        technical_score += 2
        signals.append('MACD_BULLISH')
    elif macd_line < macd_signal and macd_hist < 0:
        technical_score -= 2
        signals.append('MACD_BEARISH')
    
    # Enhanced Bollinger Bands analysis
    bb_upper = indicators.get('bb_upper', 0)
    bb_lower = indicators.get('bb_lower', 0)
    bb_middle = indicators.get('bb_middle', 0)
    current_price = indicators.get('current_price', 0)
    
    if current_price < bb_lower:
        technical_score += 2
        signals.append('BB_OVERSOLD')
    elif current_price > bb_upper:
        technical_score -= 2
        signals.append('BB_OVERBOUGHT')
    elif current_price > bb_middle:
        technical_score += 1
        signals.append('BB_ABOVE_MIDDLE')
    elif current_price < bb_middle:
        technical_score -= 1
        signals.append('BB_BELOW_MIDDLE')
    
    # Enhanced Stochastic analysis
    stoch_k = indicators.get('stoch_k', 50)
    stoch_d = indicators.get('stoch_d', 50)
    
    if stoch_k < 20 and stoch_d < 20:
        technical_score += 2
        signals.append('STOCH_OVERSOLD')
    elif stoch_k > 80 and stoch_d > 80:
        technical_score -= 2
        signals.append('STOCH_OVERBOUGHT')
    
    # Enhanced Williams %R analysis
    williams_r = indicators.get('williams_r', -50)
    
    if williams_r < -80:
        technical_score += 2
        signals.append('WILLIAMS_OVERSOLD')
    elif williams_r > -20:
        technical_score -= 2
        signals.append('WILLIAMS_OVERBOUGHT')
    
    # Enhanced CCI analysis
    cci = indicators.get('cci', 0)
    
    if cci < -100:
        technical_score += 2
        signals.append('CCI_OVERSOLD')
    elif cci > 100:
        technical_score -= 2
        signals.append('CCI_OVERBOUGHT')
    
    # Enhanced price momentum analysis
    price_change_1d = indicators.get('price_change_1d', 0)
    price_change_5d = indicators.get('price_change_5d', 0)
    price_change_20d = indicators.get('price_change_20d', 0)
    
    if price_change_1d > 2 and price_change_5d > 5 and price_change_20d > 10:
        technical_score += 3
        signals.append('STRONG_PRICE_MOMENTUM')
    elif price_change_1d > 1 and price_change_5d > 2:
        technical_score += 2
        signals.append('PRICE_MOMENTUM')
    elif price_change_1d < -2 and price_change_5d < -5 and price_change_20d < -10:
        technical_score -= 3
        signals.append('STRONG_PRICE_DECLINE')
    elif price_change_1d < -1 and price_change_5d < -2:
        technical_score -= 2
        signals.append('PRICE_DECLINE')
    
    # Enhanced trend strength analysis
    trend_strength = indicators.get('trend_strength', 0)
    
    if trend_strength > 2:
        technical_score += 1
        signals.append('STRONG_TREND')
    elif trend_strength < -2:
        technical_score -= 1
        signals.append('WEAK_TREND')
    
    # Enhanced volume analysis
    volume_ratio = indicators.get('volume_ratio', 1.0)
    
    if volume_ratio > 1.5:
        technical_score += 1
        signals.append('HIGH_VOLUME')
    elif volume_ratio < 0.5:
        technical_score -= 1
        signals.append('LOW_VOLUME')
    
    # Enhanced volatility analysis
    volatility_20d = indicators.get('volatility_20d', 0)
    
    if volatility_20d > 3:
        technical_score -= 1
        signals.append('HIGH_VOLATILITY')
    elif volatility_20d < 1:
        technical_score += 1
        signals.append('LOW_VOLATILITY')
    
    # Calculate total score with enhanced weighting
    total_score = technical_score * 0.4  # 40% weight for technical analysis
    
    # Determine action with enhanced thresholds
    if total_score >= very_strong_buy_threshold:
        return 'VERY_STRONG_BUY', signals, total_score
    elif total_score >= strong_buy_threshold:
        return 'STRONG_BUY', signals, total_score
    elif total_score >= buy_threshold:
        return 'BUY', signals, total_score
    elif total_score <= -very_strong_buy_threshold:
        return 'VERY_STRONG_SELL', signals, total_score
    elif total_score <= -strong_buy_threshold:
        return 'STRONG_SELL', signals, total_score
    elif total_score <= -buy_threshold:
        return 'SELL', signals, total_score
    else:
        return 'HOLD', signals, total_score

def calculate_enhanced_position_size(account_balance, signal_strength, current_price, optimized_params):
    """Calculate enhanced position size with optimized parameters"""
    if signal_strength <= 0:
        return 0
    
    # Get optimized parameters
    risk_per_trade = optimized_params.get('risk_per_trade', 0.001)
    max_position_size = optimized_params.get('max_position_size', 0.01)
    
    # Base position size with optimized risk
    base_risk = account_balance * risk_per_trade
    
    # Signal strength adjustment
    if signal_strength >= 4.0:
        strength_multiplier = 2.0
    elif signal_strength >= 3.0:
        strength_multiplier = 1.5
    elif signal_strength >= 2.0:
        strength_multiplier = 1.2
    elif signal_strength >= 1.0:
        strength_multiplier = 1.0
    elif signal_strength >= 0.5:
        strength_multiplier = 0.8
    else:
        strength_multiplier = 0.5
    
    # Calculate final position size
    final_risk = base_risk * strength_multiplier
    
    # Calculate shares
    shares = int(final_risk / current_price) if current_price > 0 else 0
    
    # Limit to max position size
    max_position_value = account_balance * max_position_size
    max_shares = int(max_position_value / current_price) if current_price > 0 else 0
    
    return min(shares, max_shares)

def simulate_optimized_trading(cursor, symbols, account_balance, month, year, portfolio, optimized_params):
    """Simulate optimized trading for one month"""
    print(f"\n   === OPTIMIZED MONTH {month:02d}/{year} ===")
    
    monthly_start_balance = account_balance
    monthly_trades = []
    monthly_pnl = 0
    
    # Trading days in month
    trading_days = 20
    
    for day in range(1, trading_days + 1):
        print(f"     Day {day:2d}: ", end="")
        
        # Select symbol
        symbol = random.choice(symbols)
        
        # Get current price (simulated)
        current_price = random.uniform(1000, 50000)
        
        # Calculate enhanced indicators
        synthetic_prices = [current_price * random.uniform(0.9, 1.1) for _ in range(200)]
        indicators = calculate_enhanced_indicators(synthetic_prices)
        
        # Generate enhanced signals
        action, signals, signal_strength = generate_enhanced_signals(indicators, optimized_params)
        
        # Check if we should close existing positions
        if symbol in portfolio:
            position = portfolio[symbol]
            entry_price = position['entry_price']
            quantity = position['quantity']
            
            # Calculate P&L
            if position['action'] == 'BUY':
                current_pnl = (current_price - entry_price) * quantity
                pnl_percent = (current_price - entry_price) / entry_price * 100
            else:  # SELL
                current_pnl = (entry_price - current_price) * quantity
                pnl_percent = (entry_price - current_price) / entry_price * 100
            
            # Enhanced stop loss and take profit
            stop_loss = optimized_params.get('stop_loss', 0.01) * 100
            take_profit = optimized_params.get('take_profit', 0.03) * 100
            
            if pnl_percent <= -stop_loss or pnl_percent >= take_profit:
                # Close position
                trade_cost = quantity * current_price * 0.001  # 0.1% commission
                monthly_trades.append({
                    'symbol': symbol,
                    'action': 'SELL' if position['action'] == 'BUY' else 'BUY',
                    'quantity': quantity,
                    'price': current_price,
                    'commission': trade_cost,
                    'timestamp': datetime.now()
                })
                
                if position['action'] == 'BUY':
                    account_balance += (quantity * current_price) - trade_cost
                    print(f"CLOSE BUY {quantity} {symbol} @ {current_price:.2f} = +{current_pnl:,.0f}")
                else:
                    account_balance -= (quantity * current_price) + trade_cost
                    print(f"CLOSE SELL {quantity} {symbol} @ {current_price:.2f} = +{current_pnl:,.0f}")
                del portfolio[symbol]
            continue
        
        # Execute new trade if signal is strong enough
        if action in ['BUY', 'STRONG_BUY', 'VERY_STRONG_BUY', 'SELL', 'STRONG_SELL', 'VERY_STRONG_SELL']:
            # Calculate enhanced position size
            quantity = calculate_enhanced_position_size(account_balance, signal_strength, current_price, optimized_params)
            
            if quantity > 0:
                trade_cost = quantity * current_price * 0.001  # 0.1% commission
                monthly_trades.append({
                    'symbol': symbol,
                    'action': action,
                    'quantity': quantity,
                    'price': current_price,
                    'commission': trade_cost,
                    'timestamp': datetime.now()
                })
                
                if action in ['BUY', 'STRONG_BUY', 'VERY_STRONG_BUY']:
                    account_balance -= (quantity * current_price) + trade_cost
                    portfolio[symbol] = {
                        'action': 'BUY',
                        'quantity': quantity,
                        'entry_price': current_price,
                        'entry_date': datetime.now()
                    }
                    print(f"{action} {quantity} {symbol} @ {current_price:.2f} = -{(quantity * current_price) + trade_cost:,.0f}")
                else:  # SELL
                    account_balance += (quantity * current_price) - trade_cost
                    portfolio[symbol] = {
                        'action': 'SELL',
                        'quantity': quantity,
                        'entry_price': current_price,
                        'entry_date': datetime.now()
                    }
                    print(f"{action} {quantity} {symbol} @ {current_price:.2f} = +{(quantity * current_price) - trade_cost:,.0f}")
            else:
                print(f"No position size for {symbol} (strength: {signal_strength:.2f})")
        else:
            print(f"HOLD {symbol} (strength: {signal_strength:.2f})")
    
    monthly_end_balance = account_balance
    monthly_pnl = monthly_end_balance - monthly_start_balance
    monthly_return = (monthly_pnl / monthly_start_balance) * 100 if monthly_start_balance > 0 else 0
    
    print(f"     Monthly P&L: {monthly_pnl:+,.0f} ({monthly_return:+.2f}%)")
    print(f"     Monthly Balance: {monthly_end_balance:,.0f}")
    print(f"     Monthly Trades: {len(monthly_trades)}")
    print(f"     Open Positions: {len(portfolio)}")
    
    return {
        'month': month,
        'start_balance': monthly_start_balance,
        'end_balance': monthly_end_balance,
        'pnl': monthly_pnl,
        'return_pct': monthly_return,
        'trades_count': len(monthly_trades),
        'trades': monthly_trades,
        'portfolio': portfolio.copy()
    }

def main():
    """Main function"""
    db_conn = None
    cursor = None
    results = {}
    start_time = datetime.now()
    
    print("TESTING OPTIMIZED SYSTEM")
    print("=" * 80)
    print(f"Started: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # Optimized parameters
    initial_balance = 10_000_000  # 10 juta
    simulation_year = 2024
    account_balance = initial_balance
    portfolio = {}  # Track open positions
    
    print(f"Initial Balance: Rp {initial_balance:,}")
    print(f"Simulation Year: {simulation_year}")
    print("=" * 80)
    
    try:
        db_conn = get_db_connection()
        cursor = db_conn.cursor()
        print("[PASS] Database connection established")
        
        # Load optimized parameters
        optimized_params = load_optimized_parameters(cursor)
        if not optimized_params:
            print("[ERROR] Could not load optimized parameters")
            return
        
        print(f"[INFO] Using optimized parameters:")
        for param, value in optimized_params.items():
            print(f"  {param}: {value}")
        
        # Get trading symbols
        symbols = get_trading_symbols(cursor)
        if not symbols:
            print("[ERROR] No trading symbols found")
            return
        
        print(f"[INFO] Using {len(symbols)} symbols for optimized trading")
        
        # Monthly results storage
        monthly_results = []
        total_trades = 0
        total_commission = 0
        
        # Simulate 12 months with optimized parameters
        for month in range(1, 13):
            print(f"\nOPTIMIZED MONTH {month:02d}/{simulation_year}")
            print("-" * 60)
            
            month_result = simulate_optimized_trading(cursor, symbols, account_balance, month, simulation_year, portfolio, optimized_params)
            monthly_results.append(month_result)
            
            # Update account balance and portfolio
            account_balance = month_result['end_balance']
            portfolio = month_result['portfolio']
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
            print(f"       Open Positions: {len(portfolio)}")
        
        # Calculate optimized results
        final_balance = account_balance
        total_pnl = final_balance - initial_balance
        total_return = (total_pnl / initial_balance) * 100
        
        # Calculate monthly averages
        monthly_returns = [result['return_pct'] for result in monthly_results]
        avg_monthly_return = sum(monthly_returns) / len(monthly_returns)
        
        # Calculate best and worst months
        best_month = max(monthly_results, key=lambda x: x['return_pct'])
        worst_month = min(monthly_results, key=lambda x: x['return_pct'])
        
        # Calculate Sharpe ratio
        if len(monthly_returns) > 1:
            monthly_std = math.sqrt(sum([(r - avg_monthly_return) ** 2 for r in monthly_returns]) / (len(monthly_returns) - 1))
            sharpe_ratio = avg_monthly_return / monthly_std if monthly_std > 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate win rate
        profitable_months = sum(1 for r in monthly_returns if r > 0)
        win_rate = (profitable_months / len(monthly_returns)) * 100
        
        # Generate optimized results
        results = {
            'simulation_period': f"1 year ({simulation_year}) - OPTIMIZED",
            'initial_balance': initial_balance,
            'final_balance': final_balance,
            'total_pnl': total_pnl,
            'total_return_pct': total_return,
            'avg_monthly_return': avg_monthly_return,
            'total_trades': total_trades,
            'total_commission': total_commission,
            'win_rate': win_rate,
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
            'monthly_results': monthly_results,
            'final_portfolio': portfolio,
            'optimized_parameters': optimized_params
        }
        
        # Display optimized results
        print("\n" + "=" * 80)
        print("OPTIMIZED TRADING SIMULATION RESULTS")
        print("=" * 80)
        print(f"Simulation Period: 1 year ({simulation_year}) - OPTIMIZED")
        print(f"Initial Balance: Rp {initial_balance:,}")
        print(f"Final Balance: Rp {final_balance:,}")
        print(f"Total P&L: Rp {total_pnl:+,}")
        print(f"Total Return: {total_return:+.2f}%")
        print(f"Average Monthly Return: {avg_monthly_return:+.2f}%")
        print(f"Total Trades: {total_trades}")
        print(f"Total Commission: Rp {total_commission:,.0f}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Best Month: {best_month['month']:02d} ({best_month['return_pct']:+.2f}%)")
        print(f"Worst Month: {worst_month['month']:02d} ({worst_month['return_pct']:+.2f}%)")
        print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"Final Open Positions: {len(portfolio)}")
        
        print("\nOPTIMIZED MONTHLY BREAKDOWN:")
        print("-" * 80)
        for result in monthly_results:
            print(f"Month {result['month']:02d}: {result['return_pct']:+6.2f}% | "
                  f"P&L: Rp {result['pnl']:+8,.0f} | "
                  f"Balance: Rp {result['end_balance']:8,.0f} | "
                  f"Trades: {result['trades_count']:3d} | "
                  f"Positions: {len(result['portfolio']):2d}")
        
        # Performance analysis
        print("\nOPTIMIZED PERFORMANCE ANALYSIS:")
        print("-" * 80)
        if total_return > 0:
            print("[PASS] PROFITABLE OPTIMIZED TRADING")
            print(f"   Annual Return: {total_return:.2f}%")
            print(f"   Monthly Average: {avg_monthly_return:.2f}%")
            print(f"   Win Rate: {win_rate:.1f}%")
        else:
            print("[FAIL] LOSS-MAKING OPTIMIZED TRADING")
            print(f"   Annual Loss: {total_return:.2f}%")
            print(f"   Monthly Average: {avg_monthly_return:.2f}%")
            print(f"   Win Rate: {win_rate:.1f}%")
        
        if sharpe_ratio > 1:
            print("[PASS] EXCELLENT RISK-ADJUSTED RETURNS")
        elif sharpe_ratio > 0.5:
            print("[PASS] GOOD RISK-ADJUSTED RETURNS")
        elif sharpe_ratio > 0:
            print("[WARN] MODERATE RISK-ADJUSTED RETURNS")
        else:
            print("[FAIL] POOR RISK-ADJUSTED RETURNS")
        
        # Save results
        end_time = datetime.now()
        file_timestamp = end_time.strftime("%Y%m%d_%H%M%S")
        output_filename = f"optimized_system_test_{file_timestamp}.json"
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=4, default=str)
        
        print(f"\nResults saved to: {output_filename}")
        print(f"Optimized system test completed at: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
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
