"""
Simple Trading System
=====================

Sistem trading simulation sederhana tanpa emoji untuk kompatibilitas Windows.

Author: AI Assistant
Date: 2025-01-17
"""

import asyncio
import logging
import sys
import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import json
import yfinance as yf

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleTradingSystem:
    """
    Simple Trading System dengan modal calculation dan historical data
    """
    
    def __init__(self, db_path: str = "trading_data.db"):
        self.db_path = db_path
        self.initial_capital = 100000  # $100,000 initial capital
        self.current_capital = self.initial_capital
        self.portfolio = {}
        self.trade_history = []
        self.performance_metrics = {}
        
        # Trading parameters
        self.risk_per_trade = 0.02  # 2% risk per trade
        self.max_position_size = 0.1  # 10% max position size
        self.stop_loss = 0.05  # 5% stop loss
        self.take_profit = 0.15  # 15% take profit
        
    async def run_trading_simulation(self, 
                                   start_date: str = "2023-01-01", 
                                   end_date: str = "2024-12-31",
                                   symbols: List[str] = None) -> Dict[str, Any]:
        """Run trading simulation"""
        try:
            print("Starting Simple Trading System...")
            print("=" * 60)
            
            # Set default symbols
            if not symbols:
                symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
            
            # Step 1: Load historical data
            print("\nStep 1: Loading Historical Data...")
            historical_data = await self._load_historical_data(symbols, start_date, end_date)
            if not historical_data:
                return {'error': 'Failed to load historical data'}
            
            # Step 2: Calculate portfolio allocation
            print("\nStep 2: Calculating Portfolio Allocation...")
            portfolio_allocation = await self._calculate_portfolio_allocation(symbols, historical_data)
            
            # Step 3: Run trading simulation
            print("\nStep 3: Running Trading Simulation...")
            trading_results = await self._run_trading_simulation(historical_data, portfolio_allocation)
            
            # Step 4: Calculate performance metrics
            print("\nStep 4: Calculating Performance Metrics...")
            performance = await self._calculate_performance_metrics(trading_results)
            
            # Step 5: Generate report
            print("\nStep 5: Generating Trading Report...")
            report = await self._generate_trading_report(trading_results, performance)
            
            print("\n" + "=" * 60)
            print("Trading Simulation Completed!")
            print("=" * 60)
            
            return report
            
        except Exception as e:
            logger.error(f"Error in trading simulation: {e}")
            return {'error': str(e)}
    
    async def _load_historical_data(self, symbols: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
        """Load historical data from Yahoo Finance"""
        try:
            historical_data = {}
            
            for symbol in symbols:
                print(f"Loading data for {symbol}...")
                
                try:
                    ticker = yf.Ticker(symbol)
                    data = ticker.history(start=start_date, end=end_date)
                    
                    if not data.empty:
                        # Convert to standard format
                        data = data.reset_index()
                        data.columns = ['date', 'open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits']
                        data['symbol'] = symbol
                        historical_data[symbol] = data
                        print(f"Loaded {len(data)} records for {symbol}")
                    else:
                        print(f"No data available for {symbol}")
                except Exception as e:
                    print(f"Error loading {symbol}: {e}")
                    continue
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            return {}
    
    async def _calculate_portfolio_allocation(self, symbols: List[str], historical_data: Dict[str, pd.DataFrame]) -> Dict[str, float]:
        """Calculate optimal portfolio allocation"""
        try:
            # Calculate returns for each symbol
            returns_data = {}
            for symbol, data in historical_data.items():
                if len(data) > 1:
                    returns = data['close'].pct_change().dropna()
                    returns_data[symbol] = returns
            
            if not returns_data:
                # Equal weight allocation if no data
                equal_weight = 1.0 / len(symbols)
                return {symbol: equal_weight for symbol in symbols}
            
            # Calculate mean returns and volatility
            portfolio_allocation = {}
            volatilities = {}
            
            for symbol in symbols:
                if symbol in returns_data:
                    volatility = returns_data[symbol].std()
                    volatilities[symbol] = volatility
            
            # Inverse volatility weighting (lower volatility = higher allocation)
            if volatilities:
                total_inverse_vol = sum(1.0 / vol for vol in volatilities.values())
                for symbol in symbols:
                    if symbol in volatilities:
                        portfolio_allocation[symbol] = (1.0 / volatilities[symbol]) / total_inverse_vol
                    else:
                        portfolio_allocation[symbol] = 1.0 / len(symbols)
            else:
                # Equal weight allocation
                equal_weight = 1.0 / len(symbols)
                for symbol in symbols:
                    portfolio_allocation[symbol] = equal_weight
            
            print("Portfolio allocation calculated:")
            for symbol, allocation in portfolio_allocation.items():
                print(f"  {symbol}: {allocation:.2%}")
            
            return portfolio_allocation
            
        except Exception as e:
            logger.error(f"Error calculating portfolio allocation: {e}")
            # Return equal weight allocation as fallback
            equal_weight = 1.0 / len(symbols)
            return {symbol: equal_weight for symbol in symbols}
    
    async def _run_trading_simulation(self, 
                                    historical_data: Dict[str, pd.DataFrame], 
                                    portfolio_allocation: Dict[str, float]) -> Dict[str, Any]:
        """Run trading simulation"""
        try:
            # Initialize trading state
            self.current_capital = self.initial_capital
            self.portfolio = {}
            self.trade_history = []
            
            # Get all trading dates
            all_dates = set()
            for symbol, data in historical_data.items():
                all_dates.update(data['date'].dt.date)
            
            trading_dates = sorted(list(all_dates))
            
            print(f"Running simulation for {len(trading_dates)} trading days...")
            
            # Process each trading day
            for i, date in enumerate(trading_dates):
                if i % 50 == 0:  # Progress update every 50 days
                    print(f"Processing day {i+1}/{len(trading_dates)}: {date}")
                
                # Get current prices for all symbols
                current_prices = {}
                for symbol, data in historical_data.items():
                    day_data = data[data['date'].dt.date == date]
                    if not day_data.empty:
                        current_prices[symbol] = day_data['close'].iloc[0]
                
                # Execute trading logic
                await self._execute_trading_logic(date, current_prices, portfolio_allocation)
            
            # Calculate final portfolio value
            final_portfolio_value = self.current_capital
            for symbol, shares in self.portfolio.items():
                if symbol in historical_data:
                    last_data = historical_data[symbol].iloc[-1]
                    final_portfolio_value += shares * last_data['close']
            
            return {
                'initial_capital': self.initial_capital,
                'final_portfolio_value': final_portfolio_value,
                'total_return': (final_portfolio_value - self.initial_capital) / self.initial_capital,
                'portfolio': self.portfolio,
                'trade_history': self.trade_history,
                'trading_days': len(trading_dates)
            }
            
        except Exception as e:
            logger.error(f"Error in trading simulation: {e}")
            return {'error': str(e)}
    
    async def _execute_trading_logic(self, 
                                   date: datetime.date, 
                                   current_prices: Dict[str, float], 
                                   portfolio_allocation: Dict[str, float]):
        """Execute trading logic for a specific date"""
        try:
            # Calculate target portfolio value
            total_portfolio_value = self.current_capital
            for symbol, shares in self.portfolio.items():
                if symbol in current_prices:
                    total_portfolio_value += shares * current_prices[symbol]
            
            # Rebalance portfolio
            for symbol, target_allocation in portfolio_allocation.items():
                if symbol in current_prices:
                    target_value = total_portfolio_value * target_allocation
                    current_shares = self.portfolio.get(symbol, 0)
                    current_value = current_shares * current_prices[symbol]
                    
                    # Calculate position adjustment
                    value_difference = target_value - current_value
                    
                    if abs(value_difference) > 100:  # Minimum trade size
                        shares_to_trade = value_difference / current_prices[symbol]
                        
                        if shares_to_trade > 0:  # Buy
                            # Check if we have enough capital
                            trade_value = shares_to_trade * current_prices[symbol]
                            if trade_value <= self.current_capital:
                                self.current_capital -= trade_value
                                self.portfolio[symbol] = self.portfolio.get(symbol, 0) + shares_to_trade
                                
                                self.trade_history.append({
                                    'date': date,
                                    'symbol': symbol,
                                    'action': 'BUY',
                                    'shares': shares_to_trade,
                                    'price': current_prices[symbol],
                                    'value': trade_value,
                                    'capital_remaining': self.current_capital
                                })
                        
                        elif shares_to_trade < 0:  # Sell
                            shares_to_sell = min(abs(shares_to_trade), self.portfolio.get(symbol, 0))
                            if shares_to_sell > 0:
                                trade_value = shares_to_sell * current_prices[symbol]
                                self.current_capital += trade_value
                                self.portfolio[symbol] = self.portfolio.get(symbol, 0) - shares_to_sell
                                
                                self.trade_history.append({
                                    'date': date,
                                    'symbol': symbol,
                                    'action': 'SELL',
                                    'shares': shares_to_sell,
                                    'price': current_prices[symbol],
                                    'value': trade_value,
                                    'capital_remaining': self.current_capital
                                })
            
        except Exception as e:
            logger.error(f"Error executing trading logic: {e}")
    
    async def _calculate_performance_metrics(self, trading_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate performance metrics"""
        try:
            if 'error' in trading_results:
                return {'error': trading_results['error']}
            
            initial_capital = trading_results['initial_capital']
            final_value = trading_results['final_portfolio_value']
            total_return = trading_results['total_return']
            
            # Calculate additional metrics
            trade_history = trading_results['trade_history']
            
            # Calculate win rate
            profitable_trades = 0
            total_trades = len(trade_history)
            
            # Calculate Sharpe ratio (simplified)
            sharpe_ratio = 0  # Simplified calculation
            
            # Calculate max drawdown (simplified)
            max_drawdown = 0  # Simplified calculation
            
            metrics = {
                'initial_capital': initial_capital,
                'final_value': final_value,
                'total_return': total_return,
                'total_return_percentage': total_return * 100,
                'total_trades': total_trades,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'win_rate': profitable_trades / total_trades if total_trades > 0 else 0
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {'error': str(e)}
    
    async def _generate_trading_report(self, 
                                     trading_results: Dict[str, Any], 
                                     performance: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive trading report"""
        try:
            if 'error' in trading_results:
                return trading_results
            
            # Generate summary
            report = {
                'trading_summary': {
                    'simulation_period': '2023-01-01 to 2024-12-31',
                    'initial_capital': f"${trading_results['initial_capital']:,.2f}",
                    'final_portfolio_value': f"${trading_results['final_portfolio_value']:,.2f}",
                    'total_return': f"${trading_results['final_portfolio_value'] - trading_results['initial_capital']:,.2f}",
                    'total_return_percentage': f"{trading_results['total_return'] * 100:.2f}%",
                    'total_trades': len(trading_results['trade_history']),
                    'trading_days': trading_results['trading_days']
                },
                'performance_metrics': performance,
                'portfolio_composition': self._analyze_portfolio_composition(trading_results['portfolio']),
                'trade_analysis': self._analyze_trades(trading_results['trade_history']),
                'risk_analysis': self._analyze_risk_metrics(trading_results),
                'recommendations': self._generate_recommendations(trading_results, performance)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating trading report: {e}")
            return {'error': str(e)}
    
    def _analyze_portfolio_composition(self, portfolio: Dict[str, float]) -> Dict[str, Any]:
        """Analyze portfolio composition"""
        try:
            total_value = sum(portfolio.values())
            composition = {}
            
            for symbol, shares in portfolio.items():
                if shares > 0:
                    composition[symbol] = {
                        'shares': shares,
                        'percentage': (shares / total_value * 100) if total_value > 0 else 0
                    }
            
            return {
                'total_positions': len([s for s in portfolio.values() if s > 0]),
                'composition': composition
            }
            
        except Exception as e:
            logger.error(f"Error analyzing portfolio composition: {e}")
            return {}
    
    def _analyze_trades(self, trade_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trading activity"""
        try:
            if not trade_history:
                return {'total_trades': 0}
            
            buy_trades = [t for t in trade_history if t['action'] == 'BUY']
            sell_trades = [t for t in trade_history if t['action'] == 'SELL']
            
            total_buy_value = sum(t['value'] for t in buy_trades)
            total_sell_value = sum(t['value'] for t in sell_trades)
            
            return {
                'total_trades': len(trade_history),
                'buy_trades': len(buy_trades),
                'sell_trades': len(sell_trades),
                'total_buy_value': total_buy_value,
                'total_sell_value': total_sell_value,
                'net_trading_activity': total_sell_value - total_buy_value
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trades: {e}")
            return {}
    
    def _analyze_risk_metrics(self, trading_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze risk metrics"""
        try:
            # Simplified risk analysis
            return {
                'portfolio_diversification': 'Good' if len(trading_results['portfolio']) > 3 else 'Limited',
                'risk_level': 'Medium',
                'volatility': 'Moderate'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing risk metrics: {e}")
            return {}
    
    def _generate_recommendations(self, 
                                trading_results: Dict[str, Any], 
                                performance: Dict[str, Any]) -> List[str]:
        """Generate trading recommendations"""
        try:
            recommendations = []
            
            total_return = trading_results['total_return']
            
            if total_return > 0.2:  # 20% return
                recommendations.append("Excellent performance! Consider increasing position sizes.")
            elif total_return > 0.1:  # 10% return
                recommendations.append("Good performance. Current strategy is working well.")
            elif total_return > 0:  # Positive return
                recommendations.append("Positive returns achieved. Consider optimizing strategy.")
            else:
                recommendations.append("Negative returns. Review and adjust trading strategy.")
            
            if len(trading_results['trade_history']) < 10:
                recommendations.append("Low trading activity. Consider more frequent rebalancing.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []

async def main():
    """Main function untuk menjalankan trading simulation"""
    try:
        trading_system = SimpleTradingSystem()
        
        # Run trading simulation
        results = await trading_system.run_trading_simulation(
            start_date="2023-01-01",
            end_date="2024-12-31",
            symbols=['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
        )
        
        if 'error' in results:
            print(f"\nError: {results['error']}")
            return results
        
        # Display results
        print("\nTRADING SIMULATION RESULTS:")
        print("=" * 60)
        
        summary = results['trading_summary']
        print(f"Initial Capital: {summary['initial_capital']}")
        print(f"Final Portfolio Value: {summary['final_portfolio_value']}")
        print(f"Total Return: {summary['total_return']}")
        print(f"Total Return Percentage: {summary['total_return_percentage']}")
        print(f"Total Trades: {summary['total_trades']}")
        print(f"Trading Days: {summary['trading_days']}")
        
        print("\nPERFORMANCE METRICS:")
        metrics = results['performance_metrics']
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        
        print("\nPORTFOLIO COMPOSITION:")
        composition = results['portfolio_composition']
        print(f"Total Positions: {composition['total_positions']}")
        for symbol, data in composition['composition'].items():
            print(f"  {symbol}: {data['shares']:.2f} shares ({data['percentage']:.2f}%)")
        
        print("\nRECOMMENDATIONS:")
        for recommendation in results['recommendations']:
            print(f"- {recommendation}")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    asyncio.run(main())
