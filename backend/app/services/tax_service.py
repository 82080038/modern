"""
Tax Service untuk FIFO/LIFO Tracking (Indonesia Format)
"""
from sqlalchemy.orm import Session
from app.models.trading import TaxLot, Position, Trade
from app.models.security import User
from typing import Dict, List, Optional, Tuple
from datetime import datetime, date
import logging
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)

class TaxService:
    """Service untuk tax calculations dan tracking (Indonesia format)"""
    
    def __init__(self, db: Session):
        self.db = db
        # Indonesian tax rates
        self.stock_transaction_tax_rate = Decimal('0.001')  # 0.1% untuk transaksi saham
        self.capital_gains_tax_rate = Decimal('0.1')  # 10% untuk capital gains (jika applicable)
        self.dividend_tax_rate = Decimal('0.1')  # 10% untuk dividen
    
    def create_tax_lot(self, 
                       symbol: str,
                       position_id: int,
                       quantity: int,
                       cost_basis: float,
                       purchase_date: date,
                       lot_type: str = "FIFO") -> Dict:
        """Create tax lot untuk FIFO/LIFO tracking"""
        try:
            # Validate lot type
            if lot_type not in ["FIFO", "LIFO"]:
                return {"error": "Invalid lot type. Must be FIFO or LIFO"}
            
            # Create tax lot
            tax_lot = TaxLot(
                symbol=symbol.upper(),
                position_id=position_id,
                quantity=quantity,
                cost_basis=Decimal(str(cost_basis)),
                purchase_date=purchase_date,
                remaining_quantity=quantity,
                sold_quantity=0,
                capital_gain=Decimal('0'),
                tax_liability=Decimal('0')
            )
            
            self.db.add(tax_lot)
            self.db.commit()
            
            return {
                "tax_lot_id": tax_lot.id,
                "symbol": symbol,
                "quantity": quantity,
                "cost_basis": float(cost_basis),
                "lot_type": lot_type,
                "message": "Tax lot created successfully"
            }
            
        except Exception as e:
            logger.error(f"Error creating tax lot: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def calculate_sale_tax_liability(self, 
                                   symbol: str,
                                   sell_quantity: int,
                                   sell_price: float,
                                   method: str = "FIFO") -> Dict:
        """Calculate tax liability untuk sale menggunakan FIFO/LIFO"""
        try:
            # Get tax lots untuk symbol
            tax_lots = self.db.query(TaxLot).filter(
                TaxLot.symbol == symbol.upper(),
                TaxLot.remaining_quantity > 0
            ).order_by(
                TaxLot.purchase_date.asc() if method == "FIFO" else TaxLot.purchase_date.desc()
            ).all()
            
            if not tax_lots:
                return {"error": f"No tax lots found for {symbol}"}
            
            total_cost_basis = Decimal('0')
            total_proceeds = Decimal(str(sell_price)) * sell_quantity
            remaining_sell = sell_quantity
            lots_used = []
            
            # Process lots according to method
            for lot in tax_lots:
                if remaining_sell <= 0:
                    break
                
                # Calculate quantity to sell from this lot
                sell_from_lot = min(remaining_sell, lot.remaining_quantity)
                lot_cost_basis = lot.cost_basis * sell_from_lot
                lot_proceeds = Decimal(str(sell_price)) * sell_from_lot
                lot_capital_gain = lot_proceeds - lot_cost_basis
                
                # Update lot
                lot.remaining_quantity -= sell_from_lot
                lot.sold_quantity += sell_from_lot
                lot.capital_gain += lot_capital_gain
                
                # Calculate Indonesian tax liability
                # 0.1% dari proceeds untuk transaksi saham
                lot.tax_liability = lot_proceeds * self.stock_transaction_tax_rate
                
                total_cost_basis += lot_cost_basis
                remaining_sell -= sell_from_lot
                
                lots_used.append({
                    "lot_id": lot.id,
                    "quantity_sold": sell_from_lot,
                    "cost_basis": float(lot_cost_basis),
                    "proceeds": float(lot_proceeds),
                    "capital_gain": float(lot_capital_gain),
                    "tax_liability": float(lot.tax_liability)
                })
            
            if remaining_sell > 0:
                return {"error": f"Insufficient quantity in tax lots. Need {remaining_sell} more shares"}
            
            # Calculate total tax liability
            total_capital_gain = total_proceeds - total_cost_basis
            total_tax_liability = total_proceeds * self.stock_transaction_tax_rate
            
            # Additional capital gains tax if applicable (untuk gains > threshold)
            capital_gains_tax = Decimal('0')
            if total_capital_gain > Decimal('0'):  # Only if there's a gain
                # In Indonesia, capital gains tax might apply based on holding period
                # For simplicity, we'll apply a basic rate
                capital_gains_tax = total_capital_gain * self.capital_gains_tax_rate
            
            self.db.commit()
            
            return {
                "symbol": symbol,
                "method": method,
                "total_quantity": sell_quantity,
                "total_proceeds": float(total_proceeds),
                "total_cost_basis": float(total_cost_basis),
                "total_capital_gain": float(total_capital_gain),
                "transaction_tax": float(total_tax_liability),
                "capital_gains_tax": float(capital_gains_tax),
                "total_tax_liability": float(total_tax_liability + capital_gains_tax),
                "lots_used": lots_used,
                "net_proceeds": float(total_proceeds - total_tax_liability - capital_gains_tax)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sale tax liability: {e}")
            self.db.rollback()
            return {"error": str(e)}
    
    def get_tax_summary(self, symbol: str = None, year: int = None) -> Dict:
        """Get tax summary untuk symbol atau all symbols"""
        try:
            query = self.db.query(TaxLot)
            
            if symbol:
                query = query.filter(TaxLot.symbol == symbol.upper())
            
            if year:
                query = query.filter(
                    TaxLot.purchase_date >= date(year, 1, 1),
                    TaxLot.purchase_date <= date(year, 12, 31)
                )
            
            tax_lots = query.all()
            
            if not tax_lots:
                return {
                    "symbol": symbol or "All",
                    "year": year or "All",
                    "total_lots": 0,
                    "total_quantity": 0,
                    "total_cost_basis": 0,
                    "total_sold_quantity": 0,
                    "total_capital_gain": 0,
                    "total_tax_liability": 0
                }
            
            # Calculate totals
            total_quantity = sum(lot.quantity for lot in tax_lots)
            total_cost_basis = sum(lot.cost_basis * lot.quantity for lot in tax_lots)
            total_sold_quantity = sum(lot.sold_quantity for lot in tax_lots)
            total_capital_gain = sum(lot.capital_gain for lot in tax_lots)
            total_tax_liability = sum(lot.tax_liability for lot in tax_lots)
            
            # Group by symbol if no specific symbol
            symbol_summary = {}
            if not symbol:
                for lot in tax_lots:
                    if lot.symbol not in symbol_summary:
                        symbol_summary[lot.symbol] = {
                            "total_quantity": 0,
                            "total_cost_basis": 0,
                            "total_sold_quantity": 0,
                            "total_capital_gain": 0,
                            "total_tax_liability": 0
                        }
                    
                    symbol_summary[lot.symbol]["total_quantity"] += lot.quantity
                    symbol_summary[lot.symbol]["total_cost_basis"] += float(lot.cost_basis * lot.quantity)
                    symbol_summary[lot.symbol]["total_sold_quantity"] += lot.sold_quantity
                    symbol_summary[lot.symbol]["total_capital_gain"] += float(lot.capital_gain)
                    symbol_summary[lot.symbol]["total_tax_liability"] += float(lot.tax_liability)
            
            return {
                "symbol": symbol or "All",
                "year": year or "All",
                "total_lots": len(tax_lots),
                "total_quantity": total_quantity,
                "total_cost_basis": float(total_cost_basis),
                "total_sold_quantity": total_sold_quantity,
                "total_capital_gain": float(total_capital_gain),
                "total_tax_liability": float(total_tax_liability),
                "symbol_breakdown": symbol_summary if not symbol else None
            }
            
        except Exception as e:
            logger.error(f"Error getting tax summary: {e}")
            return {"error": str(e)}
    
    def get_tax_lots(self, symbol: str = None, position_id: int = None) -> List[Dict]:
        """Get tax lots dengan filters"""
        try:
            query = self.db.query(TaxLot)
            
            if symbol:
                query = query.filter(TaxLot.symbol == symbol.upper())
            
            if position_id:
                query = query.filter(TaxLot.position_id == position_id)
            
            tax_lots = query.order_by(TaxLot.purchase_date.asc()).all()
            
            lot_list = []
            for lot in tax_lots:
                lot_list.append({
                    "id": lot.id,
                    "symbol": lot.symbol,
                    "position_id": lot.position_id,
                    "quantity": lot.quantity,
                    "cost_basis": float(lot.cost_basis),
                    "purchase_date": lot.purchase_date.isoformat(),
                    "remaining_quantity": lot.remaining_quantity,
                    "sold_quantity": lot.sold_quantity,
                    "capital_gain": float(lot.capital_gain),
                    "tax_liability": float(lot.tax_liability),
                    "created_at": lot.created_at.isoformat()
                })
            
            return lot_list
            
        except Exception as e:
            logger.error(f"Error getting tax lots: {e}")
            return []
    
    def calculate_dividend_tax(self, 
                              symbol: str,
                              dividend_amount: float,
                              shares_owned: int) -> Dict:
        """Calculate dividend tax (Indonesia format)"""
        try:
            # Calculate total dividend
            total_dividend = Decimal(str(dividend_amount)) * shares_owned
            
            # Indonesian dividend tax rate (10%)
            dividend_tax = total_dividend * self.dividend_tax_rate
            
            # Net dividend after tax
            net_dividend = total_dividend - dividend_tax
            
            return {
                "symbol": symbol,
                "shares_owned": shares_owned,
                "dividend_per_share": float(dividend_amount),
                "total_dividend": float(total_dividend),
                "dividend_tax_rate": float(self.dividend_tax_rate),
                "dividend_tax": float(dividend_tax),
                "net_dividend": float(net_dividend)
            }
            
        except Exception as e:
            logger.error(f"Error calculating dividend tax: {e}")
            return {"error": str(e)}
    
    def generate_tax_report(self, year: int, symbol: str = None) -> Dict:
        """Generate comprehensive tax report untuk tahun tertentu"""
        try:
            # Get tax summary for the year
            tax_summary = self.get_tax_summary(symbol=symbol, year=year)
            
            if "error" in tax_summary:
                return tax_summary
            
            # Get all trades for the year
            from app.models.trading import Trade
            query = self.db.query(Trade).filter(
                Trade.executed_at >= datetime(year, 1, 1),
                Trade.executed_at <= datetime(year, 12, 31)
            )
            
            if symbol:
                query = query.filter(Trade.symbol == symbol.upper())
            
            trades = query.all()
            
            # Calculate realized P&L
            realized_pnl = sum(trade.realized_pnl or 0 for trade in trades)
            
            # Get tax lots for the year
            tax_lots = self.get_tax_lots(symbol=symbol)
            year_lots = [lot for lot in tax_lots if lot['purchase_date'].startswith(str(year))]
            
            # Calculate tax obligations
            total_transaction_tax = sum(lot['tax_liability'] for lot in year_lots)
            total_capital_gains = sum(lot['capital_gain'] for lot in year_lots)
            
            # Generate report
            report = {
                "year": year,
                "symbol": symbol or "All Symbols",
                "tax_summary": tax_summary,
                "trading_summary": {
                    "total_trades": len(trades),
                    "realized_pnl": realized_pnl,
                    "buy_trades": len([t for t in trades if t.side.value == "buy"]),
                    "sell_trades": len([t for t in trades if t.side.value == "sell"])
                },
                "tax_obligations": {
                    "total_transaction_tax": float(total_transaction_tax),
                    "total_capital_gains": float(total_capital_gains),
                    "dividend_tax": 0.0,  # Would need dividend data
                    "total_tax_liability": float(total_transaction_tax)
                },
                "recommendations": self._generate_tax_recommendations(tax_summary, realized_pnl)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating tax report: {e}")
            return {"error": str(e)}
    
    def _generate_tax_recommendations(self, tax_summary: Dict, realized_pnl: float) -> List[str]:
        """Generate tax recommendations"""
        recommendations = []
        
        if tax_summary["total_capital_gain"] > 0:
            recommendations.append("Consider tax-loss harvesting to offset capital gains")
        
        if tax_summary["total_tax_liability"] > 1000000:  # > 1M IDR
            recommendations.append("High tax liability detected. Consider consulting a tax advisor")
        
        if realized_pnl < 0:
            recommendations.append("Realized losses can be used to offset future capital gains")
        
        if tax_summary["total_sold_quantity"] > 0:
            recommendations.append("Ensure all sales are properly documented for tax purposes")
        
        return recommendations
    
    def update_tax_rates(self, 
                         stock_transaction_rate: float = None,
                         capital_gains_rate: float = None,
                         dividend_rate: float = None) -> Dict:
        """Update tax rates (untuk future changes)"""
        try:
            if stock_transaction_rate is not None:
                self.stock_transaction_tax_rate = Decimal(str(stock_transaction_rate))
            
            if capital_gains_rate is not None:
                self.capital_gains_tax_rate = Decimal(str(capital_gains_rate))
            
            if dividend_rate is not None:
                self.dividend_tax_rate = Decimal(str(dividend_rate))
            
            return {
                "message": "Tax rates updated successfully",
                "current_rates": {
                    "stock_transaction_tax_rate": float(self.stock_transaction_tax_rate),
                    "capital_gains_tax_rate": float(self.capital_gains_tax_rate),
                    "dividend_tax_rate": float(self.dividend_tax_rate)
                }
            }
            
        except Exception as e:
            logger.error(f"Error updating tax rates: {e}")
            return {"error": str(e)}
