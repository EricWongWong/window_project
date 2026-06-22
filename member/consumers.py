# member/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import datetime, timedelta
import logging

# ⭐ CHANGE 1: Import the utility function
from .utils import get_dashboard_data

logger = logging.getLogger(__name__)

class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time dashboard updates - Staff only"""
    
    async def connect(self):
        # Only allow staff to connect
        if self.scope['user'].is_authenticated and self.scope['user'].is_staff:
            await self.accept()
            self.room_group_name = "staff_dashboard"
            
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            logger.info(f"✅ WebSocket connected for staff: {self.scope['user'].username}")
            await self.send_dashboard_data()
        else:
            logger.warning(f"WebSocket connection rejected: user not staff")
            await self.close()
    
    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        logger.info(f"🔌WebSocket disconnected with code: {close_code}")
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            if text_data_json.get('action') == 'refresh':
                await self.send_dashboard_data()
        except json.JSONDecodeError:
            pass
    
    async def send_dashboard_data(self):
        # ⭐ CHANGE 2: Use the utility function (no more get_dashboard_data method)
        data = await database_sync_to_async(get_dashboard_data)()
        
        # ⭐ CHANGE 3: Send data directly (no need to wrap in 'data' key)
        # Your frontend expects the data directly, not wrapped
        await self.send(text_data=json.dumps(data))
        logger.info("📊 Dashboard data sent via WebSocket")
    
    # ⭐ REMOVE the get_dashboard_data method - it's now in utils.py
    
    
    async def dashboard_update(self, event):
        """Called when signals trigger an update"""
        logger.info("📤 Dashboard update triggered by signal")
        await self.send_dashboard_data()