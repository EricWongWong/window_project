#!/usr/bin/env python3
"""
Simple test script to debug staging table issue
"""

import os
import sys
import django
from django.conf import settings

# Setup Django
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'window_project.settings')
django.setup()

import psycopg2

def get_db():
    """Get database connection"""
    db_settings = settings.DATABASES['default']
    return psycopg2.connect(
        database=db_settings.get('NAME'),
        user=db_settings.get('USER'),
        password=db_settings.get('PASSWORD'),
        host=db_settings.get('HOST', 'localhost'),
        port=db_settings.get('PORT', '5432')
    )

# Test 1: Create persistent connection and staging table (NO ON COMMIT DROP)
print("="*60)
print("TEST 1: Create persistent connection and staging table (NO ON COMMIT DROP)")
print("="*60)

persistent_conn = get_db()
print(f"✅ Persistent connection created")

cursor = persistent_conn.cursor()

try:
    cursor.execute("""
        CREATE TEMP TABLE _tmp_test (
            id INTEGER
        )
    """)
    persistent_conn.commit()
    print("✅ TEMP TABLE _tmp_test created successfully (no ON COMMIT DROP)")
except Exception as e:
    print(f"❌ Failed to create TEMP TABLE: {e}")
    sys.exit(1)

# Test 2: Insert into staging table using same connection
print("\n" + "="*60)
print("TEST 2: Insert into staging table using same connection")
print("="*60)

try:
    cursor.execute("INSERT INTO _tmp_test (id) VALUES (1)")
    persistent_conn.commit()
    print("✅ INSERT successful")
except Exception as e:
    print(f"❌ INSERT failed: {e}")

# Test 3: Select from staging table
print("\n" + "="*60)
print("TEST 3: Select from staging table")
print("="*60)

try:
    cursor.execute("SELECT COUNT(*) FROM _tmp_test")
    result = cursor.fetchone()
    print(f"✅ SELECT successful: Count = {result[0]}")
except Exception as e:
    print(f"❌ SELECT failed: {e}")

# Test 4: Insert second row
print("\n" + "="*60)
print("TEST 4: Insert second row")
print("="*60)

try:
    cursor.execute("INSERT INTO _tmp_test (id) VALUES (2)")
    persistent_conn.commit()
    print("✅ Second INSERT successful")
except Exception as e:
    print(f"❌ Second INSERT failed: {e}")

# Clean up
cursor.close()
persistent_conn.close()

print("\n" + "="*60)
print("TEST COMPLETE - ALL OPERATIONS SHOULD SUCCEED")
print("="*60)