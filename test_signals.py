# test_signals.py
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'window_project.settings')

import django
django.setup()

from django.apps import apps
app_config = apps.get_app_config('member')
print(f"App config: {app_config}")
print(f"App name: {app_config.name}")
print(f"Ready called: {app_config.ready}")

import member.signals
print("✅ Signals imported successfully")
