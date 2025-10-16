"""
Portfolio Heat Map API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.services.portfolio_heatmap_service import PortfolioHeatMapService
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/portfolio-heatmap", tags=["Portfolio Heat Map"])

# Pydantic schemas
class SectorExposureResponse(BaseModel):
    portfolio_id: int
    total_value: float
    sector_exposure: dict
    diversification_score: float

class RiskHeatmapResponse(BaseModel):
    portfolio_id: int
    risk_data: list
    total_risk: float
    max_risk_position: dict
    risk_distribution: dict

class PerformanceHeatmapResponse(BaseModel):
    portfolio_id: int
    period_days: int
    performance_data: list
    total_contribution: float
    best_performer: dict
    worst_performer: dict
    performance_distribution: dict

class CorrelationHeatmapResponse(BaseModel):
    portfolio_id: int
    period_days: int
    correlation_matrix: dict
    high_correlation_pairs: list
    diversification_analysis: dict

class ComprehensiveHeatmapResponse(BaseModel):
    portfolio_id: int
    sector_exposure: dict
    risk_heatmap: dict
    performance_heatmap: dict
    correlation_heatmap: dict
    generated_at: str

@router.get("/sector-exposure/{portfolio_id}", response_model=SectorExposureResponse)
async def get_sector_exposure(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """Get sector exposure heatmap untuk portfolio"""
    try:
        service = PortfolioHeatMapService(db)
        result = service.calculate_sector_exposure(portfolio_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return SectorExposureResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting sector exposure: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-heatmap/{portfolio_id}", response_model=RiskHeatmapResponse)
async def get_risk_heatmap(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """Get risk heatmap untuk portfolio"""
    try:
        service = PortfolioHeatMapService(db)
        result = service.calculate_risk_heatmap(portfolio_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return RiskHeatmapResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting risk heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/performance-heatmap/{portfolio_id}", response_model=PerformanceHeatmapResponse)
async def get_performance_heatmap(
    portfolio_id: int,
    days: int = Query(30, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get performance heatmap untuk portfolio"""
    try:
        service = PortfolioHeatMapService(db)
        result = service.calculate_performance_heatmap(portfolio_id, days)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return PerformanceHeatmapResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting performance heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/correlation-heatmap/{portfolio_id}", response_model=CorrelationHeatmapResponse)
async def get_correlation_heatmap(
    portfolio_id: int,
    days: int = Query(90, description="Number of days to look back"),
    db: Session = Depends(get_db)
):
    """Get correlation heatmap untuk portfolio"""
    try:
        service = PortfolioHeatMapService(db)
        result = service.calculate_correlation_heatmap(portfolio_id, days)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return CorrelationHeatmapResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting correlation heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/comprehensive/{portfolio_id}", response_model=ComprehensiveHeatmapResponse)
async def get_comprehensive_heatmap(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """Get comprehensive heatmap data untuk portfolio"""
    try:
        service = PortfolioHeatMapService(db)
        result = service.get_comprehensive_heatmap(portfolio_id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return ComprehensiveHeatmapResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting comprehensive heatmap: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diversification-analysis/{portfolio_id}")
async def get_diversification_analysis(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """Get diversification analysis untuk portfolio"""
    try:
        service = PortfolioHeatMapService(db)
        
        # Get sector exposure
        sector_result = service.calculate_sector_exposure(portfolio_id)
        if "error" in sector_result:
            raise HTTPException(status_code=400, detail=sector_result["error"])
        
        # Get correlation analysis
        correlation_result = service.calculate_correlation_heatmap(portfolio_id)
        if "error" in correlation_result:
            raise HTTPException(status_code=400, detail=correlation_result["error"])
        
        # Combine analysis
        analysis = {
            "portfolio_id": portfolio_id,
            "sector_diversification": {
                "score": sector_result["diversification_score"],
                "sector_count": len(sector_result["sector_exposure"]),
                "largest_sector": max(sector_result["sector_exposure"].items(), 
                                    key=lambda x: x[1]["percentage"]) if sector_result["sector_exposure"] else None
            },
            "correlation_diversification": correlation_result["diversification_analysis"],
            "recommendations": service._get_diversification_recommendations(
                sector_result["diversification_score"],
                correlation_result["diversification_analysis"].get("average_correlation", 0)
            )
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error getting diversification analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/risk-concentration/{portfolio_id}")
async def get_risk_concentration(
    portfolio_id: int,
    db: Session = Depends(get_db)
):
    """Get risk concentration analysis untuk portfolio"""
    try:
        service = PortfolioHeatMapService(db)
        
        # Get risk heatmap
        risk_result = service.calculate_risk_heatmap(portfolio_id)
        if "error" in risk_result:
            raise HTTPException(status_code=400, detail=risk_result["error"])
        
        # Analyze risk concentration
        risk_data = risk_result["risk_data"]
        if not risk_data:
            return {"error": "No risk data available"}
        
        # Calculate concentration metrics
        total_risk = sum([item["risk_score"] for item in risk_data])
        max_risk = max([item["risk_score"] for item in risk_data])
        
        # Top 5 risk contributors
        top_risk_contributors = sorted(risk_data, key=lambda x: x["risk_score"], reverse=True)[:5]
        
        # Risk concentration ratio
        concentration_ratio = max_risk / total_risk if total_risk > 0 else 0
        
        # Risk distribution
        risk_distribution = service._calculate_risk_distribution(risk_data)
        
        return {
            "portfolio_id": portfolio_id,
            "total_risk": total_risk,
            "max_risk": max_risk,
            "concentration_ratio": round(concentration_ratio, 4),
            "top_risk_contributors": top_risk_contributors,
            "risk_distribution": risk_distribution,
            "concentration_level": service._get_concentration_level(concentration_ratio)
        }
        
    except Exception as e:
        logger.error(f"Error getting risk concentration: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add helper methods to service
def _get_diversification_recommendations(self, sector_score: float, correlation: float) -> list:
    """Get diversification recommendations"""
    recommendations = []
    
    if sector_score < 0.3:
        recommendations.append("Portfolio has good sector diversification")
    else:
        recommendations.append("Consider diversifying across more sectors")
    
    if correlation < 0.3:
        recommendations.append("Portfolio has low correlation between positions")
    else:
        recommendations.append("Consider adding uncorrelated assets")
    
    return recommendations

def _get_concentration_level(self, concentration_ratio: float) -> str:
    """Get concentration level assessment"""
    if concentration_ratio < 0.2:
        return "Well Diversified"
    elif concentration_ratio < 0.4:
        return "Moderately Concentrated"
    elif concentration_ratio < 0.6:
        return "Concentrated"
    else:
        return "Highly Concentrated"
