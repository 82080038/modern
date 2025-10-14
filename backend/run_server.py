"""
Run Trading Platform Modern Server
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Trading Platform Modern...")
    print("📊 Features: Fundamental + Sentiment Analysis")
    print("🤖 AI-Powered 3-Pillar Analysis Platform")
    print("🌐 Access: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
