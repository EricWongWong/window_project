# member/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender='booking.Order')
@receiver(post_delete, sender='booking.Order')
@receiver(post_save, sender='booking.OrderItem')
@receiver(post_delete, sender='booking.OrderItem')
def send_dashboard_update(sender, instance, **kwargs):
    """Send WebSocket update when order data changes"""
    try:
        channel_layer = get_channel_layer()
        
        async_to_sync(channel_layer.group_send)(
            "staff_dashboard",
            {
                'type': 'dashboard_update',
            }
        )
        action = 'created' if kwargs.get('created') else 'updated' if kwargs.get('update_fields') else 'changed'
        logger.info(f"📤 Dashboard update triggered by {sender.__name__} {action} (ID: {instance.id})")
        print(f"📤 SIGNAL FIRED: {sender.__name__} {action}")  # ⭐ Debug print
    except Exception as e:
        logger.error(f"❌ Failed to send dashboard update: {e}")
        print(f"❌ SIGNAL ERROR: {e}")  # ⭐ Debug print