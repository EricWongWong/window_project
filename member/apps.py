# member/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class MemberConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'member'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import member.signals
            logger.info("✅ Member signals loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load member signals: {e}")
