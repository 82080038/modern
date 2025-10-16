"""
Fundamental Analysis Models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Date, BigInteger
from sqlalchemy.sql import func
from app.database import Base

class CompanyProfile(Base):
    """Company basic information"""
    __tablename__ = "company_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, nullable=False, index=True)
    company_name = Column(String(200), nullable=False)
    sector = Column(String(100), nullable=True)
    industry = Column(String(100), nullable=True)
    market_cap = Column(BigInteger, nullable=True)
    shares_outstanding = Column(BigInteger, nullable=True)
    website = Column(String(255), nullable=True)
    business_summary = Column(Text, nullable=True)
    employees = Column(Integer, nullable=True)
    listing_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class FinancialStatements(Base):
    """Financial statements data"""
    __tablename__ = "financial_statements"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    statement_type = Column(String(20), nullable=False)  # income, balance, cashflow
    period_type = Column(String(10), nullable=False)  # quarterly, annual
    period_date = Column(Date, nullable=False)
    
    # Income Statement
    revenue = Column(BigInteger, nullable=True)
    cost_of_revenue = Column(BigInteger, nullable=True)
    gross_profit = Column(BigInteger, nullable=True)
    operating_expenses = Column(BigInteger, nullable=True)
    operating_income = Column(BigInteger, nullable=True)
    interest_expense = Column(BigInteger, nullable=True)
    ebit = Column(BigInteger, nullable=True)
    ebitda = Column(BigInteger, nullable=True)
    net_income = Column(BigInteger, nullable=True)
    eps = Column(Float, nullable=True)
    
    # Balance Sheet
    total_assets = Column(BigInteger, nullable=True)
    current_assets = Column(BigInteger, nullable=True)
    cash_and_equivalents = Column(BigInteger, nullable=True)
    total_liabilities = Column(BigInteger, nullable=True)
    current_liabilities = Column(BigInteger, nullable=True)
    long_term_debt = Column(BigInteger, nullable=True)
    total_equity = Column(BigInteger, nullable=True)
    book_value_per_share = Column(Float, nullable=True)
    
    # Cash Flow
    operating_cash_flow = Column(BigInteger, nullable=True)
    investing_cash_flow = Column(BigInteger, nullable=True)
    financing_cash_flow = Column(BigInteger, nullable=True)
    free_cash_flow = Column(BigInteger, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FinancialRatios(Base):
    """Calculated financial ratios"""
    __tablename__ = "financial_ratios"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    period_date = Column(Date, nullable=False)
    
    # Profitability Ratios
    roe = Column(Float, nullable=True)  # Return on Equity
    roa = Column(Float, nullable=True)  # Return on Assets
    roic = Column(Float, nullable=True)  # Return on Invested Capital
    profit_margin = Column(Float, nullable=True)
    operating_margin = Column(Float, nullable=True)
    gross_margin = Column(Float, nullable=True)
    ebitda_margin = Column(Float, nullable=True)
    
    # Liquidity Ratios
    current_ratio = Column(Float, nullable=True)
    quick_ratio = Column(Float, nullable=True)
    cash_ratio = Column(Float, nullable=True)
    
    # Leverage Ratios
    debt_to_equity = Column(Float, nullable=True)
    debt_to_assets = Column(Float, nullable=True)
    interest_coverage = Column(Float, nullable=True)
    debt_service_coverage = Column(Float, nullable=True)
    
    # Efficiency Ratios
    asset_turnover = Column(Float, nullable=True)
    inventory_turnover = Column(Float, nullable=True)
    receivables_turnover = Column(Float, nullable=True)
    
    # Valuation Ratios
    pe_ratio = Column(Float, nullable=True)
    pb_ratio = Column(Float, nullable=True)
    ps_ratio = Column(Float, nullable=True)
    peg_ratio = Column(Float, nullable=True)
    ev_ebitda = Column(Float, nullable=True)
    ev_sales = Column(Float, nullable=True)
    dividend_yield = Column(Float, nullable=True)
    payout_ratio = Column(Float, nullable=True)
    
    # Growth Ratios
    revenue_growth_yoy = Column(Float, nullable=True)
    revenue_growth_qoq = Column(Float, nullable=True)
    eps_growth_yoy = Column(Float, nullable=True)
    eps_growth_qoq = Column(Float, nullable=True)
    book_value_growth = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DCFValuation(Base):
    """DCF valuation models"""
    __tablename__ = "dcf_valuations"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    valuation_date = Column(Date, nullable=False)
    
    # DCF Inputs
    terminal_growth_rate = Column(Float, nullable=True)
    discount_rate = Column(Float, nullable=True)
    forecast_periods = Column(Integer, nullable=True)
    
    # DCF Outputs
    intrinsic_value = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    margin_of_safety = Column(Float, nullable=True)
    upside_potential = Column(Float, nullable=True)
    
    # Graham Number
    graham_number = Column(Float, nullable=True)
    graham_upside = Column(Float, nullable=True)
    
    # Relative Valuation
    fair_value_pe = Column(Float, nullable=True)
    fair_value_pb = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class EarningsAnalysis(Base):
    """Earnings analysis and tracking"""
    __tablename__ = "earnings_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    earnings_date = Column(Date, nullable=False)
    period_type = Column(String(10), nullable=False)  # quarterly, annual
    
    # Earnings Data
    reported_eps = Column(Float, nullable=True)
    estimated_eps = Column(Float, nullable=True)
    eps_surprise = Column(Float, nullable=True)
    eps_surprise_pct = Column(Float, nullable=True)
    
    reported_revenue = Column(BigInteger, nullable=True)
    estimated_revenue = Column(BigInteger, nullable=True)
    revenue_surprise = Column(BigInteger, nullable=True)
    revenue_surprise_pct = Column(Float, nullable=True)
    
    # Quality Metrics
    earnings_quality_score = Column(Float, nullable=True)
    revenue_quality_score = Column(Float, nullable=True)
    consistency_score = Column(Float, nullable=True)
    
    # Growth Analysis
    eps_growth_3y = Column(Float, nullable=True)
    eps_growth_5y = Column(Float, nullable=True)
    revenue_growth_3y = Column(Float, nullable=True)
    revenue_growth_5y = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PeerComparison(Base):
    """Peer comparison analysis"""
    __tablename__ = "peer_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    comparison_date = Column(Date, nullable=False)
    sector = Column(String(100), nullable=False)
    
    # Peer Metrics
    pe_percentile = Column(Float, nullable=True)
    pb_percentile = Column(Float, nullable=True)
    roe_percentile = Column(Float, nullable=True)
    revenue_growth_percentile = Column(Float, nullable=True)
    
    # Relative Performance
    vs_sector_pe = Column(Float, nullable=True)
    vs_sector_pb = Column(Float, nullable=True)
    vs_sector_roe = Column(Float, nullable=True)
    vs_sector_growth = Column(Float, nullable=True)
    
    # Ranking
    pe_rank = Column(Integer, nullable=True)
    pb_rank = Column(Integer, nullable=True)
    roe_rank = Column(Integer, nullable=True)
    growth_rank = Column(Integer, nullable=True)
    overall_rank = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
