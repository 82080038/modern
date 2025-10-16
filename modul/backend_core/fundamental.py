"""
Fundamental Analysis Engine
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from app.models.fundamental import (
    CompanyProfile, FinancialStatements, FinancialRatios, 
    DCFValuation, EarningsAnalysis, PeerComparison
)
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class FundamentalAnalysisEngine:
    """Core engine for fundamental analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_financial_ratios(self, symbol: str, period_date: date) -> Dict:
        """Calculate comprehensive financial ratios"""
        try:
            # Get latest financial statements
            income_stmt = self.db.query(FinancialStatements).filter(
                FinancialStatements.symbol == symbol,
                FinancialStatements.statement_type == 'income',
                FinancialStatements.period_date <= period_date
            ).order_by(FinancialStatements.period_date.desc()).first()
            
            balance_sheet = self.db.query(FinancialStatements).filter(
                FinancialStatements.symbol == symbol,
                FinancialStatements.statement_type == 'balance',
                FinancialStatements.period_date <= period_date
            ).order_by(FinancialStatements.period_date.desc()).first()
            
            cash_flow = self.db.query(FinancialStatements).filter(
                FinancialStatements.symbol == symbol,
                FinancialStatements.statement_type == 'cashflow',
                FinancialStatements.period_date <= period_date
            ).order_by(FinancialStatements.period_date.desc()).first()
            
            if not all([income_stmt, balance_sheet, cash_flow]):
                return {"error": "Insufficient financial data"}
            
            ratios = {}
            
            # Profitability Ratios
            if balance_sheet.total_equity and income_stmt.net_income:
                ratios['roe'] = (income_stmt.net_income / balance_sheet.total_equity) * 100
            
            if balance_sheet.total_assets and income_stmt.net_income:
                ratios['roa'] = (income_stmt.net_income / balance_sheet.total_assets) * 100
            
            if income_stmt.revenue and income_stmt.net_income:
                ratios['profit_margin'] = (income_stmt.net_income / income_stmt.revenue) * 100
            
            if income_stmt.revenue and income_stmt.operating_income:
                ratios['operating_margin'] = (income_stmt.operating_income / income_stmt.revenue) * 100
            
            if income_stmt.revenue and income_stmt.gross_profit:
                ratios['gross_margin'] = (income_stmt.gross_profit / income_stmt.revenue) * 100
            
            # Liquidity Ratios
            if balance_sheet.current_liabilities and balance_sheet.current_assets:
                ratios['current_ratio'] = balance_sheet.current_assets / balance_sheet.current_liabilities
            
            if balance_sheet.current_liabilities and balance_sheet.cash_and_equivalents:
                ratios['cash_ratio'] = balance_sheet.cash_and_equivalents / balance_sheet.current_liabilities
            
            # Leverage Ratios
            if balance_sheet.total_equity and balance_sheet.total_liabilities:
                ratios['debt_to_equity'] = balance_sheet.total_liabilities / balance_sheet.total_equity
            
            if balance_sheet.total_assets and balance_sheet.total_liabilities:
                ratios['debt_to_assets'] = balance_sheet.total_liabilities / balance_sheet.total_assets
            
            # Efficiency Ratios
            if balance_sheet.total_assets and income_stmt.revenue:
                ratios['asset_turnover'] = income_stmt.revenue / balance_sheet.total_assets
            
            return ratios
            
        except Exception as e:
            logger.error(f"Error calculating ratios for {symbol}: {e}")
            return {"error": str(e)}
    
    def calculate_dcf_valuation(self, symbol: str, current_price: float) -> Dict:
        """Calculate DCF valuation"""
        try:
            # Get historical financial data
            statements = self.db.query(FinancialStatements).filter(
                FinancialStatements.symbol == symbol,
                FinancialStatements.statement_type == 'income'
            ).order_by(FinancialStatements.period_date.desc()).limit(5).all()
            
            if len(statements) < 3:
                return {"error": "Insufficient historical data for DCF"}
            
            # Calculate growth rates
            revenues = [s.revenue for s in statements if s.revenue]
            if len(revenues) >= 2:
                revenue_growth = (revenues[0] - revenues[1]) / revenues[1] if revenues[1] != 0 else 0
            else:
                revenue_growth = 0.05  # Default 5% growth
            
            # DCF Parameters
            terminal_growth_rate = 0.03  # 3% terminal growth
            discount_rate = 0.12  # 12% discount rate
            forecast_periods = 5
            
            # Project future cash flows
            latest_revenue = revenues[0] if revenues else 0
            latest_fcf = statements[0].free_cash_flow if statements[0].free_cash_flow else 0
            
            # Simple DCF calculation
            projected_fcf = []
            for year in range(1, forecast_periods + 1):
                fcf = latest_fcf * ((1 + revenue_growth) ** year)
                projected_fcf.append(fcf)
            
            # Calculate present value of projected cash flows
            pv_cash_flows = sum([
                fcf / ((1 + discount_rate) ** year) 
                for year, fcf in enumerate(projected_fcf, 1)
            ])
            
            # Terminal value
            terminal_value = (projected_fcf[-1] * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
            pv_terminal = terminal_value / ((1 + discount_rate) ** forecast_periods)
            
            # Enterprise value
            enterprise_value = pv_cash_flows + pv_terminal
            
            # Assume no net debt for simplicity
            equity_value = enterprise_value
            shares_outstanding = 1000000000  # Default 1B shares
            intrinsic_value = equity_value / shares_outstanding
            
            # Calculate metrics
            margin_of_safety = (intrinsic_value - current_price) / intrinsic_value if intrinsic_value > 0 else 0
            upside_potential = (intrinsic_value - current_price) / current_price if current_price > 0 else 0
            
            return {
                "intrinsic_value": intrinsic_value,
                "current_price": current_price,
                "margin_of_safety": margin_of_safety,
                "upside_potential": upside_potential,
                "terminal_growth_rate": terminal_growth_rate,
                "discount_rate": discount_rate,
                "enterprise_value": enterprise_value
            }
            
        except Exception as e:
            logger.error(f"Error calculating DCF for {symbol}: {e}")
            return {"error": str(e)}
    
    def calculate_graham_number(self, symbol: str) -> Dict:
        """Calculate Graham Number (value investing metric)"""
        try:
            # Get latest financial data
            latest_income = self.db.query(FinancialStatements).filter(
                FinancialStatements.symbol == symbol,
                FinancialStatements.statement_type == 'income'
            ).order_by(FinancialStatements.period_date.desc()).first()
            
            latest_balance = self.db.query(FinancialStatements).filter(
                FinancialStatements.symbol == symbol,
                FinancialStatements.statement_type == 'balance'
            ).order_by(FinancialStatements.period_date.desc()).first()
            
            if not latest_income or not latest_balance:
                return {"error": "Insufficient data for Graham Number"}
            
            eps = latest_income.eps
            book_value_per_share = latest_balance.book_value_per_share
            
            if not eps or not book_value_per_share or eps <= 0 or book_value_per_share <= 0:
                return {"error": "Invalid EPS or Book Value"}
            
            # Graham Number = sqrt(22.5 * EPS * Book Value per Share)
            graham_number = np.sqrt(22.5 * eps * book_value_per_share)
            
            return {
                "graham_number": graham_number,
                "eps": eps,
                "book_value_per_share": book_value_per_share,
                "formula": "sqrt(22.5 * EPS * BVPS)"
            }
            
        except Exception as e:
            logger.error(f"Error calculating Graham Number for {symbol}: {e}")
            return {"error": str(e)}
    
    def analyze_earnings_quality(self, symbol: str) -> Dict:
        """Analyze earnings quality and consistency"""
        try:
            # Get historical earnings
            earnings = self.db.query(EarningsAnalysis).filter(
                EarningsAnalysis.symbol == symbol
            ).order_by(EarningsAnalysis.earnings_date.desc()).limit(12).all()
            
            if len(earnings) < 4:
                return {"error": "Insufficient earnings history"}
            
            eps_data = [e.reported_eps for e in earnings if e.reported_eps]
            revenue_data = [e.reported_revenue for e in earnings if e.reported_revenue]
            
            if len(eps_data) < 4:
                return {"error": "Insufficient EPS data"}
            
            # Calculate growth rates
            eps_growth_rates = []
            for i in range(1, len(eps_data)):
                if eps_data[i-1] != 0:
                    growth = (eps_data[i] - eps_data[i-1]) / abs(eps_data[i-1])
                    eps_growth_rates.append(growth)
            
            # Calculate consistency metrics
            eps_std = np.std(eps_growth_rates) if eps_growth_rates else 0
            eps_mean = np.mean(eps_growth_rates) if eps_growth_rates else 0
            
            # Quality score (lower std = higher quality)
            quality_score = max(0, 1 - (eps_std / 0.5))  # Normalize to 0-1
            
            # Consistency score
            positive_quarters = sum(1 for rate in eps_growth_rates if rate > 0)
            consistency_score = positive_quarters / len(eps_growth_rates) if eps_growth_rates else 0
            
            return {
                "eps_growth_avg": eps_mean,
                "eps_growth_std": eps_std,
                "quality_score": quality_score,
                "consistency_score": consistency_score,
                "positive_quarters": positive_quarters,
                "total_quarters": len(eps_growth_rates)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing earnings quality for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_peer_comparison(self, symbol: str, sector: str) -> Dict:
        """Compare company against sector peers"""
        try:
            # Get company ratios
            company_ratios = self.db.query(FinancialRatios).filter(
                FinancialRatios.symbol == symbol
            ).order_by(FinancialRatios.period_date.desc()).first()
            
            if not company_ratios:
                return {"error": "No financial ratios found for company"}
            
            # Get sector peers
            peer_ratios = self.db.query(FinancialRatios).join(CompanyProfile).filter(
                CompanyProfile.sector == sector,
                FinancialRatios.symbol != symbol
            ).all()
            
            if not peer_ratios:
                return {"error": "No peer data found"}
            
            # Calculate sector averages
            pe_ratios = [p.pe_ratio for p in peer_ratios if p.pe_ratio and p.pe_ratio > 0]
            pb_ratios = [p.pb_ratio for p in peer_ratios if p.pb_ratio and p.pb_ratio > 0]
            roe_values = [p.roe for p in peer_ratios if p.roe]
            
            sector_avg_pe = np.mean(pe_ratios) if pe_ratios else 0
            sector_avg_pb = np.mean(pb_ratios) if pb_ratios else 0
            sector_avg_roe = np.mean(roe_values) if roe_values else 0
            
            # Calculate relative metrics
            company_pe = company_ratios.pe_ratio if company_ratios.pe_ratio else 0
            company_pb = company_ratios.pb_ratio if company_ratios.pb_ratio else 0
            company_roe = company_ratios.roe if company_ratios.roe else 0
            
            vs_sector_pe = (company_pe - sector_avg_pe) / sector_avg_pe if sector_avg_pe > 0 else 0
            vs_sector_pb = (company_pb - sector_avg_pb) / sector_avg_pb if sector_avg_pb > 0 else 0
            vs_sector_roe = (company_roe - sector_avg_roe) / sector_avg_roe if sector_avg_roe > 0 else 0
            
            return {
                "company_pe": company_pe,
                "sector_avg_pe": sector_avg_pe,
                "vs_sector_pe": vs_sector_pe,
                "company_pb": company_pb,
                "sector_avg_pb": sector_avg_pb,
                "vs_sector_pb": vs_sector_pb,
                "company_roe": company_roe,
                "sector_avg_roe": sector_avg_roe,
                "vs_sector_roe": vs_sector_roe,
                "peer_count": len(peer_ratios)
            }
            
        except Exception as e:
            logger.error(f"Error in peer comparison for {symbol}: {e}")
            return {"error": str(e)}
    
    def get_fundamental_score(self, symbol: str) -> Dict:
        """Calculate overall fundamental score (0-100)"""
        try:
            # Get latest ratios
            ratios = self.db.query(FinancialRatios).filter(
                FinancialRatios.symbol == symbol
            ).order_by(FinancialRatios.period_date.desc()).first()
            
            if not ratios:
                return {"error": "No financial ratios found"}
            
            score = 0
            max_score = 100
            factors = []
            
            # Profitability (30 points)
            if ratios.roe and ratios.roe > 0:
                roe_score = min(30, ratios.roe * 2)  # 15% ROE = 30 points
                score += roe_score
                factors.append(f"ROE: {ratios.roe:.1f}% (+{roe_score:.1f} points)")
            
            # Growth (25 points)
            if ratios.eps_growth_yoy and ratios.eps_growth_yoy > 0:
                growth_score = min(25, ratios.eps_growth_yoy * 5)  # 5% growth = 25 points
                score += growth_score
                factors.append(f"EPS Growth: {ratios.eps_growth_yoy:.1f}% (+{growth_score:.1f} points)")
            
            # Valuation (20 points)
            if ratios.pe_ratio and ratios.pe_ratio > 0:
                # Lower PE is better (value)
                pe_score = max(0, 20 - (ratios.pe_ratio - 10) * 2)  # PE 10 = 20 points
                score += pe_score
                factors.append(f"PE Ratio: {ratios.pe_ratio:.1f} (+{pe_score:.1f} points)")
            
            # Financial Health (15 points)
            if ratios.debt_to_equity and ratios.debt_to_equity >= 0:
                debt_score = max(0, 15 - ratios.debt_to_equity * 10)  # 0 debt = 15 points
                score += debt_score
                factors.append(f"Debt/Equity: {ratios.debt_to_equity:.2f} (+{debt_score:.1f} points)")
            
            # Liquidity (10 points)
            if ratios.current_ratio and ratios.current_ratio > 0:
                liquidity_score = min(10, ratios.current_ratio * 5)  # 2.0 ratio = 10 points
                score += liquidity_score
                factors.append(f"Current Ratio: {ratios.current_ratio:.2f} (+{liquidity_score:.1f} points)")
            
            # Normalize to 0-100
            score = min(100, max(0, score))
            
            # Determine rating
            if score >= 80:
                rating = "Excellent"
            elif score >= 60:
                rating = "Good"
            elif score >= 40:
                rating = "Fair"
            else:
                rating = "Poor"
            
            return {
                "fundamental_score": score,
                "rating": rating,
                "factors": factors,
                "max_possible": max_score
            }
            
        except Exception as e:
            logger.error(f"Error calculating fundamental score for {symbol}: {e}")
            return {"error": str(e)}
