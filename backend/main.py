"""
FastAPI Main Application - Trading Platform Modern
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
from app.api import fundamental, sentiment, market_data, trading, notifications, security, tax, backup, cache, backtesting, watchlist, pattern, dashboard, earnings, sentiment_scraping, economic_calendar, web_scraping
from app.database import engine, Base
from app.config import settings
from app.websocket.websocket_server import sio, start_websocket_server, stop_websocket_server
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Trading Platform Modern",
    description="AI-Powered Trading Platform with 3-Pillar Analysis: Technical + Fundamental + Sentiment",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
@app.on_event("startup")
async def startup_event():
    """Initialize database tables"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Start WebSocket server
        await start_websocket_server(app)
        logger.info("WebSocket server started")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event"""
    try:
        await stop_websocket_server()
        logger.info("WebSocket server stopped")
    except Exception as e:
        logger.error(f"Error stopping WebSocket server: {e}")

# Include API routers
app.include_router(fundamental.router, prefix="/api/v1")
app.include_router(sentiment.router, prefix="/api/v1")
app.include_router(market_data.router, prefix="/api/v1")
app.include_router(trading.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(security.router, prefix="/api/v1")
app.include_router(tax.router, prefix="/api/v1")
app.include_router(backup.router, prefix="/api/v1")
app.include_router(cache.router, prefix="/api/v1")
app.include_router(backtesting.router, prefix="/api/v1")
app.include_router(watchlist.router, prefix="/api/v1")
app.include_router(pattern.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(earnings.router, prefix="/api/v1")
app.include_router(sentiment_scraping.router, prefix="/api/v1")
app.include_router(economic_calendar.router, prefix="/api/v1")
app.include_router(web_scraping.router, prefix="/api/v1")

# Mount SocketIO app
app.mount("/socket.io", sio)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Trading Platform Modern",
        "version": "1.0.0",
        "features": [
            "Fundamental Analysis",
            "Sentiment Analysis",
            "Real-Time Market Data",
            "WebSocket Streaming",
            "Order Management System",
            "Training & Real-Time Trading Modes",
            "Technical Analysis (coming soon)",
            "AI/ML Models (coming soon)",
            "Backtesting (coming soon)"
        ]
    }

# Root endpoint
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with platform overview"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Trading Platform Modern</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            .feature-card { border-left: 4px solid #007bff; }
            .sentiment-card { border-left: 4px solid #28a745; }
            .fundamental-card { border-left: 4px solid #ffc107; }
        </style>
    </head>
    <body>
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
            <div class="container">
                <a class="navbar-brand" href="#">
                    🚀 Trading Platform Modern
                </a>
                <div class="navbar-nav ms-auto">
                    <span class="navbar-text">
                        AI-Powered 3-Pillar Analysis Platform
                    </span>
                </div>
            </div>
        </nav>

        <div class="container mt-4">
            <!-- Platform Overview -->
            <div class="row mb-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h3 class="mb-0">📊 Trading Platform Modern</h3>
                        </div>
                        <div class="card-body">
                            <h5>AI-Powered Trading Platform dengan Analisis 3-Pilar</h5>
                            <p class="text-muted">Platform trading profesional yang menggabungkan Technical + Fundamental + Sentiment Analysis</p>
                            
                            <div class="row mt-4">
                                <div class="col-md-4">
                                    <h6>🎯 Core Features:</h6>
                                    <ul>
                                        <li>Fundamental Analysis (30+ ratios)</li>
                                        <li>Sentiment Analysis (News + Social)</li>
                                        <li>DCF Valuation Models</li>
                                        <li>Peer Comparison</li>
                                        <li>Earnings Quality Analysis</li>
                                        <li>Market Sentiment Indicators</li>
                                    </ul>
                                </div>
                                <div class="col-md-4">
                                    <h6>🔗 API Endpoints:</h6>
                                    <ul>
                                        <li><a href="/docs" target="_blank">API Documentation</a></li>
                                        <li><a href="/health">Health Check</a></li>
                                        <li><a href="/api/v1/fundamental/ratios/BBCA">Fundamental Analysis</a></li>
                                        <li><a href="/api/v1/sentiment/composite/BBCA">Sentiment Analysis</a></li>
                                    </ul>
                                </div>
                                <div class="col-md-4">
                                    <h6>📈 Coming Soon:</h6>
                                    <ul>
                                        <li>Technical Analysis (50+ indicators)</li>
                                        <li>AI/ML Models (LSTM, FinBERT)</li>
                                        <li>Backtesting Framework</li>
                                        <li>Real-time Trading</li>
                                        <li>Risk Management</li>
                                        <li>Portfolio Optimization</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Feature Cards -->
            <div class="row">
                <div class="col-md-6">
                    <div class="card fundamental-card">
                        <div class="card-header">
                            <h5 class="mb-0">💼 Fundamental Analysis</h5>
                        </div>
                        <div class="card-body">
                            <h6>Financial Ratios & Valuation:</h6>
                            <ul>
                                <li><strong>Profitability:</strong> ROE, ROA, Profit Margin</li>
                                <li><strong>Liquidity:</strong> Current Ratio, Cash Ratio</li>
                                <li><strong>Leverage:</strong> Debt/Equity, Interest Coverage</li>
                                <li><strong>Valuation:</strong> DCF, Graham Number, PE/PB</li>
                                <li><strong>Growth:</strong> EPS Growth, Revenue Growth</li>
                            </ul>
                            <div class="mt-3">
                                <a href="/api/v1/fundamental/ratios/BBCA" class="btn btn-warning btn-sm">Test Fundamental API</a>
                                <a href="/api/v1/fundamental/screener" class="btn btn-outline-warning btn-sm">Stock Screener</a>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="card sentiment-card">
                        <div class="card-header">
                            <h5 class="mb-0">📰 Sentiment Analysis</h5>
                        </div>
                        <div class="card-body">
                            <h6>Multi-Source Sentiment:</h6>
                            <ul>
                                <li><strong>News Sentiment:</strong> FinBERT, Polarity Analysis</li>
                                <li><strong>Social Media:</strong> Twitter, Reddit, Facebook</li>
                                <li><strong>Market Indicators:</strong> Fear & Greed Index, VIX</li>
                                <li><strong>Insider Activity:</strong> Buy/Sell Patterns</li>
                                <li><strong>Composite Score:</strong> Weighted Sentiment</li>
                            </ul>
                            <div class="mt-3">
                                <a href="/api/v1/sentiment/composite/BBCA" class="btn btn-success btn-sm">Test Sentiment API</a>
                                <a href="/api/v1/sentiment/dashboard" class="btn btn-outline-success btn-sm">Sentiment Dashboard</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- API Examples -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">🔧 API Examples</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Fundamental Analysis:</h6>
                                    <pre><code># Get financial ratios
GET /api/v1/fundamental/ratios/BBCA

# DCF valuation
GET /api/v1/fundamental/dcf/BBCA?current_price=8500

# Fundamental screener
GET /api/v1/fundamental/screener?min_roe=15&max_pe=20</code></pre>
                                </div>
                                <div class="col-md-6">
                                    <h6>Sentiment Analysis:</h6>
                                    <pre><code># Composite sentiment
GET /api/v1/sentiment/composite/BBCA

# News sentiment
GET /api/v1/sentiment/news/BBCA?days=7

# Market sentiment
GET /api/v1/sentiment/market</code></pre>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Quick Start -->
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card">
                        <div class="card-header">
                            <h5 class="mb-0">🚀 Quick Start</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-3">
                                    <h6>1. Fundamental Analysis</h6>
                                    <p>Analyze financial health, ratios, and valuation</p>
                                </div>
                                <div class="col-md-3">
                                    <h6>2. Sentiment Analysis</h6>
                                    <p>Monitor news, social media, and market sentiment</p>
                                </div>
                                <div class="col-md-3">
                                    <h6>3. Stock Screening</h6>
                                    <p>Filter stocks by fundamental and sentiment criteria</p>
                                </div>
                                <div class="col-md-3">
                                    <h6>4. API Integration</h6>
                                    <p>Integrate with your trading applications</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <footer class="bg-light mt-5 py-4">
            <div class="container text-center">
                <p class="text-muted mb-0">
                    Trading Platform Modern - AI-Powered 3-Pillar Analysis Platform
                </p>
            </div>
        </footer>
    </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
