"""
Enhanced Fundamental Analysis Service
=====================================

Service untuk fundamental analysis dengan implementasi algoritma terbukti
menggunakan financial ratios, DCF analysis, dan advanced valuation models.

Author: AI Assistant
Date: 2025-01-17
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import json
from app.models.fundamental import FundamentalData, FinancialRatios, ValuationMetrics
from app.services.cache_service import CacheService

logger = logging.getLogger(__name__)

class EnhancedFundamentalAnalysisService:
    """
    Enhanced Fundamental Analysis Service dengan algoritma terbukti
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.cache_service = CacheService(db)
        
        # Financial ratios thresholds
        self.ratio_thresholds = {
            'current_ratio': {'good': 2.0, 'acceptable': 1.0, 'poor': 0.5},
            'quick_ratio': {'good': 1.0, 'acceptable': 0.5, 'poor': 0.2},
            'debt_to_equity': {'good': 0.3, 'acceptable': 0.6, 'poor': 1.0},
            'roe': {'good': 0.15, 'acceptable': 0.10, 'poor': 0.05},
            'roa': {'good': 0.10, 'acceptable': 0.05, 'poor': 0.02},
            'gross_margin': {'good': 0.40, 'acceptable': 0.25, 'poor': 0.15},
            'operating_margin': {'good': 0.20, 'acceptable': 0.10, 'poor': 0.05},
            'net_margin': {'good': 0.15, 'acceptable': 0.08, 'poor': 0.03}
        }
        
        # Valuation thresholds
        self.valuation_thresholds = {
            'pe_ratio': {'undervalued': 15, 'fair': 20, 'overvalued': 25},
            'pb_ratio': {'undervalued': 1.0, 'fair': 2.0, 'overvalued': 3.0},
            'ps_ratio': {'undervalued': 1.0, 'fair': 2.0, 'overvalued': 3.0},
            'peg_ratio': {'undervalued': 0.8, 'fair': 1.0, 'overvalued': 1.5}
        }
    
    async def analyze_fundamentals(
        self, 
        symbol: str, 
        analysis_type: str = 'comprehensive',
        include_forecasting: bool = True,
        include_peer_comparison: bool = True
    ) -> Dict[str, Any]:
        """Analyze fundamentals untuk symbol"""
        try:
            # Get company data
            company_data = await self._get_company_data(symbol)
            if not company_data:
                return {'error': f'No data available for {symbol}'}
            
            # Get financial statements
            financial_statements = await self._get_financial_statements(symbol)
            if not financial_statements:
                return {'error': f'No financial statements available for {symbol}'}
            
            # Calculate financial ratios
            financial_ratios = await self._calculate_financial_ratios(financial_statements)
            
            # Calculate valuation metrics
            valuation_metrics = await self._calculate_valuation_metrics(symbol, financial_statements)
            
            # Perform DCF analysis
            dcf_analysis = await self._perform_dcf_analysis(symbol, financial_statements)
            
            # Calculate intrinsic value
            intrinsic_value = await self._calculate_intrinsic_value(symbol, financial_statements, dcf_analysis)
            
            # Generate investment recommendation
            investment_recommendation = await self._generate_investment_recommendation(
                symbol, financial_ratios, valuation_metrics, intrinsic_value
            )
            
            # Peer comparison
            peer_comparison = None
            if include_peer_comparison:
                peer_comparison = await self._perform_peer_comparison(symbol, financial_ratios, valuation_metrics)
            
            # Forecasting
            forecasting = None
            if include_forecasting:
                forecasting = await self._perform_forecasting(symbol, financial_statements)
            
            # Risk assessment
            risk_assessment = await self._assess_financial_risk(symbol, financial_ratios, financial_statements)
            
            return {
                'success': True,
                'symbol': symbol,
                'analysis_type': analysis_type,
                'company_data': company_data,
                'financial_ratios': financial_ratios,
                'valuation_metrics': valuation_metrics,
                'dcf_analysis': dcf_analysis,
                'intrinsic_value': intrinsic_value,
                'investment_recommendation': investment_recommendation,
                'peer_comparison': peer_comparison,
                'forecasting': forecasting,
                'risk_assessment': risk_assessment,
                'analysis_timestamp': datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing fundamentals: {e}")
            return {'error': str(e)}
    
    async def _get_company_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get company basic data"""
        try:
            # Try to get from database first
            fundamental_data = self.db.query(FundamentalData).filter(
                FundamentalData.symbol == symbol
            ).first()
            
            if fundamental_data:
                return {
                    'symbol': fundamental_data.symbol,
                    'company_name': fundamental_data.company_name,
                    'sector': fundamental_data.sector,
                    'industry': fundamental_data.industry,
                    'market_cap': fundamental_data.market_cap,
                    'employees': fundamental_data.employees,
                    'description': fundamental_data.description
                }
            
            # If not in database, get from Yahoo Finance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            company_data = {
                'symbol': symbol,
                'company_name': info.get('longName', ''),
                'sector': info.get('sector', ''),
                'industry': info.get('industry', ''),
                'market_cap': info.get('marketCap', 0),
                'employees': info.get('fullTimeEmployees', 0),
                'description': info.get('longBusinessSummary', '')
            }
            
            # Store in database
            await self._store_company_data(company_data)
            
            return company_data
            
        except Exception as e:
            logger.error(f"Error getting company data: {e}")
            return None
    
    async def _get_financial_statements(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get financial statements"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get financial statements
            income_statement = ticker.financials
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            if income_statement.empty or balance_sheet.empty or cash_flow.empty:
                return None
            
            # Convert to dictionaries
            financial_statements = {
                'income_statement': income_statement.to_dict(),
                'balance_sheet': balance_sheet.to_dict(),
                'cash_flow': cash_flow.to_dict(),
                'latest_year': income_statement.columns[0].year if not income_statement.empty else None
            }
            
            return financial_statements
            
        except Exception as e:
            logger.error(f"Error getting financial statements: {e}")
            return None
    
    async def _calculate_financial_ratios(self, financial_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate comprehensive financial ratios"""
        try:
            income_statement = financial_statements['income_statement']
            balance_sheet = financial_statements['balance_sheet']
            cash_flow = financial_statements['cash_flow']
            
            # Get latest year data
            latest_year = financial_statements['latest_year']
            if not latest_year:
                return {}
            
            # Extract key financial data
            revenue = self._extract_financial_data(income_statement, 'Total Revenue', latest_year)
            net_income = self._extract_financial_data(income_statement, 'Net Income', latest_year)
            gross_profit = self._extract_financial_data(income_statement, 'Gross Profit', latest_year)
            operating_income = self._extract_financial_data(income_statement, 'Operating Income', latest_year)
            
            total_assets = self._extract_financial_data(balance_sheet, 'Total Assets', latest_year)
            total_liabilities = self._extract_financial_data(balance_sheet, 'Total Liabilities', latest_year)
            total_equity = self._extract_financial_data(balance_sheet, 'Total Stockholder Equity', latest_year)
            current_assets = self._extract_financial_data(balance_sheet, 'Total Current Assets', latest_year)
            current_liabilities = self._extract_financial_data(balance_sheet, 'Total Current Liabilities', latest_year)
            cash = self._extract_financial_data(balance_sheet, 'Cash And Cash Equivalents', latest_year)
            
            # Calculate profitability ratios
            gross_margin = gross_profit / revenue if revenue > 0 else 0
            operating_margin = operating_income / revenue if revenue > 0 else 0
            net_margin = net_income / revenue if revenue > 0 else 0
            roa = net_income / total_assets if total_assets > 0 else 0
            roe = net_income / total_equity if total_equity > 0 else 0
            
            # Calculate liquidity ratios
            current_ratio = current_assets / current_liabilities if current_liabilities > 0 else 0
            quick_ratio = (current_assets - cash) / current_liabilities if current_liabilities > 0 else 0
            
            # Calculate leverage ratios
            debt_to_equity = total_liabilities / total_equity if total_equity > 0 else 0
            debt_to_assets = total_liabilities / total_assets if total_assets > 0 else 0
            
            # Calculate efficiency ratios
            asset_turnover = revenue / total_assets if total_assets > 0 else 0
            equity_turnover = revenue / total_equity if total_equity > 0 else 0
            
            # Calculate growth ratios
            growth_ratios = await self._calculate_growth_ratios(income_statement)
            
            # Calculate cash flow ratios
            operating_cash_flow = self._extract_financial_data(cash_flow, 'Total Cash From Operating Activities', latest_year)
            free_cash_flow = self._extract_financial_data(cash_flow, 'Free Cash Flow', latest_year)
            
            cash_flow_margin = operating_cash_flow / revenue if revenue > 0 else 0
            free_cash_flow_margin = free_cash_flow / revenue if revenue > 0 else 0
            
            ratios = {
                'profitability': {
                    'gross_margin': gross_margin,
                    'operating_margin': operating_margin,
                    'net_margin': net_margin,
                    'roa': roa,
                    'roe': roe
                },
                'liquidity': {
                    'current_ratio': current_ratio,
                    'quick_ratio': quick_ratio
                },
                'leverage': {
                    'debt_to_equity': debt_to_equity,
                    'debt_to_assets': debt_to_assets
                },
                'efficiency': {
                    'asset_turnover': asset_turnover,
                    'equity_turnover': equity_turnover
                },
                'growth': growth_ratios,
                'cash_flow': {
                    'cash_flow_margin': cash_flow_margin,
                    'free_cash_flow_margin': free_cash_flow_margin
                }
            }
            
            # Add quality scores
            ratios['quality_scores'] = await self._calculate_quality_scores(ratios)
            
            return ratios
            
        except Exception as e:
            logger.error(f"Error calculating financial ratios: {e}")
            return {}
    
    def _extract_financial_data(self, financial_data: Dict, key: str, year: int) -> float:
        """Extract financial data for specific year"""
        try:
            if key in financial_data:
                data = financial_data[key]
                if year in data:
                    return float(data[year])
            return 0.0
        except:
            return 0.0
    
    async def _calculate_growth_ratios(self, income_statement: Dict) -> Dict[str, float]:
        """Calculate growth ratios"""
        try:
            revenue_data = income_statement.get('Total Revenue', {})
            net_income_data = income_statement.get('Net Income', {})
            
            # Get years
            years = sorted(revenue_data.keys(), reverse=True)
            if len(years) < 2:
                return {}
            
            # Calculate growth rates
            revenue_growth = 0
            net_income_growth = 0
            
            if len(years) >= 2:
                current_revenue = revenue_data[years[0]]
                previous_revenue = revenue_data[years[1]]
                if previous_revenue > 0:
                    revenue_growth = (current_revenue - previous_revenue) / previous_revenue
            
            if len(years) >= 2:
                current_net_income = net_income_data[years[0]]
                previous_net_income = net_income_data[years[1]]
                if previous_net_income > 0:
                    net_income_growth = (current_net_income - previous_net_income) / previous_net_income
            
            return {
                'revenue_growth': revenue_growth,
                'net_income_growth': net_income_growth
            }
            
        except Exception as e:
            logger.error(f"Error calculating growth ratios: {e}")
            return {}
    
    async def _calculate_quality_scores(self, ratios: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality scores untuk ratios"""
        try:
            quality_scores = {}
            
            # Profitability quality
            profitability_score = 0
            profitability_ratios = ratios.get('profitability', {})
            
            for ratio_name, value in profitability_ratios.items():
                if ratio_name in self.ratio_thresholds:
                    thresholds = self.ratio_thresholds[ratio_name]
                    if value >= thresholds['good']:
                        profitability_score += 1
                    elif value >= thresholds['acceptable']:
                        profitability_score += 0.5
            
            quality_scores['profitability'] = profitability_score / len(profitability_ratios) if profitability_ratios else 0
            
            # Liquidity quality
            liquidity_score = 0
            liquidity_ratios = ratios.get('liquidity', {})
            
            for ratio_name, value in liquidity_ratios.items():
                if ratio_name in self.ratio_thresholds:
                    thresholds = self.ratio_thresholds[ratio_name]
                    if value >= thresholds['good']:
                        liquidity_score += 1
                    elif value >= thresholds['acceptable']:
                        liquidity_score += 0.5
            
            quality_scores['liquidity'] = liquidity_score / len(liquidity_ratios) if liquidity_ratios else 0
            
            # Overall quality score
            quality_scores['overall'] = (quality_scores['profitability'] + quality_scores['liquidity']) / 2
            
            return quality_scores
            
        except Exception as e:
            logger.error(f"Error calculating quality scores: {e}")
            return {}
    
    async def _calculate_valuation_metrics(self, symbol: str, financial_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate valuation metrics"""
        try:
            # Get current market data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            current_price = info.get('currentPrice', 0)
            market_cap = info.get('marketCap', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            
            # Get financial data
            income_statement = financial_statements['income_statement']
            balance_sheet = financial_statements['balance_sheet']
            
            latest_year = financial_statements['latest_year']
            net_income = self._extract_financial_data(income_statement, 'Net Income', latest_year)
            total_equity = self._extract_financial_data(balance_sheet, 'Total Stockholder Equity', latest_year)
            revenue = self._extract_financial_data(income_statement, 'Total Revenue', latest_year)
            
            # Calculate valuation ratios
            pe_ratio = market_cap / net_income if net_income > 0 else 0
            pb_ratio = market_cap / total_equity if total_equity > 0 else 0
            ps_ratio = market_cap / revenue if revenue > 0 else 0
            
            # Calculate PEG ratio (simplified)
            growth_rate = await self._calculate_growth_rate(income_statement)
            peg_ratio = pe_ratio / growth_rate if growth_rate > 0 else 0
            
            # Calculate EV/EBITDA (simplified)
            ebitda = self._extract_financial_data(income_statement, 'EBITDA', latest_year)
            ev_ebitda = market_cap / ebitda if ebitda > 0 else 0
            
            # Calculate price-to-cash-flow
            operating_cash_flow = self._extract_financial_data(financial_statements['cash_flow'], 'Total Cash From Operating Activities', latest_year)
            price_to_cash_flow = market_cap / operating_cash_flow if operating_cash_flow > 0 else 0
            
            valuation_metrics = {
                'pe_ratio': pe_ratio,
                'pb_ratio': pb_ratio,
                'ps_ratio': ps_ratio,
                'peg_ratio': peg_ratio,
                'ev_ebitda': ev_ebitda,
                'price_to_cash_flow': price_to_cash_flow,
                'current_price': current_price,
                'market_cap': market_cap
            }
            
            # Add valuation assessment
            valuation_metrics['assessment'] = await self._assess_valuation(valuation_metrics)
            
            return valuation_metrics
            
        except Exception as e:
            logger.error(f"Error calculating valuation metrics: {e}")
            return {}
    
    async def _calculate_growth_rate(self, income_statement: Dict) -> float:
        """Calculate growth rate"""
        try:
            revenue_data = income_statement.get('Total Revenue', {})
            years = sorted(revenue_data.keys(), reverse=True)
            
            if len(years) < 2:
                return 0.0
            
            current_revenue = revenue_data[years[0]]
            previous_revenue = revenue_data[years[1]]
            
            if previous_revenue > 0:
                return (current_revenue - previous_revenue) / previous_revenue
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating growth rate: {e}")
            return 0.0
    
    async def _assess_valuation(self, valuation_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Assess valuation attractiveness"""
        try:
            assessment = {
                'pe_assessment': 'fair',
                'pb_assessment': 'fair',
                'ps_assessment': 'fair',
                'overall_assessment': 'fair',
                'score': 0
            }
            
            score = 0
            
            # PE ratio assessment
            pe_ratio = valuation_metrics.get('pe_ratio', 0)
            if pe_ratio <= self.valuation_thresholds['pe_ratio']['undervalued']:
                assessment['pe_assessment'] = 'undervalued'
                score += 1
            elif pe_ratio >= self.valuation_thresholds['pe_ratio']['overvalued']:
                assessment['pe_assessment'] = 'overvalued'
                score -= 1
            
            # PB ratio assessment
            pb_ratio = valuation_metrics.get('pb_ratio', 0)
            if pb_ratio <= self.valuation_thresholds['pb_ratio']['undervalued']:
                assessment['pb_assessment'] = 'undervalued'
                score += 1
            elif pb_ratio >= self.valuation_thresholds['pb_ratio']['overvalued']:
                assessment['pb_assessment'] = 'overvalued'
                score -= 1
            
            # PS ratio assessment
            ps_ratio = valuation_metrics.get('ps_ratio', 0)
            if ps_ratio <= self.valuation_thresholds['ps_ratio']['undervalued']:
                assessment['ps_assessment'] = 'undervalued'
                score += 1
            elif ps_ratio >= self.valuation_thresholds['ps_ratio']['overvalued']:
                assessment['ps_assessment'] = 'overvalued'
                score -= 1
            
            # Overall assessment
            if score >= 2:
                assessment['overall_assessment'] = 'undervalued'
            elif score <= -2:
                assessment['overall_assessment'] = 'overvalued'
            
            assessment['score'] = score
            
            return assessment
            
        except Exception as e:
            logger.error(f"Error assessing valuation: {e}")
            return {'overall_assessment': 'fair', 'score': 0}
    
    async def _perform_dcf_analysis(self, symbol: str, financial_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Perform DCF analysis"""
        try:
            # Get financial data
            income_statement = financial_statements['income_statement']
            cash_flow = financial_statements['cash_flow']
            
            latest_year = financial_statements['latest_year']
            free_cash_flow = self._extract_financial_data(cash_flow, 'Free Cash Flow', latest_year)
            revenue = self._extract_financial_data(income_statement, 'Total Revenue', latest_year)
            
            # Calculate growth rate
            growth_rate = await self._calculate_growth_rate(income_statement)
            
            # DCF parameters
            discount_rate = 0.10  # 10% discount rate
            terminal_growth_rate = 0.03  # 3% terminal growth
            projection_years = 5
            
            # Project future cash flows
            projected_cash_flows = []
            current_fcf = free_cash_flow
            
            for year in range(1, projection_years + 1):
                if year == 1:
                    projected_fcf = current_fcf * (1 + growth_rate)
                else:
                    # Gradually reduce growth rate
                    adjusted_growth = growth_rate * (1 - (year - 1) * 0.1)
                    projected_fcf = projected_cash_flows[-1] * (1 + adjusted_growth)
                
                projected_cash_flows.append(projected_fcf)
            
            # Calculate present value of projected cash flows
            pv_cash_flows = []
            for i, cf in enumerate(projected_cash_flows):
                pv = cf / ((1 + discount_rate) ** (i + 1))
                pv_cash_flows.append(pv)
            
            # Calculate terminal value
            terminal_fcf = projected_cash_flows[-1] * (1 + terminal_growth_rate)
            terminal_value = terminal_fcf / (discount_rate - terminal_growth_rate)
            pv_terminal_value = terminal_value / ((1 + discount_rate) ** projection_years)
            
            # Calculate enterprise value
            enterprise_value = sum(pv_cash_flows) + pv_terminal_value
            
            # Calculate equity value (simplified)
            equity_value = enterprise_value  # Assuming no debt
            
            # Calculate fair value per share
            shares_outstanding = self._get_shares_outstanding(symbol)
            fair_value_per_share = equity_value / shares_outstanding if shares_outstanding > 0 else 0
            
            return {
                'enterprise_value': enterprise_value,
                'equity_value': equity_value,
                'fair_value_per_share': fair_value_per_share,
                'projected_cash_flows': projected_cash_flows,
                'terminal_value': terminal_value,
                'discount_rate': discount_rate,
                'terminal_growth_rate': terminal_growth_rate
            }
            
        except Exception as e:
            logger.error(f"Error performing DCF analysis: {e}")
            return {}
    
    def _get_shares_outstanding(self, symbol: str) -> float:
        """Get shares outstanding"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return info.get('sharesOutstanding', 0)
        except:
            return 0
    
    async def _calculate_intrinsic_value(self, symbol: str, financial_statements: Dict[str, Any], dcf_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate intrinsic value using multiple methods"""
        try:
            # Get current price
            ticker = yf.Ticker(symbol)
            info = ticker.info
            current_price = info.get('currentPrice', 0)
            
            # DCF intrinsic value
            dcf_value = dcf_analysis.get('fair_value_per_share', 0)
            
            # Graham intrinsic value (simplified)
            income_statement = financial_statements['income_statement']
            balance_sheet = financial_statements['balance_sheet']
            
            latest_year = financial_statements['latest_year']
            eps = self._extract_financial_data(income_statement, 'Net Income', latest_year) / self._get_shares_outstanding(symbol)
            book_value = self._extract_financial_data(balance_sheet, 'Total Stockholder Equity', latest_year) / self._get_shares_outstanding(symbol)
            
            # Graham formula: V = EPS * (8.5 + 2g) * 4.4 / Y
            growth_rate = await self._calculate_growth_rate(income_statement)
            graham_value = eps * (8.5 + 2 * growth_rate * 100) * 4.4 / 4.4  # Simplified
            
            # Average intrinsic value
            intrinsic_values = [dcf_value, graham_value]
            intrinsic_values = [v for v in intrinsic_values if v > 0]
            
            if intrinsic_values:
                average_intrinsic_value = sum(intrinsic_values) / len(intrinsic_values)
            else:
                average_intrinsic_value = current_price
            
            # Calculate margin of safety
            margin_of_safety = (average_intrinsic_value - current_price) / average_intrinsic_value if average_intrinsic_value > 0 else 0
            
            return {
                'dcf_value': dcf_value,
                'graham_value': graham_value,
                'average_intrinsic_value': average_intrinsic_value,
                'current_price': current_price,
                'margin_of_safety': margin_of_safety,
                'undervalued': margin_of_safety > 0.2,  # 20% margin of safety
                'overvalued': margin_of_safety < -0.2   # 20% overvaluation
            }
            
        except Exception as e:
            logger.error(f"Error calculating intrinsic value: {e}")
            return {}
    
    async def _generate_investment_recommendation(
        self, 
        symbol: str, 
        financial_ratios: Dict[str, Any], 
        valuation_metrics: Dict[str, Any], 
        intrinsic_value: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate investment recommendation"""
        try:
            recommendation = {
                'action': 'hold',
                'confidence': 'medium',
                'reasons': [],
                'risks': [],
                'score': 0
            }
            
            score = 0
            
            # Financial health assessment
            quality_scores = financial_ratios.get('quality_scores', {})
            overall_quality = quality_scores.get('overall', 0)
            
            if overall_quality >= 0.7:
                recommendation['reasons'].append('Strong financial health')
                score += 2
            elif overall_quality >= 0.5:
                recommendation['reasons'].append('Moderate financial health')
                score += 1
            else:
                recommendation['risks'].append('Weak financial health')
                score -= 1
            
            # Valuation assessment
            valuation_assessment = valuation_metrics.get('assessment', {})
            overall_valuation = valuation_assessment.get('overall_assessment', 'fair')
            
            if overall_valuation == 'undervalued':
                recommendation['reasons'].append('Undervalued based on metrics')
                score += 2
            elif overall_valuation == 'overvalued':
                recommendation['risks'].append('Overvalued based on metrics')
                score -= 2
            
            # Intrinsic value assessment
            if intrinsic_value.get('undervalued', False):
                recommendation['reasons'].append('Trading below intrinsic value')
                score += 2
            elif intrinsic_value.get('overvalued', False):
                recommendation['risks'].append('Trading above intrinsic value')
                score -= 2
            
            # Growth assessment
            growth_ratios = financial_ratios.get('growth', {})
            revenue_growth = growth_ratios.get('revenue_growth', 0)
            net_income_growth = growth_ratios.get('net_income_growth', 0)
            
            if revenue_growth > 0.1 and net_income_growth > 0.1:
                recommendation['reasons'].append('Strong growth metrics')
                score += 1
            elif revenue_growth < 0 or net_income_growth < 0:
                recommendation['risks'].append('Declining growth')
                score -= 1
            
            # Determine action
            if score >= 4:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = 'high'
            elif score >= 2:
                recommendation['action'] = 'buy'
                recommendation['confidence'] = 'medium'
            elif score <= -4:
                recommendation['action'] = 'sell'
                recommendation['confidence'] = 'high'
            elif score <= -2:
                recommendation['action'] = 'sell'
                recommendation['confidence'] = 'medium'
            else:
                recommendation['action'] = 'hold'
                recommendation['confidence'] = 'medium'
            
            recommendation['score'] = score
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating investment recommendation: {e}")
            return {'action': 'hold', 'confidence': 'low', 'reasons': [], 'risks': [], 'score': 0}
    
    async def _perform_peer_comparison(self, symbol: str, financial_ratios: Dict[str, Any], valuation_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Perform peer comparison"""
        try:
            # This would require sector/industry data
            # For now, return placeholder
            return {
                'peer_count': 0,
                'relative_performance': 'unknown',
                'sector_ranking': 'unknown'
            }
            
        except Exception as e:
            logger.error(f"Error performing peer comparison: {e}")
            return {}
    
    async def _perform_forecasting(self, symbol: str, financial_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Perform financial forecasting"""
        try:
            # This would implement forecasting models
            # For now, return placeholder
            return {
                'revenue_forecast': {},
                'earnings_forecast': {},
                'cash_flow_forecast': {}
            }
            
        except Exception as e:
            logger.error(f"Error performing forecasting: {e}")
            return {}
    
    async def _assess_financial_risk(self, symbol: str, financial_ratios: Dict[str, Any], financial_statements: Dict[str, Any]) -> Dict[str, Any]:
        """Assess financial risk"""
        try:
            risk_assessment = {
                'overall_risk': 'medium',
                'risk_factors': [],
                'risk_score': 0
            }
            
            score = 0
            
            # Liquidity risk
            liquidity_ratios = financial_ratios.get('liquidity', {})
            current_ratio = liquidity_ratios.get('current_ratio', 0)
            
            if current_ratio < 1.0:
                risk_assessment['risk_factors'].append('Low liquidity')
                score += 2
            elif current_ratio < 1.5:
                risk_assessment['risk_factors'].append('Moderate liquidity concerns')
                score += 1
            
            # Leverage risk
            leverage_ratios = financial_ratios.get('leverage', {})
            debt_to_equity = leverage_ratios.get('debt_to_equity', 0)
            
            if debt_to_equity > 1.0:
                risk_assessment['risk_factors'].append('High leverage')
                score += 2
            elif debt_to_equity > 0.6:
                risk_assessment['risk_factors'].append('Moderate leverage')
                score += 1
            
            # Profitability risk
            profitability_ratios = financial_ratios.get('profitability', {})
            net_margin = profitability_ratios.get('net_margin', 0)
            
            if net_margin < 0.03:
                risk_assessment['risk_factors'].append('Low profitability')
                score += 1
            
            # Determine overall risk
            if score >= 4:
                risk_assessment['overall_risk'] = 'high'
            elif score >= 2:
                risk_assessment['overall_risk'] = 'medium'
            else:
                risk_assessment['overall_risk'] = 'low'
            
            risk_assessment['risk_score'] = score
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Error assessing financial risk: {e}")
            return {'overall_risk': 'unknown', 'risk_factors': [], 'risk_score': 0}
    
    async def _store_company_data(self, company_data: Dict[str, Any]):
        """Store company data in database"""
        try:
            fundamental_data = FundamentalData(
                symbol=company_data['symbol'],
                company_name=company_data['company_name'],
                sector=company_data['sector'],
                industry=company_data['industry'],
                market_cap=company_data['market_cap'],
                employees=company_data['employees'],
                description=company_data['description'],
                created_at=datetime.now()
            )
            
            self.db.add(fundamental_data)
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error storing company data: {e}")
            self.db.rollback()
