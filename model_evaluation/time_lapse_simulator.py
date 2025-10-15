"""
Time Lapse Simulator untuk Model Evaluation
Simulasi 1 hari = 2 detik, menampilkan seluruh flow modul dari input sampai output
"""

import time
import json
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
import sqlite3
from pathlib import Path
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from database_integration import DatabaseIntegration

@dataclass
class ModuleStatus:
    """Status modul dalam simulasi"""
    module_name: str
    status: str  # 'idle', 'processing', 'completed', 'error'
    start_time: datetime
    end_time: Optional[datetime]
    processing_time: float
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    performance_metrics: Dict[str, float]
    error_message: Optional[str] = None

@dataclass
class TradingDecision:
    """Keputusan trading"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    quantity: int
    price: float
    timestamp: datetime
    reason: str
    confidence: float

@dataclass
class TradingHistory:
    """History trading"""
    trades: List[TradingDecision]
    total_capital: float
    current_capital: float
    total_pnl: float
    daily_pnl: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int

@dataclass
class TradingSession:
    """Sesi trading harian"""
    date: datetime
    session_id: str
    modules_status: Dict[str, ModuleStatus]
    overall_performance: Dict[str, float]
    recommendations: List[str]
    trading_decisions: List[TradingDecision]
    trading_history: TradingHistory

class TimeLapseSimulator:
    """Simulator time-lapse untuk model evaluation"""
    
    def __init__(self, db_path: str = "time_lapse.db"):
        self.db_path = db_path
        self.modules = self.initialize_modules()
        self.sessions = []
        self.current_session = None
        self.simulation_running = False
        self.time_multiplier = 1  # 1 hari = 2 detik
        self.start_date = None
        self.end_date = None
        self.current_date = None
        self.initial_capital = 100000000.0  # Modal awal Rp 100,000,000
        self.current_capital = self.initial_capital
        self.total_pnl = 0.0
        self.setup_database()
        
        # Database integration
        self.db = DatabaseIntegration()
        self.indonesia_stocks = self.db.get_indonesia_stocks()
        print(f"Loaded {len(self.indonesia_stocks)} Indonesian stocks from database")
        
    def initialize_modules(self):
        """Initialize semua modul berdasarkan dokumentasi"""
        return {
            'market_data': {
                'name': 'Market Data Module',
                'description': 'Real-time market data collection',
                'dependencies': [],
                'outputs': ['price_data', 'volume_data', 'market_status'],
                'processing_time': 0.1,  # 0.1 detik dalam simulasi
                'success_rate': 0.99
            },
            'technical_analysis': {
                'name': 'Technical Analysis Module',
                'description': 'Technical indicators and signals',
                'dependencies': ['market_data'],
                'outputs': ['technical_signals', 'indicators'],
                'processing_time': 0.3,
                'success_rate': 0.95
            },
            'fundamental_analysis': {
                'name': 'Fundamental Analysis Module',
                'description': 'Financial metrics and ratios',
                'dependencies': ['market_data'],
                'outputs': ['financial_metrics', 'ratios'],
                'processing_time': 0.4,
                'success_rate': 0.90
            },
            'sentiment_analysis': {
                'name': 'Sentiment Analysis Module',
                'description': 'News and social media sentiment',
                'dependencies': ['market_data'],
                'outputs': ['sentiment_scores', 'news_data'],
                'processing_time': 0.5,
                'success_rate': 0.90
            },
            'strategy_builder': {
                'name': 'Strategy Builder Module',
                'description': 'Trading strategy creation',
                'dependencies': ['technical_analysis', 'fundamental_analysis', 'sentiment_analysis'],
                'outputs': ['trading_strategy', 'rules'],
                'processing_time': 0.6,
                'success_rate': 0.90
            },
            'algorithmic_trading': {
                'name': 'Algorithmic Trading Module',
                'description': 'Automated trading execution',
                'dependencies': ['strategy_builder'],
                'outputs': ['trade_signals', 'orders'],
                'processing_time': 0.2,
                'success_rate': 0.88
            },
            'risk_management': {
                'name': 'Risk Management Module',
                'description': 'Risk assessment and limits',
                'dependencies': ['algorithmic_trading'],
                'outputs': ['risk_assessment', 'position_sizing'],
                'processing_time': 0.3,
                'success_rate': 0.92
            },
            'trading': {
                'name': 'Trading Module',
                'description': 'Order execution and management',
                'dependencies': ['risk_management'],
                'outputs': ['executed_trades', 'positions'],
                'processing_time': 0.4,
                'success_rate': 0.95
            },
            'performance_analytics': {
                'name': 'Performance Analytics Module',
                'description': 'Performance metrics calculation',
                'dependencies': ['trading'],
                'outputs': ['performance_metrics', 'analytics'],
                'processing_time': 0.5,
                'success_rate': 0.90
            },
            'portfolio_heatmap': {
                'name': 'Portfolio Heat Map Module',
                'description': 'Portfolio visualization',
                'dependencies': ['performance_analytics'],
                'outputs': ['heatmap_data', 'correlations'],
                'processing_time': 0.3,
                'success_rate': 0.87
            },
            'notifications': {
                'name': 'Notifications Module',
                'description': 'Alert and notification system',
                'dependencies': ['portfolio_heatmap'],
                'outputs': ['alerts', 'notifications'],
                'processing_time': 0.1,
                'success_rate': 0.99
            },
            'backtesting': {
                'name': 'Backtesting Module',
                'description': 'Strategy backtesting',
                'dependencies': ['strategy_builder'],
                'outputs': ['backtest_results', 'statistics'],
                'processing_time': 1.0,
                'success_rate': 0.95
            }
        }
    
    def setup_database(self):
        """Setup database untuk menyimpan simulasi"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabel untuk session tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trading_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                date DATETIME NOT NULL,
                overall_performance TEXT,
                recommendations TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabel untuk module status
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS module_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                module_name TEXT NOT NULL,
                status TEXT NOT NULL,
                start_time DATETIME,
                end_time DATETIME,
                processing_time REAL,
                input_data TEXT,
                output_data TEXT,
                performance_metrics TEXT,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_trading_session(self, date: datetime) -> TradingSession:
        """Buat sesi trading baru"""
        session_id = f"session_{date.strftime('%Y%m%d')}"
        
        # Generate trading decisions for this session
        trading_decisions = self.generate_trading_decisions(date)
        
        # Update trading history
        trading_history = self.update_trading_history(trading_decisions)
        
        session = TradingSession(
            date=date,
            session_id=session_id,
            modules_status={},
            overall_performance={},
            recommendations=[],
            trading_decisions=trading_decisions,
            trading_history=trading_history
        )
        
        self.current_session = session
        return session
    
    def simulate_module_execution(self, module_name: str, session: TradingSession) -> ModuleStatus:
        """Simulasi eksekusi modul"""
        module_config = self.modules[module_name]
        
        # Check dependencies
        for dep in module_config['dependencies']:
            if dep in session.modules_status:
                dep_status = session.modules_status[dep]
                if dep_status.status != 'completed':
                    error_msg = f"Dependency {dep} not completed"
                    print(f"FAILED {module_name}: {error_msg}")
                    return ModuleStatus(
                        module_name=module_name,
                        status='error',
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        processing_time=0,
                        input_data={},
                        output_data={},
                        performance_metrics={},
                        error_message=error_msg
                    )
        
        # Start processing
        start_time = datetime.now()
        status = ModuleStatus(
            module_name=module_name,
            status='processing',
            start_time=start_time,
            end_time=None,
            processing_time=0,
            input_data=self.generate_input_data(module_name),
            output_data={},
            performance_metrics={}
        )
        
        # Simulate processing time
        processing_time = module_config['processing_time'] * self.time_multiplier
        time.sleep(processing_time)
        
        # Simulate success/failure with VERY high success rate
        success = np.random.random() < 0.95  # 95% success rate for all modules
        
        if success:
            status.status = 'completed'
            status.output_data = self.generate_output_data(module_name)
            status.performance_metrics = self.calculate_performance_metrics(module_name)
            print(f"COMPLETED {module_name} in {status.processing_time:.2f}s")
            print(f"   Performance: {status.performance_metrics}")
            
            # Simpan performance metrics ke database
            if hasattr(self, 'db') and status.performance_metrics:
                self.db.save_performance_metrics(
                    f"session_{session.date.strftime('%Y%m%d')}", 
                    module_name, 
                    status.performance_metrics, 
                    session.date
                )
        else:
            status.status = 'error'
            status.error_message = f"Processing error in {module_name}"
            print(f"FAILED {module_name}: {status.error_message}")
        
        status.end_time = datetime.now()
        status.processing_time = (status.end_time - status.start_time).total_seconds()
        
        return status
    
    def generate_trading_decisions(self, date: datetime) -> List[TradingDecision]:
        """Generate trading decisions untuk sesi"""
        decisions = []
        symbols = ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'TLKM', 'ASII', 'UNVR', 'ICBP', 'INDF', 'GOTO']
        
        # Generate 3-7 trading decisions per session
        num_decisions = np.random.randint(3, 8)
        
        for i in range(num_decisions):
            # Pilih saham dari database
            stock = np.random.choice(self.indonesia_stocks)
            symbol = stock['symbol']
            
            # Ambil harga dari database
            price = self.db.get_stock_price(symbol, date)
            
            action = np.random.choice(['BUY', 'SELL', 'HOLD'], p=[0.4, 0.3, 0.3])
            quantity = np.random.randint(10, 100)
            confidence = np.random.uniform(0.6, 0.95)
            
            # Generate reason dalam bahasa Indonesia
            if action == 'BUY':
                reason = f"Sinyal teknis: RSI oversold, MACD bullish crossover"
            elif action == 'SELL':
                reason = f"Manajemen risiko: Stop loss terpicu, target profit tercapai"
            else:
                reason = f"Ketidakpastian pasar: Menunggu entry point yang lebih baik"
            
            decision = TradingDecision(
                symbol=symbol,
                action=action,
                quantity=quantity,
                price=price,
                timestamp=date,
                reason=reason,
                confidence=confidence
            )
            decisions.append(decision)
            
            # Simpan ke database
            self.db.save_trading_decision(symbol, action, quantity, price, 
                                        f"session_{date.strftime('%Y%m%d')}", date)
        
        return decisions
    
    def update_trading_history(self, new_decisions: List[TradingDecision]) -> TradingHistory:
        """Update trading history dengan decisions baru"""
        # Simulate P&L for each decision
        daily_pnl = 0.0
        winning_trades = 0
        losing_trades = 0
        
        # Track portfolio investment dan returns
        portfolio_investment = 0.0  # Total belanja portfolio (BUY)
        portfolio_returns = 0.0     # Total return dari portfolio (SELL + P&L)
        
        for decision in new_decisions:
            trade_value = decision.quantity * decision.price
            
            if decision.action == 'BUY':
                # Belanja portfolio - mengurangi modal yang tersedia
                portfolio_investment += trade_value
                # Simulate profit/loss untuk BUY
                pnl = np.random.normal(0, trade_value * 0.02)  # 2% volatility
                portfolio_returns += pnl
                daily_pnl += pnl
                if pnl > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
                    
            elif decision.action == 'SELL':
                # Jual portfolio - menambah modal
                portfolio_returns += trade_value
                # Simulate profit/loss untuk SELL
                pnl = np.random.normal(0, trade_value * 0.015)  # 1.5% volatility
                portfolio_returns += pnl
                daily_pnl += pnl
                if pnl > 0:
                    winning_trades += 1
                else:
                    losing_trades += 1
                    
            elif decision.action == 'HOLD':
                # HOLD tidak mengubah modal
                pass
        
        # Update total P&L
        self.total_pnl += daily_pnl
        
        # Modal saat ini = (modal awal + untung) - (belanja portfolio + rugi)
        # Atau: modal awal + total P&L
        self.current_capital = self.initial_capital + self.total_pnl
        
        # Calculate win rate
        total_trades = winning_trades + losing_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
        
        # Get all trades from all sessions
        all_trades = []
        for session in self.sessions:
            all_trades.extend(session.trading_decisions)
        all_trades.extend(new_decisions)
        
        # Calculate total winning and losing trades from all sessions
        total_winning = 0
        total_losing = 0
        for trade in all_trades:
            # Simulate P&L for each trade to determine win/loss
            if trade.action in ['BUY', 'SELL']:
                trade_pnl = np.random.normal(0, trade.price * 0.02)
                if trade_pnl > 0:
                    total_winning += 1
                else:
                    total_losing += 1
        
        # Calculate overall win rate
        total_trades_count = total_winning + total_losing
        overall_win_rate = total_winning / total_trades_count if total_trades_count > 0 else 0.0
        
        return TradingHistory(
            trades=all_trades,
            total_capital=self.initial_capital,
            current_capital=self.current_capital,
            total_pnl=self.total_pnl,
            daily_pnl=daily_pnl,
            win_rate=overall_win_rate,
            total_trades=total_trades_count,
            winning_trades=total_winning,
            losing_trades=total_losing
        )
    
    def generate_input_data(self, module_name: str) -> Dict[str, Any]:
        """Generate input data untuk modul"""
        if module_name == 'market_data':
            return {
                'symbols': ['BBCA', 'BBRI', 'BMRI', 'BBNI', 'TLKM'],
                'price_data': np.random.normal(100, 10, 4).tolist(),
                'volume_data': np.random.randint(1000, 10000, 4).tolist(),
                'market_status': 'open'
            }
        elif module_name in ['technical_analysis', 'fundamental_analysis', 'sentiment_analysis']:
            return {
                'price_data': np.random.normal(100, 5, 20).tolist(),
                'volume_data': np.random.randint(1000, 5000, 20).tolist(),
                'timestamp': datetime.now().isoformat()
            }
        else:
            return {
                'previous_output': f"Data from previous module",
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_output_data(self, module_name: str) -> Dict[str, Any]:
        """Generate output data untuk modul"""
        if module_name == 'technical_analysis':
            return {
                'signals': ['BUY', 'SELL', 'HOLD', 'BUY'],
                'indicators': {
                    'rsi': np.random.uniform(20, 80, 4).tolist(),
                    'macd': np.random.uniform(-2, 2, 4).tolist(),
                    'sma': np.random.uniform(95, 105, 4).tolist()
                }
            }
        elif module_name == 'fundamental_analysis':
            return {
                'pe_ratio': np.random.uniform(10, 30, 4).tolist(),
                'pb_ratio': np.random.uniform(1, 5, 4).tolist(),
                'roe': np.random.uniform(5, 25, 4).tolist(),
                'debt_ratio': np.random.uniform(0.1, 0.8, 4).tolist()
            }
        elif module_name == 'sentiment_analysis':
            return {
                'sentiment_scores': np.random.uniform(-1, 1, 4).tolist(),
                'news_sentiment': np.random.uniform(0, 1, 4).tolist(),
                'social_sentiment': np.random.uniform(0, 1, 4).tolist()
            }
        elif module_name == 'strategy_builder':
            return {
                'strategy_rules': ['Buy when RSI < 30', 'Sell when RSI > 70'],
                'risk_parameters': {'max_position': 0.1, 'stop_loss': 0.05},
                'entry_conditions': ['Technical signal', 'Fundamental score > 0.5']
            }
        elif module_name == 'algorithmic_trading':
            return {
                'trade_signals': ['BUY', 'SELL', 'HOLD'],
                'order_quantities': [100, 50, 0],
                'target_prices': [105.5, 98.2, 0]
            }
        elif module_name == 'risk_management':
            return {
                'position_sizes': [0.05, 0.03, 0.0],
                'risk_scores': [0.3, 0.4, 0.0],
                'max_loss': [0.02, 0.015, 0.0]
            }
        elif module_name == 'trading':
            return {
                'executed_trades': [
                    {'symbol': 'BBCA', 'quantity': 100, 'price': 10550, 'side': 'BUY'},
                    {'symbol': 'BBRI', 'quantity': 50, 'price': 9820, 'side': 'SELL'}
                ],
                'positions': {'BBCA': 100, 'BBRI': -50}
            }
        elif module_name == 'performance_analytics':
            return {
                'daily_pnl': 1250.50,
                'total_return': 0.08,
                'sharpe_ratio': 1.85,
                'max_drawdown': 0.05,
                'win_rate': 0.68
            }
        elif module_name == 'portfolio_heatmap':
            return {
                'sector_allocation': {'Technology': 0.4, 'Finance': 0.3, 'Healthcare': 0.3},
                'correlation_matrix': np.random.uniform(-1, 1, (4, 4)).tolist(),
                'risk_metrics': {'var_95': 0.02, 'expected_shortfall': 0.03}
            }
        elif module_name == 'notifications':
            return {
                'alerts': [
                    'Volatilitas tinggi terdeteksi di BBCA',
                    'Portfolio risk limit approaching',
                    'New trading opportunity in GOOGL'
                ],
                'notifications_sent': 3
            }
        else:
            return {'output': f"Output from {module_name}"}
    
    def calculate_performance_metrics(self, module_name: str) -> Dict[str, float]:
        """Hitung performance metrics untuk modul"""
        base_accuracy = np.random.uniform(0.6, 0.95)
        base_speed = np.random.uniform(0.5, 1.0)
        
        return {
            'accuracy': base_accuracy,
            'processing_speed': base_speed,
            'reliability': np.random.uniform(0.7, 0.99),
            'efficiency': np.random.uniform(0.6, 0.9),
            'error_rate': 1 - base_accuracy
        }
    
    def simulate_daily_session(self, date: datetime) -> TradingSession:
        """Simulasi sesi trading harian"""
        print(f"\n{'='*60}")
        print(f"SIMULATING TRADING SESSION: {date.strftime('%Y-%m-%d')}")
        print(f"{'='*60}")
        
        session = self.create_trading_session(date)
        
        # Define execution order based on dependencies
        execution_order = [
            'market_data',
            'technical_analysis', 'fundamental_analysis', 'sentiment_analysis',
            'strategy_builder',
            'algorithmic_trading',
            'risk_management',
            'trading',
            'performance_analytics',
            'portfolio_heatmap',
            'notifications',
            'backtesting'
        ]
        
        # Execute modules in order with dependency checking
        for module_name in execution_order:
            # Check if simulation should stop
            if not self.simulation_running:
                print(f"\nSimulation stopped during {module_name}")
                break
                
            if module_name in self.modules:
                # Check dependencies - VERY lenient approach
                dependencies = self.modules[module_name].get('dependencies', [])
                dependencies_met = True
                
                # Skip dependency checking for first 4 modules
                if module_name in ['market_data', 'technical_analysis', 'fundamental_analysis', 'sentiment_analysis']:
                    dependencies_met = True
                else:
                    # For other modules, check dependencies but be more lenient
                    for dep in dependencies:
                        if dep in session.modules_status:
                            if session.modules_status[dep].status not in ['completed', 'processing']:
                                # Only fail if dependency is explicitly failed
                                if session.modules_status[dep].status == 'failed':
                                    dependencies_met = False
                                    print(f"FAILED {module_name}: Dependency {dep} failed")
                                    break
                        else:
                            # If dependency not in session yet, assume it will succeed
                            dependencies_met = True
                
                if not dependencies_met:
                    # Create failed status
                    failed_status = ModuleStatus(
                        module_name=module_name,
                        status='failed',
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        processing_time=0,
                        input_data={},
                        output_data={},
                        performance_metrics={},
                        error_message=f"Dependency not completed"
                    )
                    session.modules_status[module_name] = failed_status
                    continue
                
                print(f"\nProcessing {self.modules[module_name]['name']}...")
                
                status = self.simulate_module_execution(module_name, session)
                session.modules_status[module_name] = status
                
                if status.status == 'completed':
                    print(f"COMPLETED {module_name} in {status.processing_time:.2f}s")
                    print(f"   Performance: {status.performance_metrics}")
                else:
                    print(f"FAILED {module_name}: {status.error_message}")
                
                # Small delay between modules
                time.sleep(0.1)
        
        # Calculate overall session performance
        session.overall_performance = self.calculate_session_performance(session)
        session.recommendations = self.generate_session_recommendations(session)
        
        # Save to database
        self.save_session_to_db(session)
        
        # Print session summary
        self.print_session_summary(session)
        
        return session
    
    def calculate_session_performance(self, session: TradingSession) -> Dict[str, float]:
        """Hitung overall performance sesi"""
        completed_modules = [m for m in session.modules_status.values() if m.status == 'completed']
        
        if not completed_modules:
            return {'overall_score': 0.0, 'success_rate': 0.0}
        
        total_accuracy = sum(m.performance_metrics.get('accuracy', 0) for m in completed_modules)
        avg_accuracy = total_accuracy / len(completed_modules)
        
        success_rate = len(completed_modules) / len(session.modules_status)
        
        return {
            'overall_score': avg_accuracy,
            'success_rate': success_rate,
            'total_modules': len(session.modules_status),
            'completed_modules': len(completed_modules),
            'failed_modules': len(session.modules_status) - len(completed_modules)
        }
    
    def generate_session_recommendations(self, session: TradingSession) -> List[str]:
        """Generate rekomendasi berdasarkan performance sesi"""
        recommendations = []
        
        # Check individual module performance
        for module_name, status in session.modules_status.items():
            if status.status == 'error':
                recommendations.append(f"ERROR {module_name}: Module failed - needs immediate attention")
            elif status.performance_metrics.get('accuracy', 0) < 0.7:
                recommendations.append(f"WARNING {module_name}: Low accuracy - consider tuning")
            elif status.performance_metrics.get('accuracy', 0) > 0.9:
                recommendations.append(f"SUCCESS {module_name}: Excellent performance - maintain")
        
        # Overall recommendations
        overall_perf = session.overall_performance
        if overall_perf['success_rate'] < 0.8:
            recommendations.append("CRITICAL: System reliability low - review failed modules")
        elif overall_perf['overall_score'] < 0.7:
            recommendations.append("WARNING: Overall performance below target - optimization needed")
        else:
            recommendations.append("SUCCESS: System performing well - continue monitoring")
        
        return recommendations
    
    def save_session_to_db(self, session: TradingSession):
        """Simpan sesi ke database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Save session
        cursor.execute('''
            INSERT INTO trading_sessions (session_id, date, overall_performance, recommendations)
            VALUES (?, ?, ?, ?)
        ''', (
            session.session_id,
            session.date,
            json.dumps(session.overall_performance),
            json.dumps(session.recommendations)
        ))
        
        # Save module statuses
        for module_name, status in session.modules_status.items():
            cursor.execute('''
                INSERT INTO module_status 
                (session_id, module_name, status, start_time, end_time, processing_time,
                 input_data, output_data, performance_metrics, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                session.session_id, module_name, status.status,
                status.start_time, status.end_time, status.processing_time,
                json.dumps(status.input_data), json.dumps(status.output_data),
                json.dumps(status.performance_metrics), status.error_message
            ))
        
        conn.commit()
        conn.close()
    
    def print_session_summary(self, session: TradingSession):
        """Print ringkasan sesi"""
        print(f"\nSESSION SUMMARY: {session.date.strftime('%Y-%m-%d')}")
        print(f"Overall Score: {session.overall_performance['overall_score']:.2f}")
        print(f"Success Rate: {session.overall_performance['success_rate']:.1%}")
        print(f"Completed Modules: {session.overall_performance['completed_modules']}/{session.overall_performance['total_modules']}")
        
        print(f"\nRECOMMENDATIONS:")
        for rec in session.recommendations:
            print(f"   {rec}")
    
    def run_time_lapse_simulation(self, start_date: datetime, days: int = 30):
        """Jalankan simulasi time-lapse"""
        print(f"STARTING TIME-LAPSE SIMULATION")
        print(f"Period: {start_date.strftime('%Y-%m-%d')} to {(start_date + timedelta(days=days)).strftime('%Y-%m-%d')}")
        print(f"Time Multiplier: 1 day = {self.time_multiplier} seconds")
        print(f"Total Simulation Time: {days * self.time_multiplier:.1f} seconds")
        print(f"Modal Awal: Rp {self.initial_capital:,.0f}")
        print(f"Database: {self.db.db_path}")
        print(f"Indonesian Stocks: {len(self.indonesia_stocks)} stocks loaded")
        print(f"{'='*60}")
        
        self.simulation_running = True
        self.sessions = []
        self.start_date = start_date
        self.end_date = start_date + timedelta(days=days)
        self.current_date = start_date
        
        try:
            for day in range(days):
                # Check if simulation should stop
                if not self.simulation_running:
                    print(f"\nSimulation stopped by user at day {day + 1}")
                    break
                    
                current_date = start_date + timedelta(days=day)
                self.current_date = current_date
                session = self.simulate_daily_session(current_date)
                self.sessions.append(session)
                
                # Progress indicator with trading info
                progress = (day + 1) / days * 100
                print(f"\nPROGRESS: {progress:.1f}% ({day + 1}/{days} days)")
                print(f"Tanggal Saat Ini: {current_date.strftime('%d/%m/%Y')}")
                print(f"Modal Awal: Rp {self.initial_capital:,.0f}")
                print(f"Total P&L: Rp {self.total_pnl:,.0f} ({self.total_pnl/self.initial_capital*100:.2f}%)")
                print(f"Modal Saat Ini: Rp {self.current_capital:,.0f} (Modal Awal + P&L)")
                
        except KeyboardInterrupt:
            print("\nSimulation stopped by user")
            self.simulation_running = False
        
        # Final analysis
        self.generate_final_analysis()
    
    def generate_final_analysis(self):
        """Generate analisis akhir dari semua sesi"""
        print(f"\n{'='*60}")
        print(f"FINAL ANALYSIS - {len(self.sessions)} SESSIONS")
        print(f"{'='*60}")
        
        # Overall statistics
        all_scores = [s.overall_performance['overall_score'] for s in self.sessions]
        all_success_rates = [s.overall_performance['success_rate'] for s in self.sessions]
        
        print(f"Average Overall Score: {np.mean(all_scores):.3f}")
        print(f"Average Success Rate: {np.mean(all_success_rates):.1%}")
        print(f"Best Session: {max(all_scores):.3f}")
        print(f"Worst Session: {min(all_scores):.3f}")
        
        # Module performance analysis
        module_performance = {}
        for session in self.sessions:
            for module_name, status in session.modules_status.items():
                if module_name not in module_performance:
                    module_performance[module_name] = []
                module_performance[module_name].append({
                    'accuracy': status.performance_metrics.get('accuracy', 0),
                    'status': status.status,
                    'processing_time': status.processing_time
                })
        
        print(f"\nMODULE PERFORMANCE ANALYSIS:")
        for module_name, performances in module_performance.items():
            avg_accuracy = np.mean([p['accuracy'] for p in performances])
            success_rate = len([p for p in performances if p['status'] == 'completed']) / len(performances)
            avg_processing_time = np.mean([p['processing_time'] for p in performances])
            
            print(f"\n{module_name}:")
            print(f"  Average Accuracy: {avg_accuracy:.3f}")
            print(f"  Success Rate: {success_rate:.1%}")
            print(f"  Avg Processing Time: {avg_processing_time:.2f}s")
            
            # Recommendations
            if avg_accuracy < 0.7:
                print(f"  RECOMMENDATION: Replace or major tuning needed")
            elif avg_accuracy < 0.8:
                print(f"  RECOMMENDATION: Tuning recommended")
            elif avg_accuracy > 0.9:
                print(f"  RECOMMENDATION: Excellent - maintain")
            else:
                print(f"  RECOMMENDATION: Good - monitor")
        
        print(f"\nSYSTEM RECOMMENDATIONS:")
        print(f"1. Focus on modules with accuracy < 0.8")
        print(f"2. Optimize processing times for slow modules")
        print(f"3. Implement redundancy for critical modules")
        print(f"4. Regular monitoring and maintenance schedule")

# Global simulator instance
simulator = None

def get_simulator():
    """Get or create simulator instance"""
    global simulator
    if simulator is None:
        simulator = TimeLapseSimulator()
    return simulator

def run_simulation(start_date: datetime, days: int = 30):
    """Run time-lapse simulation"""
    simulator = get_simulator()
    simulator.run_time_lapse_simulation(start_date, days)

if __name__ == '__main__':
    # Run simulation for 30 days
    start_date = datetime(2024, 1, 1)
    run_simulation(start_date, 30)
