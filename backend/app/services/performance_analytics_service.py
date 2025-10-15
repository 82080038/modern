"""
Advanced Performance Analytics Service
Implementasi metrik performa trading profesional
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.trading import Trade, Portfolio, RiskMetrics
from app.models.market_data import HistoricalData
import logging

logger = logging.getLogger(__name__)

class PerformanceAnalyticsService:
    """Service untuk advanced performance analytics"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sharpe Ratio"""
        try:
            if not returns or len(returns) < 2:
                return 0.0
            
            returns_array = np.array(returns)
            excess_returns = returns_array - risk_free_rate / 252  # Daily risk-free rate
            
            if np.std(excess_returns) == 0:
                return 0.0
            
            sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)
            return round(sharpe_ratio, 4)
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return 0.0
    
    def calculate_sortino_ratio(self, returns: List[float], target_return: float = 0.0) -> float:
        """Calculate Sortino Ratio"""
        try:
            if not returns or len(returns) < 2:
                return 0.0
            
            returns_array = np.array(returns)
            excess_returns = returns_array - target_return / 252
            
            # Only consider negative returns for downside deviation
            negative_returns = excess_returns[excess_returns < 0]
            
            if len(negative_returns) == 0 or np.std(negative_returns) == 0:
                return 0.0
            
            sortino_ratio = np.mean(excess_returns) / np.std(negative_returns) * np.sqrt(252)
            return round(sortino_ratio, 4)
            
        except Exception as e:
            logger.error(f"Error calculating Sortino ratio: {e}")
            return 0.0
    
    def calculate_calmar_ratio(self, returns: List[float], max_drawdown: float) -> float:
        """Calculate Calmar Ratio"""
        try:
            if not returns or max_drawdown == 0:
                return 0.0
            
            annual_return = np.mean(returns) * 252
            calmar_ratio = annual_return / abs(max_drawdown)
            return round(calmar_ratio, 4)
            
        except Exception as e:
            logger.error(f"Error calculating Calmar ratio: {e}")
            return 0.0
    
    def calculate_information_ratio(self, portfolio_returns: List[float], benchmark_returns: List[float]) -> float:
        """Calculate Information Ratio"""
        try:
            if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
                return 0.0
            
            portfolio_array = np.array(portfolio_returns)
            benchmark_array = np.array(benchmark_returns)
            
            active_returns = portfolio_array - benchmark_array
            tracking_error = np.std(active_returns)
            
            if tracking_error == 0:
                return 0.0
            
            information_ratio = np.mean(active_returns) / tracking_error * np.sqrt(252)
            return round(information_ratio, 4)
            
        except Exception as e:
            logger.error(f"Error calculating Information ratio: {e}")
            return 0.0
    
    def calculate_treynor_ratio(self, returns: List[float], beta: float) -> float:
        """Calculate Treynor Ratio"""
        try:
            if not returns or beta == 0:
                return 0.0
            
            annual_return = np.mean(returns) * 252
            risk_free_rate = 0.02
            excess_return = annual_return - risk_free_rate
            
            treynor_ratio = excess_return / beta
            return round(treynor_ratio, 4)
            
        except Exception as e:
            logger.error(f"Error calculating Treynor ratio: {e}")
            return 0.0
    
    def calculate_jensen_alpha(self, portfolio_returns: List[float], benchmark_returns: List[float], beta: float) -> float:
        """Calculate Jensen's Alpha"""
        try:
            if len(portfolio_returns) != len(benchmark_returns) or len(portfolio_returns) < 2:
                return 0.0
            
            portfolio_array = np.array(portfolio_returns)
            benchmark_array = np.array(benchmark_returns)
            
            portfolio_mean = np.mean(portfolio_array)
            benchmark_mean = np.mean(benchmark_array)
            risk_free_rate = 0.02 / 252  # Daily risk-free rate
            
            jensen_alpha = (portfolio_mean - risk_free_rate) - beta * (benchmark_mean - risk_free_rate)
            return round(jensen_alpha * 252, 4)  # Annualized
            
        except Exception as e:
            logger.error(f"Error calculating Jensen's alpha: {e}")
            return 0.0
    
    def calculate_maximum_drawdown(self, returns: List[float]) -> Dict:
        """Calculate Maximum Drawdown"""
        try:
            if not returns:
                return {"max_drawdown": 0.0, "max_drawdown_duration": 0, "recovery_time": 0}
            
            returns_array = np.array(returns)
            cumulative_returns = np.cumprod(1 + returns_array)
            running_max = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - running_max) / running_max
            
            max_drawdown = np.min(drawdown)
            max_drawdown_idx = np.argmin(drawdown)
            
            # Calculate drawdown duration
            drawdown_duration = 0
            recovery_time = 0
            
            if max_drawdown_idx < len(drawdown) - 1:
                # Find when drawdown started
                start_idx = max_drawdown_idx
                while start_idx > 0 and drawdown[start_idx] < 0:
                    start_idx -= 1
                
                # Find when drawdown ended
                end_idx = max_drawdown_idx
                while end_idx < len(drawdown) - 1 and drawdown[end_idx] < 0:
                    end_idx += 1
                
                drawdown_duration = end_idx - start_idx
                recovery_time = end_idx - max_drawdown_idx
            
            return {
                "max_drawdown": round(max_drawdown, 4),
                "max_drawdown_duration": drawdown_duration,
                "recovery_time": recovery_time,
                "max_drawdown_date": max_drawdown_idx
            }
            
        except Exception as e:
            logger.error(f"Error calculating maximum drawdown: {e}")
            return {"max_drawdown": 0.0, "max_drawdown_duration": 0, "recovery_time": 0}
    
    def calculate_win_rate(self, trades: List[Dict]) -> Dict:
        """Calculate Win Rate and Trade Statistics"""
        try:
            if not trades:
                return {
                    "win_rate": 0.0,
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "average_win": 0.0,
                    "average_loss": 0.0,
                    "profit_factor": 0.0,
                    "expectancy": 0.0
                }
            
            winning_trades = [t for t in trades if t.get('pnl', 0) > 0]
            losing_trades = [t for t in trades if t.get('pnl', 0) < 0]
            
            total_trades = len(trades)
            winning_count = len(winning_trades)
            losing_count = len(losing_trades)
            
            win_rate = (winning_count / total_trades * 100) if total_trades > 0 else 0.0
            
            average_win = np.mean([t['pnl'] for t in winning_trades]) if winning_trades else 0.0
            average_loss = np.mean([t['pnl'] for t in losing_trades]) if losing_trades else 0.0
            
            total_wins = sum([t['pnl'] for t in winning_trades]) if winning_trades else 0.0
            total_losses = abs(sum([t['pnl'] for t in losing_trades])) if losing_trades else 0.0
            
            profit_factor = (total_wins / total_losses) if total_losses > 0 else 0.0
            expectancy = (win_rate / 100 * average_win) - ((100 - win_rate) / 100 * abs(average_loss))
            
            return {
                "win_rate": round(win_rate, 2),
                "total_trades": total_trades,
                "winning_trades": winning_count,
                "losing_trades": losing_count,
                "average_win": round(average_win, 2),
                "average_loss": round(average_loss, 2),
                "profit_factor": round(profit_factor, 2),
                "expectancy": round(expectancy, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating win rate: {e}")
            return {"win_rate": 0.0, "total_trades": 0, "winning_trades": 0, "losing_trades": 0}
    
    def calculate_value_at_risk(self, returns: List[float], confidence_level: float = 0.05) -> Dict:
        """Calculate Value at Risk (VaR)"""
        try:
            if not returns or len(returns) < 2:
                return {"var_1d": 0.0, "var_1w": 0.0, "var_1m": 0.0}
            
            returns_array = np.array(returns)
            
            # Historical VaR
            var_1d = np.percentile(returns_array, confidence_level * 100)
            var_1w = var_1d * np.sqrt(5)  # Weekly VaR
            var_1m = var_1d * np.sqrt(21)  # Monthly VaR
            
            # Parametric VaR (assuming normal distribution)
            mean_return = np.mean(returns_array)
            std_return = np.std(returns_array)
            
            from scipy.stats import norm
            z_score = norm.ppf(confidence_level)
            parametric_var_1d = mean_return + z_score * std_return
            
            return {
                "var_1d": round(var_1d, 4),
                "var_1w": round(var_1w, 4),
                "var_1m": round(var_1m, 4),
                "parametric_var_1d": round(parametric_var_1d, 4),
                "confidence_level": confidence_level
            }
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return {"var_1d": 0.0, "var_1w": 0.0, "var_1m": 0.0}
    
    def calculate_conditional_var(self, returns: List[float], confidence_level: float = 0.05) -> float:
        """Calculate Conditional Value at Risk (CVaR)"""
        try:
            if not returns or len(returns) < 2:
                return 0.0
            
            returns_array = np.array(returns)
            var_threshold = np.percentile(returns_array, confidence_level * 100)
            
            # CVaR is the mean of returns below VaR threshold
            tail_returns = returns_array[returns_array <= var_threshold]
            cvar = np.mean(tail_returns) if len(tail_returns) > 0 else 0.0
            
            return round(cvar, 4)
            
        except Exception as e:
            logger.error(f"Error calculating CVaR: {e}")
            return 0.0
    
    def get_comprehensive_performance_metrics(self, portfolio_id: int, start_date: datetime, end_date: datetime) -> Dict:
        """Get comprehensive performance metrics untuk portfolio"""
        try:
            # Get trades for portfolio
            trades = self.db.query(Trade).filter(
                Trade.portfolio_id == portfolio_id,
                Trade.created_at >= start_date,
                Trade.created_at <= end_date
            ).all()
            
            if not trades:
                return {"error": "No trades found for the specified period"}
            
            # Convert trades to returns
            trade_data = []
            for trade in trades:
                trade_data.append({
                    'pnl': trade.realized_pnl or 0,
                    'date': trade.created_at,
                    'symbol': trade.symbol
                })
            
            # Calculate daily returns
            daily_returns = []
            for i in range(1, len(trade_data)):
                if trade_data[i-1]['pnl'] != 0:
                    daily_return = (trade_data[i]['pnl'] - trade_data[i-1]['pnl']) / abs(trade_data[i-1]['pnl'])
                    daily_returns.append(daily_return)
            
            # Calculate all metrics
            sharpe_ratio = self.calculate_sharpe_ratio(daily_returns)
            sortino_ratio = self.calculate_sortino_ratio(daily_returns)
            max_drawdown_info = self.calculate_maximum_drawdown(daily_returns)
            win_rate_info = self.calculate_win_rate(trade_data)
            var_info = self.calculate_value_at_risk(daily_returns)
            cvar = self.calculate_conditional_var(daily_returns)
            
            # Calculate Calmar ratio
            calmar_ratio = self.calculate_calmar_ratio(daily_returns, max_drawdown_info['max_drawdown'])
            
            return {
                "portfolio_id": portfolio_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "risk_metrics": {
                    "sharpe_ratio": sharpe_ratio,
                    "sortino_ratio": sortino_ratio,
                    "calmar_ratio": calmar_ratio,
                    "max_drawdown": max_drawdown_info['max_drawdown'],
                    "max_drawdown_duration": max_drawdown_info['max_drawdown_duration'],
                    "recovery_time": max_drawdown_info['recovery_time']
                },
                "trade_metrics": win_rate_info,
                "var_metrics": var_info,
                "cvar": cvar,
                "total_trades": len(trades),
                "total_pnl": sum([t.realized_pnl or 0 for t in trades])
            }
            
        except Exception as e:
            logger.error(f"Error calculating comprehensive performance metrics: {e}")
            return {"error": str(e)}
