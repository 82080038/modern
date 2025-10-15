"""
Tax API Endpoints untuk FIFO/LIFO Tracking (Indonesia Format)
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import date
from app.database import get_db
from app.services.tax_service import TaxService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/tax", tags=["Tax"])

# Pydantic schemas
class CreateTaxLotRequest(BaseModel):
    symbol: str
    position_id: int
    quantity: int
    cost_basis: float
    purchase_date: date
    lot_type: str = "FIFO"  # FIFO or LIFO

class CalculateSaleTaxRequest(BaseModel):
    symbol: str
    sell_quantity: int
    sell_price: float
    method: str = "FIFO"  # FIFO or LIFO

class CalculateDividendTaxRequest(BaseModel):
    symbol: str
    dividend_amount: float
    shares_owned: int

class TaxSummaryResponse(BaseModel):
    symbol: str
    year: str
    total_lots: int
    total_quantity: int
    total_cost_basis: float
    total_sold_quantity: int
    total_capital_gain: float
    total_tax_liability: float
    symbol_breakdown: Optional[Dict] = None

class TaxReportResponse(BaseModel):
    year: int
    symbol: str
    tax_summary: Dict
    trading_summary: Dict
    tax_obligations: Dict
    recommendations: List[str]

@router.post("/lots")
async def create_tax_lot(
    lot_request: CreateTaxLotRequest,
    db: Session = Depends(get_db)
):
    """Create tax lot untuk FIFO/LIFO tracking"""
    try:
        # Validate lot type
        if lot_request.lot_type not in ["FIFO", "LIFO"]:
            raise HTTPException(status_code=400, detail="Invalid lot type. Must be FIFO or LIFO")
        
        # Create tax service
        tax_service = TaxService(db)
        
        # Create tax lot
        result = tax_service.create_tax_lot(
            symbol=lot_request.symbol,
            position_id=lot_request.position_id,
            quantity=lot_request.quantity,
            cost_basis=lot_request.cost_basis,
            purchase_date=lot_request.purchase_date,
            lot_type=lot_request.lot_type
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating tax lot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-sale")
async def calculate_sale_tax(
    sale_request: CalculateSaleTaxRequest,
    db: Session = Depends(get_db)
):
    """Calculate tax liability untuk sale"""
    try:
        # Validate method
        if sale_request.method not in ["FIFO", "LIFO"]:
            raise HTTPException(status_code=400, detail="Invalid method. Must be FIFO or LIFO")
        
        # Create tax service
        tax_service = TaxService(db)
        
        # Calculate sale tax
        result = tax_service.calculate_sale_tax_liability(
            symbol=sale_request.symbol,
            sell_quantity=sale_request.sell_quantity,
            sell_price=sale_request.sell_price,
            method=sale_request.method
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating sale tax: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/calculate-dividend")
async def calculate_dividend_tax(
    dividend_request: CalculateDividendTaxRequest,
    db: Session = Depends(get_db)
):
    """Calculate dividend tax"""
    try:
        # Create tax service
        tax_service = TaxService(db)
        
        # Calculate dividend tax
        result = tax_service.calculate_dividend_tax(
            symbol=dividend_request.symbol,
            dividend_amount=dividend_request.dividend_amount,
            shares_owned=dividend_request.shares_owned
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating dividend tax: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary", response_model=TaxSummaryResponse)
async def get_tax_summary(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    year: Optional[int] = Query(None, description="Filter by year"),
    db: Session = Depends(get_db)
):
    """Get tax summary"""
    try:
        tax_service = TaxService(db)
        summary = tax_service.get_tax_summary(symbol=symbol, year=year)
        
        if "error" in summary:
            raise HTTPException(status_code=400, detail=summary["error"])
        
        return TaxSummaryResponse(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/lots")
async def get_tax_lots(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    position_id: Optional[int] = Query(None, description="Filter by position ID"),
    db: Session = Depends(get_db)
):
    """Get tax lots"""
    try:
        tax_service = TaxService(db)
        lots = tax_service.get_tax_lots(symbol=symbol, position_id=position_id)
        
        return {
            "tax_lots": lots,
            "total_count": len(lots)
        }
        
    except Exception as e:
        logger.error(f"Error getting tax lots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{year}", response_model=TaxReportResponse)
async def generate_tax_report(
    year: int,
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    db: Session = Depends(get_db)
):
    """Generate comprehensive tax report"""
    try:
        # Validate year
        current_year = date.today().year
        if year < 2020 or year > current_year:
            raise HTTPException(status_code=400, detail=f"Invalid year. Must be between 2020 and {current_year}")
        
        tax_service = TaxService(db)
        report = tax_service.generate_tax_report(year=year, symbol=symbol)
        
        if "error" in report:
            raise HTTPException(status_code=400, detail=report["error"])
        
        return TaxReportResponse(**report)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating tax report: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rates")
async def get_tax_rates(db: Session = Depends(get_db)):
    """Get current tax rates"""
    try:
        tax_service = TaxService(db)
        
        return {
            "stock_transaction_tax_rate": float(tax_service.stock_transaction_tax_rate),
            "capital_gains_tax_rate": float(tax_service.capital_gains_tax_rate),
            "dividend_tax_rate": float(tax_service.dividend_tax_rate),
            "currency": "IDR",
            "description": "Indonesian tax rates for stock transactions"
        }
        
    except Exception as e:
        logger.error(f"Error getting tax rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/rates")
async def update_tax_rates(
    stock_transaction_rate: Optional[float] = Body(None, description="Stock transaction tax rate"),
    capital_gains_rate: Optional[float] = Body(None, description="Capital gains tax rate"),
    dividend_rate: Optional[float] = Body(None, description="Dividend tax rate"),
    db: Session = Depends(get_db)
):
    """Update tax rates"""
    try:
        tax_service = TaxService(db)
        result = tax_service.update_tax_rates(
            stock_transaction_rate=stock_transaction_rate,
            capital_gains_rate=capital_gains_rate,
            dividend_rate=dividend_rate
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating tax rates: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/positions/{symbol}")
async def get_position_tax_info(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get tax information for a specific position"""
    try:
        tax_service = TaxService(db)
        
        # Get tax lots for symbol
        tax_lots = tax_service.get_tax_lots(symbol=symbol)
        
        # Get tax summary for symbol
        tax_summary = tax_service.get_tax_summary(symbol=symbol)
        
        if "error" in tax_summary:
            raise HTTPException(status_code=400, detail=tax_summary["error"])
        
        # Calculate unrealized P&L
        from app.models.trading import Position
        position = db.query(Position).filter(Position.symbol == symbol.upper()).first()
        
        unrealized_pnl = 0.0
        if position:
            unrealized_pnl = (position.current_price - position.average_price) * position.quantity
        
        return {
            "symbol": symbol.upper(),
            "tax_lots": tax_lots,
            "tax_summary": tax_summary,
            "position_info": {
                "quantity": position.quantity if position else 0,
                "average_price": position.average_price if position else 0,
                "current_price": position.current_price if position else 0,
                "unrealized_pnl": unrealized_pnl
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting position tax info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/obligations")
async def get_tax_obligations(
    year: Optional[int] = Query(None, description="Filter by year"),
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    db: Session = Depends(get_db)
):
    """Get tax obligations summary"""
    try:
        tax_service = TaxService(db)
        
        # Get tax summary
        tax_summary = tax_service.get_tax_summary(symbol=symbol, year=year)
        
        if "error" in tax_summary:
            raise HTTPException(status_code=400, detail=tax_summary["error"])
        
        # Calculate total obligations
        total_obligations = tax_summary["total_tax_liability"]
        
        # Get recent trades for context
        from app.models.trading import Trade
        from datetime import datetime
        
        query = db.query(Trade)
        if year:
            query = query.filter(
                Trade.executed_at >= datetime(year, 1, 1),
                Trade.executed_at <= datetime(year, 12, 31)
            )
        if symbol:
            query = query.filter(Trade.symbol == symbol.upper())
        
        trades = query.all()
        total_trades = len(trades)
        total_volume = sum(trade.quantity * trade.price for trade in trades)
        
        return {
            "year": year or "All",
            "symbol": symbol or "All",
            "total_tax_obligations": float(total_obligations),
            "trading_activity": {
                "total_trades": total_trades,
                "total_volume": float(total_volume)
            },
            "tax_breakdown": {
                "transaction_tax": float(total_obligations),
                "capital_gains_tax": 0.0,  # Would need more complex calculation
                "dividend_tax": 0.0  # Would need dividend data
            },
            "recommendations": [
                "Ensure all transactions are properly documented",
                "Consider tax-loss harvesting strategies",
                "Keep records for at least 5 years as required by Indonesian tax law"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tax obligations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
