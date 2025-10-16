#!/usr/bin/env python3
"""
Automated Module Tuning System
=============================

Script untuk melakukan tuning otomatis pada semua modul trading
dengan menggunakan genetic algorithm untuk mendapatkan konfigurasi terbaik.

Author: AI Assistant
Date: 2025-01-17
"""

import sys
import os
import json
import time
import random
import numpy as np
import mysql.connector
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

class AutomatedModuleTuning:
    """Automated Module Tuning System"""
    
    def __init__(self, db_config: Dict[str, Any], config_file: str = "modul/module_configuration.json"):
        self.db_config = db_config
        self.config_file = config_file
        self.connection = None
        self.cursor = None
        self.configuration = {}
        self.tuning_results = {}
        
    def load_configuration(self) -> bool:
        """Load module configuration from JSON file"""
        try:
            with open(self.config_file, 'r') as f:
                self.configuration = json.load(f)
            print(f"[PASS] Configuration loaded from {self.config_file}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to load configuration: {e}")
            return False
    
    def save_configuration(self) -> bool:
        """Save module configuration to JSON file"""
        try:
            # Update last_updated timestamp
            self.configuration['module_configuration']['last_updated'] = datetime.now().isoformat()
            
            with open(self.config_file, 'w') as f:
                json.dump(self.configuration, f, indent=2)
            print(f"[PASS] Configuration saved to {self.config_file}")
            return True
        except Exception as e:
            print(f"[FAIL] Failed to save configuration: {e}")
            return False
    
    def connect_database(self):
        """Connect to database"""
        try:
            self.connection = mysql.connector.connect(
                **self.db_config,
                charset='utf8mb4',
                collation='utf8mb4_unicode_ci',
                autocommit=False
            )
            self.cursor = self.connection.cursor()
            print("[PASS] Database connection established")
            return True
        except Exception as e:
            print(f"[FAIL] Database connection failed: {e}")
            return False
    
    def disconnect_database(self):
        """Disconnect from database"""
        if self.connection and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("[PASS] Database connection closed")
    
    def test_module_performance(self, module_name: str, configuration: Dict[str, Any]) -> float:
        """Test module performance with given configuration"""
        try:
            performance_score = 0.0
            
            if module_name == "trading_module":
                performance_score = self.test_trading_module(configuration)
            elif module_name == "market_data_module":
                performance_score = self.test_market_data_module(configuration)
            elif module_name == "risk_management_module":
                performance_score = self.test_risk_management_module(configuration)
            elif module_name == "technical_analysis_module":
                performance_score = self.test_technical_analysis_module(configuration)
            elif module_name == "fundamental_analysis_module":
                performance_score = self.test_fundamental_analysis_module(configuration)
            elif module_name == "sentiment_analysis_module":
                performance_score = self.test_sentiment_analysis_module(configuration)
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Testing {module_name}: {e}")
            return 0.0
    
    def test_trading_module(self, configuration: Dict[str, Any]) -> float:
        """Test trading module performance"""
        try:
            # Test execution latency
            self.cursor.execute("SELECT AVG(TIMESTAMPDIFF(MICROSECOND, created_at, executed_at)) FROM orders WHERE executed_at IS NOT NULL")
            avg_latency = self.cursor.fetchone()[0] or 0
            latency_score = max(0, 100 - (avg_latency / 1000000))  # Convert to seconds
            
            # Test execution rate
            self.cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'executed'")
            executed_orders = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM orders")
            total_orders = self.cursor.fetchone()[0]
            execution_rate = (executed_orders / total_orders * 100) if total_orders > 0 else 0
            
            # Test position sizing
            max_position_size = configuration.get('max_position_size', 0.1)
            position_size_score = min(100, max_position_size * 1000)  # Convert to percentage
            
            # Test risk management
            stop_loss = configuration.get('stop_loss_percentage', 0.02)
            take_profit = configuration.get('take_profit_percentage', 0.04)
            risk_reward_ratio = take_profit / stop_loss if stop_loss > 0 else 0
            risk_score = min(100, risk_reward_ratio * 25)  # Optimal ratio is 2:1
            
            # Calculate overall performance
            performance_score = (latency_score + execution_rate + position_size_score + risk_score) / 4
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Trading module test: {e}")
            return 0.0
    
    def test_market_data_module(self, configuration: Dict[str, Any]) -> float:
        """Test market data module performance"""
        try:
            # Test data completeness
            self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE symbol LIKE '%.JK'")
            market_data_count = self.cursor.fetchone()[0]
            completeness_score = min(100, market_data_count / 1000 * 100)
            
            # Test data quality
            self.cursor.execute("SELECT AVG(overall_quality_score) FROM market_data_quality_metrics")
            data_quality_score = self.cursor.fetchone()[0] or 0
            
            # Test data timeliness
            self.cursor.execute("SELECT COUNT(*) FROM market_data WHERE date >= DATE_SUB(NOW(), INTERVAL 1 DAY)")
            recent_data_count = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM market_data")
            total_data_count = self.cursor.fetchone()[0]
            timeliness_score = (recent_data_count / total_data_count * 100) if total_data_count > 0 else 0
            
            # Test refresh interval efficiency
            refresh_interval = configuration.get('data_refresh_interval', 60)
            refresh_score = max(0, 100 - (refresh_interval / 10))  # Lower interval is better
            
            # Calculate overall performance
            performance_score = (completeness_score + float(data_quality_score) + timeliness_score + refresh_score) / 4
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Market data module test: {e}")
            return 0.0
    
    def test_risk_management_module(self, configuration: Dict[str, Any]) -> float:
        """Test risk management module performance"""
        try:
            # Test VaR calculation
            var_confidence = configuration.get('var_confidence_level', 0.95)
            self.cursor.execute("SELECT COUNT(*) FROM risk_metrics WHERE var_95 IS NOT NULL")
            var_count = self.cursor.fetchone()[0]
            var_score = min(100, var_count / 10 * 100)
            
            # Test portfolio risk
            self.cursor.execute("SELECT COUNT(*) FROM portfolio_risk")
            portfolio_risk_count = self.cursor.fetchone()[0]
            portfolio_score = min(100, portfolio_risk_count / 5 * 100)
            
            # Test Sharpe ratio
            self.cursor.execute("SELECT AVG(sharpe_ratio) FROM risk_metrics WHERE sharpe_ratio IS NOT NULL")
            avg_sharpe_ratio = self.cursor.fetchone()[0] or 0
            sharpe_score = min(100, float(avg_sharpe_ratio) * 50)  # Scale up sharpe ratio
            
            # Test correlation analysis
            correlation_threshold = configuration.get('correlation_threshold', 0.7)
            correlation_score = min(100, (1 - correlation_threshold) * 200)  # Lower threshold is better
            
            # Calculate overall performance
            performance_score = (var_score + portfolio_score + sharpe_score + correlation_score) / 4
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Risk management module test: {e}")
            return 0.0
    
    def test_technical_analysis_module(self, configuration: Dict[str, Any]) -> float:
        """Test technical analysis module performance"""
        try:
            # Test indicator coverage
            self.cursor.execute("SELECT COUNT(*) FROM technical_indicators WHERE indicator_type IS NOT NULL")
            typed_indicators = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM technical_indicators")
            total_indicators = self.cursor.fetchone()[0]
            coverage_score = (typed_indicators / total_indicators * 100) if total_indicators > 0 else 0
            
            # Test indicator diversity
            self.cursor.execute("SELECT COUNT(DISTINCT indicator_type) FROM technical_indicators WHERE indicator_type IS NOT NULL")
            unique_indicators = self.cursor.fetchone()[0]
            diversity_score = min(100, unique_indicators * 10)  # More indicators is better
            
            # Test SMA configuration
            sma_periods = configuration.get('sma_periods', [20, 50, 200])
            sma_score = min(100, len(sma_periods) * 25)  # More periods is better
            
            # Test RSI configuration
            rsi_period = configuration.get('rsi_period', 14)
            rsi_score = max(0, 100 - abs(rsi_period - 14) * 5)  # 14 is optimal
            
            # Test MACD configuration
            macd_fast = configuration.get('macd_fast', 12)
            macd_slow = configuration.get('macd_slow', 26)
            macd_score = max(0, 100 - abs(macd_fast - 12) - abs(macd_slow - 26))
            
            # Calculate overall performance
            performance_score = (coverage_score + diversity_score + sma_score + rsi_score + macd_score) / 5
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Technical analysis module test: {e}")
            return 0.0
    
    def test_fundamental_analysis_module(self, configuration: Dict[str, Any]) -> float:
        """Test fundamental analysis module performance"""
        try:
            # Test fundamental data coverage
            self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE pe_ratio IS NOT NULL")
            pe_ratio_count = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM fundamental_data")
            total_fundamental = self.cursor.fetchone()[0]
            coverage_score = (pe_ratio_count / total_fundamental * 100) if total_fundamental > 0 else 0
            
            # Test PE ratio threshold
            pe_threshold = configuration.get('pe_ratio_threshold', 15)
            self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE pe_ratio <= %s", (pe_threshold,))
            good_pe_count = self.cursor.fetchone()[0]
            pe_score = (good_pe_count / pe_ratio_count * 100) if pe_ratio_count > 0 else 0
            
            # Test PB ratio threshold
            pb_threshold = configuration.get('pb_ratio_threshold', 2.0)
            self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE pb_ratio <= %s", (pb_threshold,))
            good_pb_count = self.cursor.fetchone()[0]
            pb_score = (good_pb_count / pe_ratio_count * 100) if pe_ratio_count > 0 else 0
            
            # Test debt-to-equity threshold
            debt_threshold = configuration.get('debt_to_equity_threshold', 0.5)
            self.cursor.execute("SELECT COUNT(*) FROM fundamental_data WHERE debt_to_equity <= %s", (debt_threshold,))
            good_debt_count = self.cursor.fetchone()[0]
            debt_score = (good_debt_count / pe_ratio_count * 100) if pe_ratio_count > 0 else 0
            
            # Calculate overall performance
            performance_score = (coverage_score + pe_score + pb_score + debt_score) / 4
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Fundamental analysis module test: {e}")
            return 0.0
    
    def test_sentiment_analysis_module(self, configuration: Dict[str, Any]) -> float:
        """Test sentiment analysis module performance"""
        try:
            # Test sentiment data coverage
            self.cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE sentiment_score IS NOT NULL")
            sentiment_count = self.cursor.fetchone()[0]
            self.cursor.execute("SELECT COUNT(*) FROM sentiment_data")
            total_sentiment = self.cursor.fetchone()[0]
            coverage_score = (sentiment_count / total_sentiment * 100) if total_sentiment > 0 else 0
            
            # Test sentiment threshold
            sentiment_threshold = configuration.get('sentiment_threshold', 0.7)
            self.cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE sentiment_score >= %s", (sentiment_threshold,))
            positive_sentiment_count = self.cursor.fetchone()[0]
            sentiment_score = (positive_sentiment_count / sentiment_count * 100) if sentiment_count > 0 else 0
            
            # Test confidence threshold
            confidence_threshold = configuration.get('confidence_threshold', 0.8)
            self.cursor.execute("SELECT COUNT(*) FROM sentiment_data WHERE confidence >= %s", (confidence_threshold,))
            high_confidence_count = self.cursor.fetchone()[0]
            confidence_score = (high_confidence_count / sentiment_count * 100) if sentiment_count > 0 else 0
            
            # Test sentiment window
            sentiment_window = configuration.get('sentiment_window', 7)
            window_score = max(0, 100 - abs(sentiment_window - 7) * 10)  # 7 days is optimal
            
            # Calculate overall performance
            performance_score = (coverage_score + sentiment_score + confidence_score + window_score) / 4
            
            return performance_score
            
        except Exception as e:
            print(f"[ERROR] Sentiment analysis module test: {e}")
            return 0.0
    
    def generate_random_configuration(self, module_name: str) -> Dict[str, Any]:
        """Generate random configuration for a module"""
        try:
            module_config = self.configuration['module_configuration']['modules'][module_name]
            tuning_params = module_config['tuning_parameters']
            
            random_config = {}
            for param_name, param_config in tuning_params.items():
                if isinstance(param_config['current'], list):
                    # Handle list parameters
                    random_config[param_name] = []
                    for i, (min_val, max_val, step) in enumerate(zip(param_config['min'], param_config['max'], param_config['step'])):
                        random_val = random.uniform(min_val, max_val)
                        random_val = round(random_val / step) * step
                        random_config[param_name].append(random_val)
                else:
                    # Handle single parameters
                    min_val = param_config['min']
                    max_val = param_config['max']
                    step = param_config['step']
                    
                    random_val = random.uniform(min_val, max_val)
                    random_val = round(random_val / step) * step
                    random_val = max(min_val, min(max_val, random_val))
                    
                    random_config[param_name] = random_val
            
            return random_config
            
        except Exception as e:
            print(f"[ERROR] Generating random configuration for {module_name}: {e}")
            return {}
    
    def crossover_configurations(self, config1: Dict[str, Any], config2: Dict[str, Any]) -> Dict[str, Any]:
        """Crossover two configurations to create offspring"""
        try:
            offspring = {}
            
            for key in config1.keys():
                if random.random() < 0.5:
                    offspring[key] = config1[key]
                else:
                    offspring[key] = config2[key]
            
            return offspring
            
        except Exception as e:
            print(f"[ERROR] Crossover configurations: {e}")
            return config1
    
    def mutate_configuration(self, configuration: Dict[str, Any], module_name: str) -> Dict[str, Any]:
        """Mutate a configuration"""
        try:
            mutated_config = configuration.copy()
            module_config = self.configuration['module_configuration']['modules'][module_name]
            tuning_params = module_config['tuning_parameters']
            
            # Mutate random parameters
            for param_name in random.sample(list(tuning_params.keys()), k=min(3, len(tuning_params))):
                param_config = tuning_params[param_name]
                
                if isinstance(param_config['current'], list):
                    # Handle list parameters
                    mutated_list = []
                    for i, (min_val, max_val, step) in enumerate(zip(param_config['min'], param_config['max'], param_config['step'])):
                        if random.random() < 0.3:  # 30% chance to mutate each element
                            random_val = random.uniform(min_val, max_val)
                            random_val = round(random_val / step) * step
                            random_val = max(min_val, min(max_val, random_val))
                            mutated_list.append(random_val)
                        else:
                            mutated_list.append(mutated_config[param_name][i])
                    mutated_config[param_name] = mutated_list
                else:
                    # Handle single parameters
                    if random.random() < 0.3:  # 30% chance to mutate
                        min_val = param_config['min']
                        max_val = param_config['max']
                        step = param_config['step']
                        
                        random_val = random.uniform(min_val, max_val)
                        random_val = round(random_val / step) * step
                        random_val = max(min_val, min(max_val, random_val))
                        
                        mutated_config[param_name] = random_val
            
            return mutated_config
            
        except Exception as e:
            print(f"[ERROR] Mutating configuration: {e}")
            return configuration
    
    def run_genetic_algorithm(self, module_name: str, generations: int = 50) -> Dict[str, Any]:
        """Run genetic algorithm for module tuning"""
        try:
            print(f"   Running genetic algorithm for {module_name}...")
            
            # Get tuning strategy
            tuning_strategy = self.configuration['module_configuration']['tuning_strategy']
            population_size = tuning_strategy['population_size']
            mutation_rate = tuning_strategy['mutation_rate']
            crossover_rate = tuning_strategy['crossover_rate']
            elitism_rate = tuning_strategy['elitism_rate']
            
            # Initialize population
            population = []
            for _ in range(population_size):
                config = self.generate_random_configuration(module_name)
                performance = self.test_module_performance(module_name, config)
                population.append({
                    'configuration': config,
                    'performance': performance
                })
            
            best_performance = 0.0
            best_configuration = {}
            performance_history = []
            
            for generation in range(generations):
                print(f"     Generation {generation + 1}/{generations}")
                
                # Sort population by performance
                population.sort(key=lambda x: x['performance'], reverse=True)
                
                # Update best configuration
                if population[0]['performance'] > best_performance:
                    best_performance = population[0]['performance']
                    best_configuration = population[0]['configuration']
                
                performance_history.append(best_performance)
                
                # Create new population
                new_population = []
                
                # Elitism: keep best individuals
                elite_count = int(population_size * elitism_rate)
                new_population.extend(population[:elite_count])
                
                # Generate offspring
                while len(new_population) < population_size:
                    # Selection: tournament selection
                    parent1 = self.tournament_selection(population, 3)
                    parent2 = self.tournament_selection(population, 3)
                    
                    # Crossover
                    if random.random() < crossover_rate:
                        offspring_config = self.crossover_configurations(
                            parent1['configuration'], 
                            parent2['configuration']
                        )
                    else:
                        offspring_config = parent1['configuration']
                    
                    # Mutation
                    if random.random() < mutation_rate:
                        offspring_config = self.mutate_configuration(offspring_config, module_name)
                    
                    # Test offspring performance
                    offspring_performance = self.test_module_performance(module_name, offspring_config)
                    
                    new_population.append({
                        'configuration': offspring_config,
                        'performance': offspring_performance
                    })
                
                population = new_population
                
                print(f"       Best performance: {best_performance:.2f}%")
            
            return {
                'best_configuration': best_configuration,
                'best_performance': best_performance,
                'performance_history': performance_history
            }
            
        except Exception as e:
            print(f"[ERROR] Genetic algorithm for {module_name}: {e}")
            return {}
    
    def tournament_selection(self, population: List[Dict], tournament_size: int) -> Dict:
        """Tournament selection for genetic algorithm"""
        try:
            tournament = random.sample(population, tournament_size)
            return max(tournament, key=lambda x: x['performance'])
        except Exception as e:
            print(f"[ERROR] Tournament selection: {e}")
            return population[0]
    
    def run_automated_tuning(self) -> Dict[str, Any]:
        """Run automated tuning for all modules"""
        try:
            print("AUTOMATED MODULE TUNING SYSTEM")
            print("=" * 80)
            print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            
            # Results
            results = {
                'tuning_type': 'automated_module_tuning',
                'tuning_start': datetime.now().isoformat(),
                'database_connection': False,
                'module_tuning_results': {},
                'overall_improvement': {},
                'final_assessment': {}
            }
            
            # Load configuration
            if not self.load_configuration():
                return results
            
            # Connect to database
            if not self.connect_database():
                return results
            
            results['database_connection'] = True
            
            # Get modules to tune
            modules = self.configuration['module_configuration']['modules']
            tuning_strategy = self.configuration['module_configuration']['tuning_strategy']
            generations = tuning_strategy['generations']
            
            print(f"\nTuning {len(modules)} modules with {generations} generations each...")
            
            # Tune each module
            for module_name, module_config in modules.items():
                if module_config['status'] == 'ACTIVE':
                    print(f"\nTUNING {module_name.upper()}")
                    print("-" * 60)
                    
                    # Run genetic algorithm
                    tuning_result = self.run_genetic_algorithm(module_name, generations)
                    
                    if tuning_result:
                        # Update module configuration
                        modules[module_name]['performance_score'] = tuning_result['best_performance']
                        modules[module_name]['best_configuration'] = tuning_result['best_configuration']
                        modules[module_name]['performance_history'].extend(tuning_result['performance_history'])
                        
                        # Update tuning parameters with best values
                        for param_name, param_value in tuning_result['best_configuration'].items():
                            if param_name in modules[module_name]['tuning_parameters']:
                                modules[module_name]['tuning_parameters'][param_name]['best'] = param_value
                                modules[module_name]['tuning_parameters'][param_name]['current'] = param_value
                        
                        results['module_tuning_results'][module_name] = {
                            'best_performance': tuning_result['best_performance'],
                            'improvement': tuning_result['best_performance'] - module_config.get('performance_score', 0),
                            'best_configuration': tuning_result['best_configuration']
                        }
                        
                        print(f"   Best performance: {tuning_result['best_performance']:.2f}%")
                        print(f"   Improvement: {tuning_result['best_performance'] - module_config.get('performance_score', 0):.2f}%")
                    else:
                        print(f"   [ERROR] Failed to tune {module_name}")
            
            # Calculate overall improvement
            total_improvement = 0.0
            improved_modules = 0
            
            for module_name, tuning_result in results['module_tuning_results'].items():
                if tuning_result['improvement'] > 0:
                    total_improvement += tuning_result['improvement']
                    improved_modules += 1
            
            results['overall_improvement'] = {
                'total_improvement': total_improvement,
                'improved_modules': improved_modules,
                'average_improvement': total_improvement / improved_modules if improved_modules > 0 else 0
            }
            
            # Generate final assessment
            final_assessment = self.generate_final_assessment(results)
            results['final_assessment'] = final_assessment
            
            # Save updated configuration
            self.save_configuration()
            
            # Close database connection
            self.disconnect_database()
            
            # Generate comprehensive report
            self.generate_comprehensive_report(results)
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Automated tuning failed: {e}")
            return {'error': str(e)}
    
    def generate_final_assessment(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate final assessment"""
        try:
            assessment = {
                'tuning_status': '',
                'overall_improvement': 0.0,
                'best_performing_modules': [],
                'modules_needing_improvement': [],
                'recommendations': []
            }
            
            # Analyze overall improvement
            overall_improvement = results.get('overall_improvement', {})
            total_improvement = overall_improvement.get('total_improvement', 0)
            improved_modules = overall_improvement.get('improved_modules', 0)
            average_improvement = overall_improvement.get('average_improvement', 0)
            
            assessment['overall_improvement'] = total_improvement
            
            # Determine tuning status
            if total_improvement > 50:
                assessment['tuning_status'] = 'EXCELLENT'
            elif total_improvement > 20:
                assessment['tuning_status'] = 'GOOD'
            elif total_improvement > 0:
                assessment['tuning_status'] = 'FAIR'
            else:
                assessment['tuning_status'] = 'POOR'
            
            # Analyze module performance
            module_results = results.get('module_tuning_results', {})
            
            for module_name, module_result in module_results.items():
                improvement = module_result.get('improvement', 0)
                best_performance = module_result.get('best_performance', 0)
                
                if improvement > 10:
                    assessment['best_performing_modules'].append({
                        'module': module_name,
                        'improvement': improvement,
                        'performance': best_performance
                    })
                elif best_performance < 70:
                    assessment['modules_needing_improvement'].append({
                        'module': module_name,
                        'performance': best_performance
                    })
            
            # Recommendations
            if total_improvement > 20:
                assessment['recommendations'].append("Continue with current tuning strategy")
                assessment['recommendations'].append("Implement additional testing phases")
            else:
                assessment['recommendations'].append("Adjust tuning parameters")
                assessment['recommendations'].append("Increase number of generations")
                assessment['recommendations'].append("Modify mutation and crossover rates")
            
            return assessment
            
        except Exception as e:
            return {'error': str(e)}
    
    def generate_comprehensive_report(self, results: Dict[str, Any]) -> None:
        """Generate comprehensive report"""
        print("\nAUTOMATED MODULE TUNING REPORT")
        print("=" * 80)
        
        # Module tuning results
        module_results = results.get('module_tuning_results', {})
        print(f"Module Tuning Results:")
        
        for module_name, module_result in module_results.items():
            print(f"  {module_name}:")
            print(f"    Best Performance: {module_result.get('best_performance', 0):.2f}%")
            print(f"    Improvement: {module_result.get('improvement', 0):.2f}%")
        
        # Overall improvement
        overall_improvement = results.get('overall_improvement', {})
        print(f"\nOverall Improvement:")
        print(f"  Total Improvement: {overall_improvement.get('total_improvement', 0):.2f}%")
        print(f"  Improved Modules: {overall_improvement.get('improved_modules', 0)}")
        print(f"  Average Improvement: {overall_improvement.get('average_improvement', 0):.2f}%")
        
        # Final assessment
        final_assessment = results.get('final_assessment', {})
        print(f"\nFinal Assessment:")
        print(f"  Tuning Status: {final_assessment.get('tuning_status', 'UNKNOWN')}")
        print(f"  Overall Improvement: {final_assessment.get('overall_improvement', 0):.2f}%")
        
        best_modules = final_assessment.get('best_performing_modules', [])
        if best_modules:
            print(f"  Best Performing Modules:")
            for module in best_modules:
                print(f"    - {module['module']}: {module['improvement']:.2f}% improvement")
        
        modules_needing_improvement = final_assessment.get('modules_needing_improvement', [])
        if modules_needing_improvement:
            print(f"  Modules Needing Improvement:")
            for module in modules_needing_improvement:
                print(f"    - {module['module']}: {module['performance']:.2f}% performance")
        
        recommendations = final_assessment.get('recommendations', [])
        if recommendations:
            print(f"  Recommendations:")
            for recommendation in recommendations:
                print(f"    - {recommendation}")
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"automated_module_tuning_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nAutomated module tuning results saved to: {results_file}")
        print(f"Tuning completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'scalper',
        'port': 3306
    }
    
    # Create automated module tuning instance
    tuning_system = AutomatedModuleTuning(db_config)
    
    # Run automated tuning
    results = tuning_system.run_automated_tuning()
    
    return results

if __name__ == "__main__":
    main()
