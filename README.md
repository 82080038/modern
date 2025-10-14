# 🚀 Trading Platform Modern - AI-Powered 3-Pillar Analysis Platform

Platform trading profesional yang menggabungkan **Technical + Fundamental + Sentiment Analysis** untuk pasar saham Indonesia.

## ✨ Features

### 📊 **Fundamental Analysis**
- **30+ Financial Ratios**: ROE, ROA, Profit Margin, Current Ratio, Debt/Equity
- **Valuation Models**: DCF, Graham Number, PE/PB Analysis
- **Earnings Quality**: Consistency, Growth Analysis
- **Peer Comparison**: Sector-based benchmarking
- **Stock Screener**: Multi-criteria filtering

### 📰 **Sentiment Analysis**
- **News Sentiment**: FinBERT, Polarity Analysis, Impact Scoring
- **Social Media**: Twitter, Reddit, Facebook sentiment
- **Market Indicators**: Fear & Greed Index, VIX, Put/Call Ratio
- **Insider Activity**: Buy/Sell pattern analysis
- **Composite Score**: Weighted sentiment from all sources

### 🤖 **AI/ML Models** (Coming Soon)
- **LSTM**: Price prediction models
- **FinBERT**: Financial sentiment analysis
- **Ensemble Methods**: Model stacking and blending
- **Feature Engineering**: 50+ technical indicators

### 📈 **Technical Analysis** (Coming Soon)
- **50+ Indicators**: MA, RSI, MACD, Bollinger Bands
- **Pattern Recognition**: Candlestick, Chart patterns
- **Multi-timeframe**: 1m, 5m, 15m, 1h, 1d analysis

### 🛡️ **Risk Management** (Coming Soon)
- **Position Sizing**: Kelly Criterion, Fixed Fractional
- **VaR & CVaR**: Portfolio risk calculation
- **Drawdown Control**: Circuit breakers
- **Portfolio Optimization**: Risk-adjusted returns

## 🏗️ Architecture

```
[Data Sources] → [ETL Pipeline] → [Analysis Engines] → [API Layer] → [Frontend]
     ↓              ↓                ↓                ↓            ↓
[IDX Data]    [Data Quality]   [Fundamental]     [FastAPI]    [Dashboard]
[News API]    [Feature Eng]    [Sentiment]       [REST API]   [Charts]
[Social Media] [Sentiment]      [Technical]       [WebSocket]  [Analytics]
```

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Async REST API
- **SQLAlchemy** - ORM
- **MySQL** - Database (existing `scalper` database)
- **Redis** - Caching & session
- **Celery** - Background tasks

### AI/ML
- **PyTorch** - Deep learning
- **Transformers** - FinBERT sentiment
- **scikit-learn** - Classical ML
- **TA-Lib** - Technical indicators
- **Optuna** - Hyperparameter tuning

### Frontend
- **HTML5 + Bootstrap 5** - Responsive UI
- **jQuery** - DOM manipulation
- **Lightweight Charts** - Interactive charts
- **DataTables** - Advanced tables

## 🚀 Quick Start

### 1. **Setup Environment**
```bash
cd trading-platform-modern/backend
pip install -r requirements.txt
```

### 2. **Database Setup**
- Ensure MySQL server running
- Database `scalper` already exists
- Tables will be created automatically

### 3. **Run Server**
```bash
python run_server.py
```

### 4. **Access Application**
- **Main App**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📊 API Endpoints

### Fundamental Analysis
- `GET /api/v1/fundamental/ratios/{symbol}` - Financial ratios
- `GET /api/v1/fundamental/dcf/{symbol}` - DCF valuation
- `GET /api/v1/fundamental/graham/{symbol}` - Graham Number
- `GET /api/v1/fundamental/earnings-quality/{symbol}` - Earnings analysis
- `GET /api/v1/fundamental/score/{symbol}` - Fundamental score
- `GET /api/v1/fundamental/peer-comparison/{symbol}` - Peer analysis
- `GET /api/v1/fundamental/screener` - Stock screener

### Sentiment Analysis
- `GET /api/v1/sentiment/news/{symbol}` - News sentiment
- `GET /api/v1/sentiment/social/{symbol}` - Social media sentiment
- `GET /api/v1/sentiment/market` - Market sentiment indicators
- `GET /api/v1/sentiment/insider/{symbol}` - Insider activity
- `GET /api/v1/sentiment/composite/{symbol}` - Composite sentiment
- `GET /api/v1/sentiment/alerts/{symbol}` - Sentiment alerts
- `GET /api/v1/sentiment/dashboard` - Multi-symbol dashboard
- `GET /api/v1/sentiment/screener` - Sentiment screener

## 💡 Usage Examples

