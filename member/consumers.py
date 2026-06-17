# member/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from datetime import datetime, timedelta
import logging

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
            
            logger.info(f"WebSocket connected for staff: {self.scope['user'].username}")
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
        logger.info(f"WebSocket disconnected with code: {close_code}")
    
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            if text_data_json.get('action') == 'refresh':
                await self.send_dashboard_data()
        except json.JSONDecodeError:
            pass
    
    async def send_dashboard_data(self):
        data = await self.get_dashboard_data()
        
        await self.send(text_data=json.dumps({
            'type': 'dashboard_update',
            'data': data
        }))
    
    @database_sync_to_async
    def get_dashboard_data(self):
        """Fetch dashboard statistics from database"""
        # ⭐ Import Django models INSIDE the function
        from django.contrib.auth.models import User
        from booking.models import Order
        
        try:
            today = timezone.now().date()
            
            total_members = User.objects.count()
            total_orders = Order.objects.count()
            
            # Today's orders
            today_start = datetime.combine(today, datetime.min.time())
            today_start = timezone.make_aware(today_start) if not timezone.is_aware(today_start) else today_start
            today_end = datetime.combine(today, datetime.max.time())
            today_end = timezone.make_aware(today_end) if not timezone.is_aware(today_end) else today_end
            
            today_orders = Order.objects.filter(
                created_at__gte=today_start,
                created_at__lte=today_end
            ).count()
            
            # This week orders
            week_ago = today - timedelta(days=7)
            week_start = datetime.combine(week_ago, datetime.min.time())
            week_start = timezone.make_aware(week_start) if not timezone.is_aware(week_start) else week_start
            this_week_orders = Order.objects.filter(
                created_at__gte=week_start
            ).count()
            
            # This month orders
            month_start = datetime(today.year, today.month, 1)
            month_start = timezone.make_aware(month_start) if not timezone.is_aware(month_start) else month_start
            this_month_orders = Order.objects.filter(
                created_at__gte=month_start
            ).count()
            
            # Daily orders (last 7 days)
            daily_orders = []
            for i in range(6, -1, -1):
                date = today - timedelta(days=i)
                date_start = datetime.combine(date, datetime.min.time())
                date_start = timezone.make_aware(date_start) if not timezone.is_aware(date_start) else date_start
                date_end = datetime.combine(date, datetime.max.time())
                date_end = timezone.make_aware(date_end) if not timezone.is_aware(date_end) else date_end
                
                count = Order.objects.filter(
                    created_at__gte=date_start,
                    created_at__lte=date_end
                ).count()
                
                daily_orders.append({
                    'date': date.strftime('%m/%d'),
                    'count': count,
                    'day': date.strftime('%A')[:3]
                })
            
            # Weekly orders (last 4 weeks)
            weekly_orders = []
            for i in range(3, -1, -1):
                week_start_date = today - timedelta(days=today.weekday() + (7 * i))
                week_end_date = week_start_date + timedelta(days=6)
                
                week_start_datetime = datetime.combine(week_start_date, datetime.min.time())
                week_start_datetime = timezone.make_aware(week_start_datetime) if not timezone.is_aware(week_start_datetime) else week_start_datetime
                week_end_datetime = datetime.combine(week_end_date, datetime.max.time())
                week_end_datetime = timezone.make_aware(week_end_datetime) if not timezone.is_aware(week_end_datetime) else week_end_datetime
                
                count = Order.objects.filter(
                    created_at__gte=week_start_datetime,
                    created_at__lte=week_end_datetime
                ).count()
                
                week_number = (today - week_start_date).days // 7 + 1
                if week_number == 1:
                    week_label = "本週"
                elif week_number == 2:
                    week_label = "上週"
                else:
                    week_label = f"{week_number}週前"
                
                weekly_orders.append({
                    'week': week_label,
                    'date_range': f"{week_start_date.strftime('%m/%d')} - {week_end_date.strftime('%m/%d')}",
                    'count': count
                })
            
            # Monthly orders (last 6 months)
            monthly_orders = []
            for i in range(5, -1, -1):
                month = today.month - i
                year = today.year
                
                if month <= 0:
                    month += 12
                    year -= 1
                
                month_start = datetime(year, month, 1)
                month_start = timezone.make_aware(month_start) if not timezone.is_aware(month_start) else month_start
                
                if month == 12:
                    month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
                else:
                    month_end = datetime(year, month + 1, 1) - timedelta(days=1)
                month_end = timezone.make_aware(month_end) if not timezone.is_aware(month_end) else month_end
                
                count = Order.objects.filter(
                    created_at__gte=month_start,
                    created_at__lte=month_end
                ).count()
                
                monthly_orders.append({
                    'month': month_start.strftime('%Y-%m'),
                    'month_name': month_start.strftime('%b %Y'),
                    'count': count
                })
            
            # Status distribution
            status_counts = {
                'pending': Order.objects.filter(status='pending').count(),
                'confirmed': Order.objects.filter(status='confirmed').count(),
                'in_progress': Order.objects.filter(status='in_progress').count(),
                'completed': Order.objects.filter(status='completed').count(),
                'cancelled': Order.objects.filter(status='cancelled').count(),
            }
            
            # Recent orders
            recent_orders = []
            recent_orders_query = Order.objects.order_by('-created_at')[:10]
            
            for order in recent_orders_query:
                recent_orders.append({
                    'id': order.id,
                    'customer': order.name if order.name else 'N/A',
                    'phone': order.phone if order.phone else 'N/A',
                    'service_type': order.service_type if order.service_type else 'N/A',
                    'booking_date': order.booking_date.strftime('%Y-%m-%d') if order.booking_date else '',
                    'status': order.status if order.status else 'pending',
                    'created_at': order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '',
                })
            
            return {
                'stats': {
                    'total_members': total_members,
                    'total_orders': total_orders,
                    'today_orders': today_orders,
                    'this_week_orders': this_week_orders,
                    'this_month_orders': this_month_orders,
                },
                'daily_orders': daily_orders,
                'weekly_orders': weekly_orders,
                'monthly_orders': monthly_orders,
                'status_counts': status_counts,
                'recent_orders': recent_orders,
                'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Dashboard data error: {str(e)}", exc_info=True)
            return {
                'stats': {
                    'total_members': 0,
                    'total_orders': 0,
                    'today_orders': 0,
                    'this_week_orders': 0,
                    'this_month_orders': 0,
                },
                'daily_orders': [],
                'weekly_orders': [],
                'monthly_orders': [],
                'status_counts': {},
                'recent_orders': [],
                'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    async def dashboard_update(self, event):
        await self.send_dashboard_data()