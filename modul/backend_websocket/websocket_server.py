"""
WebSocket Server untuk Real-Time Data Streaming
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Set
import socketio
from fastapi import FastAPI
from app.services.data_service import DataService
from app.database import get_db
from sqlalchemy.orm import Session
import redis
from app.config import settings

logger = logging.getLogger(__name__)

# Redis client untuk pub/sub
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# SocketIO server
sio = socketio.AsyncServer(
    cors_allowed_origins="*",
    logger=True,
    engineio_logger=True
)

class WebSocketManager:
    """Manager untuk WebSocket connections dan real-time data"""
    
    def __init__(self):
        self.connected_clients: Set[str] = set()
        self.subscribed_symbols: Dict[str, Set[str]] = {}  # symbol -> set of client_ids
        self.data_service = None
        
    async def initialize(self):
        """Initialize data service"""
        db = next(get_db())
        self.data_service = DataService(db)
    
    async def add_client(self, client_id: str):
        """Add new client connection"""
        self.connected_clients.add(client_id)
        logger.info(f"Client {client_id} connected. Total clients: {len(self.connected_clients)}")
    
    async def remove_client(self, client_id: str):
        """Remove client connection"""
        self.connected_clients.discard(client_id)
        
        # Remove from all symbol subscriptions
        for symbol, clients in self.subscribed_symbols.items():
            clients.discard(client_id)
        
        logger.info(f"Client {client_id} disconnected. Total clients: {len(self.connected_clients)}")
    
    async def subscribe_symbol(self, client_id: str, symbol: str):
        """Subscribe client to symbol updates"""
        if symbol not in self.subscribed_symbols:
            self.subscribed_symbols[symbol] = set()
        
        self.subscribed_symbols[symbol].add(client_id)
        logger.info(f"Client {client_id} subscribed to {symbol}")
        
        # Send current price immediately
        if self.data_service:
            price_data = self.data_service.get_real_time_price(symbol)
            if price_data:
                await sio.emit('price_update', price_data, room=client_id)
    
    async def unsubscribe_symbol(self, client_id: str, symbol: str):
        """Unsubscribe client from symbol updates"""
        if symbol in self.subscribed_symbols:
            self.subscribed_symbols[symbol].discard(client_id)
            logger.info(f"Client {client_id} unsubscribed from {symbol}")
    
    async def broadcast_price_update(self, symbol: str, price_data: Dict):
        """Broadcast price update to all subscribed clients"""
        if symbol in self.subscribed_symbols:
            subscribed_clients = self.subscribed_symbols[symbol]
            if subscribed_clients:
                await sio.emit('price_update', price_data, room=list(subscribed_clients))
                logger.debug(f"Broadcasted price update for {symbol} to {len(subscribed_clients)} clients")
    
    async def broadcast_market_update(self, market_data: Dict):
        """Broadcast market-wide updates"""
        await sio.emit('market_update', market_data)
        logger.debug(f"Broadcasted market update to {len(self.connected_clients)} clients")

# Global WebSocket manager
ws_manager = WebSocketManager()

# SocketIO event handlers
@sio.event
async def connect(sid, environ):
    """Handle client connection"""
    await ws_manager.add_client(sid)
    await sio.emit('connected', {'message': 'Connected to Trading Platform Modern'}, room=sid)

@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    await ws_manager.remove_client(sid)

@sio.event
async def subscribe_symbol(sid, data):
    """Handle symbol subscription"""
    try:
        symbol = data.get('symbol', '').upper()
        if symbol:
            await ws_manager.subscribe_symbol(sid, symbol)
            await sio.emit('subscription_confirmed', {'symbol': symbol}, room=sid)
    except Exception as e:
        logger.error(f"Error subscribing to symbol: {e}")
        await sio.emit('error', {'message': 'Failed to subscribe to symbol'}, room=sid)

@sio.event
async def unsubscribe_symbol(sid, data):
    """Handle symbol unsubscription"""
    try:
        symbol = data.get('symbol', '').upper()
        if symbol:
            await ws_manager.unsubscribe_symbol(sid, symbol)
            await sio.emit('unsubscription_confirmed', {'symbol': symbol}, room=sid)
    except Exception as e:
        logger.error(f"Error unsubscribing from symbol: {e}")
        await sio.emit('error', {'message': 'Failed to unsubscribe from symbol'}, room=sid)

@sio.event
async def get_historical_data(sid, data):
    """Handle historical data request"""
    try:
        symbol = data.get('symbol', '').upper()
        timeframe = data.get('timeframe', '1D')
        limit = data.get('limit', 100)
        
        if symbol and ws_manager.data_service:
            historical_data = ws_manager.data_service.get_market_data(symbol, timeframe, limit)
            await sio.emit('historical_data', {
                'symbol': symbol,
                'timeframe': timeframe,
                'data': historical_data
            }, room=sid)
    except Exception as e:
        logger.error(f"Error getting historical data: {e}")
        await sio.emit('error', {'message': 'Failed to get historical data'}, room=sid)

@sio.event
async def get_real_time_price(sid, data):
    """Handle real-time price request"""
    try:
        symbol = data.get('symbol', '').upper()
        
        if symbol and ws_manager.data_service:
            price_data = ws_manager.data_service.get_real_time_price(symbol)
            if price_data:
                await sio.emit('price_update', price_data, room=sid)
    except Exception as e:
        logger.error(f"Error getting real-time price: {e}")
        await sio.emit('error', {'message': 'Failed to get real-time price'}, room=sid)

class RealTimeDataUpdater:
    """Background task untuk update real-time data"""
    
    def __init__(self):
        self.running = False
        self.update_interval = 5  # seconds
    
    async def start(self):
        """Start real-time data updater"""
        self.running = True
        await ws_manager.initialize()
        
        while self.running:
            try:
                await self._update_all_subscribed_symbols()
                await asyncio.sleep(self.update_interval)
            except Exception as e:
                logger.error(f"Error in real-time data updater: {e}")
                await asyncio.sleep(self.update_interval)
    
    async def stop(self):
        """Stop real-time data updater"""
        self.running = False
    
    async def _update_all_subscribed_symbols(self):
        """Update all subscribed symbols"""
        if not ws_manager.data_service:
            return
        
        for symbol in ws_manager.subscribed_symbols.keys():
            try:
                price_data = ws_manager.data_service.get_real_time_price(symbol)
                if price_data:
                    await ws_manager.broadcast_price_update(symbol, price_data)
            except Exception as e:
                logger.error(f"Error updating {symbol}: {e}")

# Global real-time updater
realtime_updater = RealTimeDataUpdater()

async def start_websocket_server(app: FastAPI):
    """Start WebSocket server"""
    # Initialize WebSocket manager
    await ws_manager.initialize()
    
    # Start real-time data updater
    asyncio.create_task(realtime_updater.start())
    
    logger.info("WebSocket server started")

async def stop_websocket_server():
    """Stop WebSocket server"""
    await realtime_updater.stop()
    logger.info("WebSocket server stopped")

# Redis pub/sub untuk external data updates
async def redis_subscriber():
    """Redis subscriber untuk external data updates"""
    pubsub = redis_client.pubsub()
    await pubsub.subscribe('market_data_updates')
    
    async for message in pubsub.listen():
        if message['type'] == 'message':
            try:
                data = json.loads(message['data'])
                symbol = data.get('symbol')
                if symbol:
                    await ws_manager.broadcast_price_update(symbol, data)
            except Exception as e:
                logger.error(f"Error processing Redis message: {e}")

# Export untuk use di main app
__all__ = ['sio', 'ws_manager', 'start_websocket_server', 'stop_websocket_server', 'redis_subscriber']