### Fundamental Analysis
```bash
# Get financial ratios for BBCA
curl "http://localhost:8000/api/v1/fundamental/ratios/BBCA"

# DCF valuation
curl "http://localhost:8000/api/v1/fundamental/dcf/BBCA?current_price=8500"

# Stock screener
curl "http://localhost:8000/api/v1/fundamental/screener?min_roe=15&max_pe=20"
```

### Sentiment Analysis
```bash
# Composite sentiment
curl "http://localhost:8000/api/v1/sentiment/composite/BBCA"

# News sentiment
curl "http://localhost:8000/api/v1/sentiment/news/BBCA?days=7"

# Market sentiment
curl "http://localhost:8000/api/v1/sentiment/market"
```

## 📁 Project Structure

```
trading-platform-modern/
├── backend/
│   ├── app/
│   │   ├── api/              # FastAPI endpoints
│   │   │   ├── fundamental.py # Fundamental analysis API
│   │   │   └── sentiment.py  # Sentiment analysis API
│   │   ├── core/             # Business logic
│   │   │   ├── fundamental.py # Fundamental analysis engine
│   │   │   └── sentiment.py  # Sentiment analysis engine
│   │   ├── models/           # Database models
│   │   │   ├── fundamental.py # Fundamental data models
│   │   │   └── sentiment.py  # Sentiment data models
│   │   ├── config.py        # Configuration
│   │   └── database.py      # DB connections
│   ├── main.py              # FastAPI app
│   ├── run_server.py        # Server runner
│   └── requirements.txt     # Dependencies
├── frontend/                # Coming soon
├── data/                    # Data storage
├── docker/                  # Docker configuration
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
└── README.md
```

## 🎯 Development Roadmap

### Phase 1: Foundation ✅
- [x] Database schema design
- [x] FastAPI project structure
- [x] Fundamental analysis engine
- [x] Sentiment analysis engine
- [x] API endpoints

### Phase 2: Data Integration (Next)
- [ ] Real-time market data
- [ ] News scraping pipeline
- [ ] Social media integration
- [ ] Data quality control

### Phase 3: Technical Analysis
- [ ] 50+ technical indicators
- [ ] Pattern recognition
- [ ] Multi-timeframe analysis
- [ ] Technical signals

### Phase 4: AI/ML Models
- [ ] LSTM price prediction
- [ ] FinBERT sentiment
- [ ] Ensemble methods
- [ ] Model training pipeline

### Phase 5: Advanced Features
- [ ] Backtesting framework
- [ ] Risk management
- [ ] Portfolio optimization
- [ ] Real-time trading

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=mysql+pymysql://root:@localhost:3306/scalper
REDIS_URL=redis://localhost:6379/0

# API Keys (optional)
ALPHA_VANTAGE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
TWITTER_API_KEY=your_key_here

# Trading Configuration
PAPER_TRADING_MODE=true
VIRTUAL_BALANCE=10000000.0
COMMISSION_RATE=0.0015
SLIPPAGE_RATE=0.0005
```

## 📊 Supported Analysis

### Fundamental Analysis
- **Profitability**: ROE, ROA, Profit Margin, Operating Margin
- **Liquidity**: Current Ratio, Quick Ratio, Cash Ratio
- **Leverage**: Debt/Equity, Debt/Assets, Interest Coverage
- **Efficiency**: Asset Turnover, Inventory Turnover
- **Valuation**: PE, PB, PS, PEG, EV/EBITDA
- **Growth**: EPS Growth, Revenue Growth, Book Value Growth

### Sentiment Analysis
- **News Sentiment**: Polarity, Subjectivity, Confidence
- **Social Sentiment**: Engagement-weighted scoring
- **Market Sentiment**: Fear & Greed Index, VIX, Breadth
- **Insider Activity**: Buy/Sell patterns, Net activity
- **Composite Score**: Weighted average from all sources

## 🛡️ Risk Management

### Position Sizing
- Fixed fractional: 1-2% risk per trade
- Kelly Criterion: Optimal position sizing
- Volatility-adjusted sizing

### Portfolio Limits
- Max position size: 10% of portfolio
- Daily loss limit: 2%
- Max drawdown: 15%

## 📈 Performance Metrics

- **Fundamental Score**: 0-100 rating system
- **Sentiment Score**: -1 to +1 scale
- **Composite Score**: Weighted combination
- **Confidence Level**: 0 to 1 scale
- **Trend Analysis**: Improving/Declining/Stable

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

For issues and questions:
- Create GitHub issue
- Check API documentation at `/docs`
- Review logs in console output

---

**🚀 Ready to start your AI-powered trading analysis journey!**

### Quick Test Commands

```bash
# Test fundamental analysis
curl "http://localhost:8000/api/v1/fundamental/ratios/BBCA"

# Test sentiment analysis  
curl "http://localhost:8000/api/v1/sentiment/composite/BBCA"

# Test health check
curl "http://localhost:8000/health"
```
