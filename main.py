#!/usr/bin/env python3
"""
BOM System - Field-Level Diff for ALL Tables
Complete BOM management with CSV import/export
"""

import os
import sys
import json
import csv
import psycopg2
from datetime import datetime

# ============================================================
# LOGGING FUNCTION
# ============================================================

def write_log(level, message):
    """Write to log file with timestamp"""
    log_file = "logs/pipeline_errors.log"
    os.makedirs('logs', exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}\n"
    
    with open(log_file, 'a') as f:
        f.write(log_entry)


# ============================================================
# SAMPLE DATA FOR TEMPLATE GENERATION
# ============================================================

SAMPLE_PRODUCTS = [
    ("3-inch stainless hinge", 12.50),
    ("4-inch aluminum hinge", 8.00),
    ("Stainless steel rivet", 0.25),
    ("Self-tapping screw", 0.15),
    ("Anchor bolt", 0.50),
    ("Silicone sealant", 5.00),
    ("Weatherstrip tape", 1.20),
    ("Epoxy adhesive", 8.50),
    ("Float glass 5mm", 15.00),
    ("Tempered glass", 25.00),
    ("Rivet gun bit", 3.00),
    ("Spacer block", 0.80),
    ("Cleaning cloth", 1.00),
    ("Window handle", 7.50),
    ("Rubber gasket", 2.00),
]

SAMPLE_BOMS = [
    ("Hinge Repair Kit", '[{"product_name": "3-inch stainless hinge", "qty": 2}, {"product_name": "Stainless steel rivet", "qty": 8}]'),
    ("Seal Kit", '[{"product_name": "Silicone sealant", "qty": 1}, {"product_name": "Weatherstrip tape", "qty": 5}]'),
    ("Glass Replacement", '[{"product_name": "Float glass 5mm", "qty": 1}, {"product_name": "Silicone sealant", "qty": 1}]'),
    ("Hardware Kit", '[{"product_name": "Window handle", "qty": 1}, {"product_name": "Self-tapping screw", "qty": 4}]'),
    ("Complete Overhaul", '[{"product_name": "3-inch stainless hinge", "qty": 2}, {"product_name": "Silicone sealant", "qty": 1}, {"product_name": "Stainless steel rivet", "qty": 12}]'),
]

SAMPLE_ORDER_ITEMS = [
    (1001, "Hinge Repair Kit", 2),
    (1001, "Seal Kit", 1),
    (1002, "Glass Replacement", 1),
    (1002, "Complete Overhaul", 1),
    (1003, "Hardware Kit", 1),
]


# ============================================================
# DATABASE CONNECTION (SILENT - NO DEBUG)
# ============================================================

import django
from django.conf import settings

# Setup Django once at module level
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'window_project.settings')
django.setup()

_persistent_conn = None

def get_db():
    """Get database connection - silent, no debug output"""
    db_settings = settings.DATABASES['default']
    return psycopg2.connect(
        database=db_settings.get('NAME'),
        user=db_settings.get('USER'),
        password=db_settings.get('PASSWORD'),
        host=db_settings.get('HOST', 'localhost'),
        port=db_settings.get('PORT', '5432'),
        connect_timeout=5
    )

def get_persistent_conn():
    """Get or create a persistent database connection"""
    global _persistent_conn
    if _persistent_conn is None or _persistent_conn.closed:
        _persistent_conn = get_db()
    return _persistent_conn

def run_sql(query, params=None, fetch=False, use_persistent=False):
    """Run SQL query"""
    if use_persistent:
        conn = get_persistent_conn()
        close_conn = False
    else:
        conn = get_db()
        close_conn = True
    
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            col_names = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            return [dict(zip(col_names, row)) for row in rows]
        else:
            conn.commit()
            return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        if close_conn:
            conn.close()


def table_exists(table_name):
    """Check if a table exists"""
    try:
        run_sql(f"SELECT 1 FROM {table_name} LIMIT 1", fetch=True)
        return True
    except:
        return False


# ============================================================
# DIRECTORY MANAGEMENT
# ============================================================

def ensure_directories():
    """Ensure required directories exist"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(os.path.join(script_dir, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'import'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'export'), exist_ok=True)
    os.makedirs(os.path.join(script_dir, 'logs'), exist_ok=True)
    return script_dir

def get_latest_csv_file(import_dir, keyword):
    """Find the latest CSV file containing the keyword"""
    matching_files = []
    
    if not os.path.exists(import_dir):
        return None
    
    for f in os.listdir(import_dir):
        if f.endswith('.csv') and keyword in f.lower():
            file_path = os.path.join(import_dir, f)
            mod_time = os.path.getmtime(file_path)
            matching_files.append((file_path, mod_time))
    
    if matching_files:
        return max(matching_files, key=lambda x: x[1])[0]
    return None

# ============================================================
# TEMPLATE GENERATION (SEED) - Option 2
# ============================================================

def generate_templates():
    """Generate CSV template files with sample data"""
    print("\n" + "="*60)
    print("GENERATING CSV TEMPLATES WITH SAMPLE DATA")
    print("="*60)
    
    script_dir = ensure_directories()
    templates_dir = os.path.join(script_dir, 'templates')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Products template
    products_file = os.path.join(templates_dir, f"products_template_{timestamp}.csv")
    with open(products_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['product_name', 'unit_price'])
        writer.writerow(['# List all parts/materials here', '# Price in USD'])
        for name, price in SAMPLE_PRODUCTS:
            writer.writerow([name, price])
    print(f"✓ Created: {products_file}")
    
    # BOMs template
    boms_file = os.path.join(templates_dir, f"boms_template_{timestamp}.csv")
    with open(boms_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['bom_name', 'components'])
        writer.writerow(['# Name of the service package', '# JSON array: [{"product_name": "exact name", "qty": number}]'])
        for name, components in SAMPLE_BOMS:
            writer.writerow([name, components])
    print(f"✓ Created: {boms_file}")
    
    # Order Items template
    order_file = os.path.join(templates_dir, f"order_items_template_{timestamp}.csv")
    with open(order_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['order_id', 'bom_name', 'order_qty'])
        writer.writerow(['# REQUIRED or EMPTY: Order ID (empty = NULL, can link later)', '# REQUIRED: Exact BOM name', '# REQUIRED: Quantity'])
        for order_id, bom_name, qty in SAMPLE_ORDER_ITEMS:
            writer.writerow([order_id, bom_name, qty])
    print(f"✓ Created: {order_file}")
    
    print("\n" + "="*60)
    print("TEMPLATES GENERATED SUCCESSFULLY!")
    print(f"\n📍 Files saved in: {templates_dir}/")
    print("="*60)
    
    return products_file, boms_file, order_file


# ============================================================
# EXPORT FUNCTIONS - Option 3
# ============================================================

def export_products_to_csv():
    """Export current products from database to CSV"""
    print(f"\n--- Exporting Products ---")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(script_dir, 'export')
    
    products = run_sql("SELECT product_name, unit_price FROM booking_productmaster ORDER BY product_name", fetch=True)
    
    if not products:
        print("  ⚠️ No products found in database.")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(export_dir, f"products_{timestamp}.csv")
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['product_name', 'unit_price'])
        for p in products:
            writer.writerow([p['product_name'], float(p['unit_price'])])
    
    print(f"  ✓ Exported {len(products)} products to: {filename}")
    return filename


def export_boms_to_csv():
    """Export current BOMs from database to CSV - ensures valid JSON format"""
    print(f"\n--- Exporting BOMs ---")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(script_dir, 'export')
    
    boms = run_sql("SELECT bom_name, components FROM booking_productbom ORDER BY bom_name", fetch=True)
    
    if not boms:
        print("  ⚠️ No BOMs found in database.")
        write_log("WARNING", "Export BOMs attempted but no BOMs found")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(export_dir, f"boms_{timestamp}.csv")
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['bom_name', 'components'])
        
        for b in boms:
            components = b['components']
            
            # Ensure components is in valid JSON list format
            if isinstance(components, dict):
                # Convert single dict to list
                components = [components]
            elif isinstance(components, str):
                try:
                    components = json.loads(components)
                    if isinstance(components, dict):
                        components = [components]
                except:
                    pass
            
            # Convert to JSON string with double quotes and proper formatting
            json_str = json.dumps(components, ensure_ascii=False)
            writer.writerow([b['bom_name'], json_str])
    
    print(f"  ✓ Exported {len(boms)} BOMs to: {filename}")
    write_log("SUCCESS", f"Exported {len(boms)} BOMs to {filename}")
    return filename

def export_order_items_to_csv():
    """Export current order items from database to CSV"""
    print(f"\n--- Exporting Order Items ---")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    export_dir = os.path.join(script_dir, 'export')
    
    items = run_sql("""
        SELECT oi.order_id, ob.bom_name, oi.order_qty
        FROM booking_orderitem oi
        JOIN booking_productbom ob ON oi.bom_id = ob.id
        ORDER BY oi.id
    """, fetch=True)
    
    if not items:
        print("  ⚠️ No order items found in database.")
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(export_dir, f"order_items_{timestamp}.csv")
    
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['order_id', 'bom_name', 'order_qty'])
        for item in items:
            order_id = item['order_id'] if item['order_id'] else ''
            writer.writerow([order_id, item['bom_name'], item['order_qty']])
    
    print(f"  ✓ Exported {len(items)} order items to: {filename}")
    return filename

def export_all_to_csv():
    """Export all tables to CSV files"""
    print("\n" + "="*60)
    print("EXPORTING CURRENT DATABASE TO CSV")
    print("="*60)
    
    export_products_to_csv()
    export_boms_to_csv()
    export_order_items_to_csv()
    
    print("\n" + "="*60)
    print("EXPORT COMPLETE!")
    print(f"Files saved in: {os.path.abspath('export')}/")
    print("="*60)


# ============================================================
# STAGING TABLE FUNCTIONS
# ============================================================

def create_staging_tables():
    """Create temporary tables for dry run validation"""
    print("\n--- Creating staging tables for validation ---")
    
    run_sql("""
        CREATE TEMP TABLE _tmp_productmaster (
            LIKE booking_productmaster INCLUDING ALL
        )
    """, use_persistent=True)
    print("  ✓ _tmp_productmaster created")
    
    run_sql("""
        CREATE TEMP TABLE _tmp_productbom (
            LIKE booking_productbom INCLUDING ALL
        )
    """, use_persistent=True)
    print("  ✓ _tmp_productbom created")
    
    run_sql("""
        CREATE TEMP TABLE _tmp_orderitem (
            order_id INTEGER,
            bom_name VARCHAR(200),
            order_qty INTEGER
        )
    """, use_persistent=True)
    print("  ✓ _tmp_orderitem created")
    
    print("  ✓ All staging tables created successfully")


# ============================================================
# VALIDATION FUNCTIONS
# ============================================================

def validate_products_with_staging(csv_filepath):
    """Validate products using staging table - detects duplicates"""
    print(f"\n--- VALIDATING PRODUCTS (with staging) ---")
    
    if not os.path.exists(csv_filepath):
        print(f"  ✗ File not found: {csv_filepath}")
        return [], [], 0, 0
    
    with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    valid_rows = [r for r in rows if not r.get('product_name', '').startswith('#')]
    
    if not valid_rows:
        print("  ✗ No data found in CSV file")
        return [], [], 0, 0
    
    critical_errors = []
    warnings = []
    valid_count = 0
    duplicate_count = 0
    seen_names = set()
    
    for idx, row in enumerate(valid_rows):
        name = row.get('product_name', '').strip()
        price_str = row.get('unit_price', '').strip()
        
        if not name:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Missing product_name")
            continue
        
        try:
            price = float(price_str)
            if price <= 0:
                critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid price: {price}")
                continue
            elif price > 10000:
                warnings.append(f"Row {idx+1}: WARNING - Very high price: ${price}")
        except ValueError:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid price format: '{price_str}'")
            continue
        
        if name in seen_names:
            duplicate_count += 1
            critical_errors.append(f"Row {idx+1}: CRITICAL - Duplicate product name '{name}' in CSV")
            continue
        
        seen_names.add(name)
        valid_count += 1
        
        try:
            run_sql("""
                INSERT INTO _tmp_productmaster (product_name, unit_price) 
                VALUES (%s, %s)
            """, (name, price), use_persistent=True)
        except Exception as e:
            if "duplicate key" in str(e).lower():
                duplicate_count += 1
                critical_errors.append(f"Row {idx+1}: CRITICAL - Product '{name}' already exists in database")
            else:
                critical_errors.append(f"Row {idx+1}: CRITICAL - Database error: {e}")
    
    print(f"  ✓ {valid_count} valid products (ready to import)")
    if duplicate_count:
        print(f"  ✗ {duplicate_count} duplicate products (will be skipped)")
    if critical_errors:
        print(f"  ✗ {len(critical_errors)} CRITICAL errors")
        print("\nFIRST 5 ERRORS:")
        for err in critical_errors[:5]:
            print(f"  {err}")
    
    return critical_errors, warnings, valid_count, duplicate_count


def validate_boms_with_staging(csv_filepath, product_names):
    """Validate BOMs using staging table"""
    print(f"\n--- VALIDATING BOMS (with staging) ---")
    
    if not os.path.exists(csv_filepath):
        print(f"  ✗ File not found: {csv_filepath}")
        return [], [], 0
    
    with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    valid_rows = [r for r in rows if not r.get('bom_name', '').startswith('#')]
    
    if not valid_rows:
        print("  ✗ No data found in CSV file")
        return [], [], 0
    
    critical_errors = []
    warnings = []
    valid_count = 0
    seen_names = set()
    
    for idx, row in enumerate(valid_rows):
        name = row.get('bom_name', '').strip()
        components_str = row.get('components', '').strip()
        # DEBUG: Print each row being processed
        print(f"  DEBUG: Processing row {idx+1}: bom_name='{name}', components='{components_str[:100]}...'")
        
        if not name:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Missing bom_name")
            continue
        
        if name in seen_names:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Duplicate BOM name '{name}' in CSV")
            continue
        
        if not components_str:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Missing components for BOM '{name}'")
            continue
        
        try:
            components = json.loads(components_str)
            if not isinstance(components, list):
                critical_errors.append(f"Row {idx+1}: CRITICAL - Components must be a JSON array")
                continue
            
            all_products_exist = True
            for comp in components:
                if 'product_name' not in comp:
                    critical_errors.append(f"Row {idx+1}: CRITICAL - Missing 'product_name' in component")
                    all_products_exist = False
                elif 'qty' not in comp:
                    critical_errors.append(f"Row {idx+1}: CRITICAL - Missing 'qty' in component")
                    all_products_exist = False
                elif not isinstance(comp['qty'], int) or comp['qty'] <= 0:
                    critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid qty: {comp.get('qty')}")
                    all_products_exist = False
                elif comp['product_name'] not in product_names:
                    critical_errors.append(f"Row {idx+1}: CRITICAL - Product '{comp['product_name']}' not found")
                    all_products_exist = False
            
            if not all_products_exist:
                continue
            
        except json.JSONDecodeError as e:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid JSON: {e}")
            continue
        
        existing = run_sql(
            "SELECT id FROM booking_productbom WHERE bom_name = %s",
            (name,), fetch=True, use_persistent=True
        )
        if existing:
            warnings.append(f"Row {idx+1}: WARNING - BOM '{name}' already exists (will be replaced)")
        
        seen_names.add(name)
        valid_count += 1
        
        try:
            run_sql("""
                INSERT INTO _tmp_productbom (bom_name, components) 
                VALUES (%s, %s)
            """, (name, components_str), use_persistent=True)
        except Exception as e:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Database error: {e}")
    
    print(f"  ✓ {valid_count} valid BOMs (ready to import)")
    if critical_errors:
        print(f"  ✗ {len(critical_errors)} CRITICAL errors")
        # DEBUG: Print each critical error
        print("\n  DETAILED CRITICAL ERRORS:")
        for err in critical_errors:
            print(f"    {err}")
    
    return critical_errors, warnings, valid_count


def validate_order_items_with_staging(csv_filepath, bom_names):
    """Validate Order Items using staging table - allows NULL order_id"""
    print(f"\n--- VALIDATING ORDER ITEMS (with staging) ---")
    
    if not os.path.exists(csv_filepath):
        print(f"  ✗ File not found: {csv_filepath}")
        return [], [], 0
    
    with open(csv_filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    
    valid_rows = [r for r in rows if not r.get('order_id', '').startswith('#')]
    
    if not valid_rows:
        print("  ✗ No data found in CSV file")
        return [], [], 0
    
    critical_errors = []
    warnings = []
    valid_count = 0
    
    for idx, row in enumerate(valid_rows):
        order_id_str = row.get('order_id', '').strip()
        bom_name = row.get('bom_name', '').strip()
        qty_str = row.get('order_qty', '').strip()
        
        if order_id_str == '':
            order_id = None
        else:
            try:
                order_id = int(order_id_str)
                if order_id <= 0:
                    critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid order_id: {order_id}")
                    continue
                
                order_exists = run_sql(
                    "SELECT id FROM booking_order WHERE id = %s",
                    (order_id,), fetch=True, use_persistent=True
                )
                if not order_exists:
                    warnings.append(f"Row {idx+1}: WARNING - Order ID {order_id} not found, will be inserted as NULL")
                    order_id = None
            except ValueError:
                critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid order_id format: '{order_id_str}'")
                continue
        
        if not bom_name:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Missing bom_name")
            continue
        
        if bom_name not in bom_names:
            critical_errors.append(f"Row {idx+1}: CRITICAL - BOM '{bom_name}' not found")
            continue
        
        try:
            qty = int(qty_str)
            if qty <= 0:
                critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid quantity: {qty}")
                continue
            elif qty > 100:
                warnings.append(f"Row {idx+1}: WARNING - Very high quantity: {qty}")
        except ValueError:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Invalid quantity: '{qty_str}'")
            continue
        
        valid_count += 1
        
        try:
            run_sql("""
                INSERT INTO _tmp_orderitem (order_id, bom_name, order_qty) 
                VALUES (%s, %s, %s)
            """, (order_id, bom_name, qty), use_persistent=True)
        except Exception as e:
            critical_errors.append(f"Row {idx+1}: CRITICAL - Database error: {e}")
    
    print(f"  ✓ {valid_count} valid order items (ready to import)")
    print(f"  ℹ️ Note: Order items with missing order_id will be inserted as NULL")
    
    if critical_errors:
        print(f"  ✗ {len(critical_errors)} CRITICAL errors")
    if warnings:
        print(f"  ⚠️ {len(warnings)} WARNINGS")
    
    return critical_errors, warnings, valid_count


# ============================================================
# FIELD-LEVEL DIFF CHECK FUNCTIONS
# ============================================================

def get_current_data():
    """Get current data from database for diff comparison"""
    current_products = {}
    current_boms = {}
    current_order_items = []
    
    try:
        products = run_sql("SELECT product_name, unit_price FROM booking_productmaster", fetch=True)
        for p in products:
            current_products[p['product_name']] = float(p['unit_price'])
    except:
        pass
    
    try:
        boms = run_sql("SELECT bom_name, components FROM booking_productbom", fetch=True)
        for b in boms:
            current_boms[b['bom_name']] = b['components']
    except:
        pass
    
    try:
        items = run_sql("""
            SELECT oi.order_id, ob.bom_name, oi.order_qty
            FROM booking_orderitem oi
            JOIN booking_productbom ob ON oi.bom_id = ob.id
        """, fetch=True)
        current_order_items = [(i['order_id'], i['bom_name'], i['order_qty']) for i in items]
    except:
        pass
    
    return current_products, current_boms, current_order_items


def get_csv_data(products_file, boms_file, order_file):
    """Get data from CSV files for diff comparison"""
    csv_products = {}
    csv_boms = {}
    csv_order_items = []
    
    if products_file and os.path.exists(products_file):
        with open(products_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('product_name', '').strip()
                if name and not name.startswith('#'):
                    try:
                        price = float(row.get('unit_price', 0))
                        csv_products[name] = price
                    except:
                        pass
    
    if boms_file and os.path.exists(boms_file):
        with open(boms_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('bom_name', '').strip()
                if name and not name.startswith('#'):
                    components = row.get('components', '').strip()
                    csv_boms[name] = components
    
    if order_file and os.path.exists(order_file):
        with open(order_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                order_id_str = row.get('order_id', '').strip()
                if order_id_str.startswith('#'):
                    continue
                
                if order_id_str == '':
                    order_id = None
                else:
                    try:
                        order_id = int(order_id_str)
                    except ValueError:
                        continue
                
                bom_name = row.get('bom_name', '').strip()
                if not bom_name:
                    continue
                
                try:
                    qty = int(row.get('order_qty', 0))
                    if qty > 0:
                        csv_order_items.append((order_id, bom_name, qty))
                except ValueError:
                    pass
    
    return csv_products, csv_boms, csv_order_items


def show_products_field_diff(current_products, csv_products):
    """Show field-level diff for Products"""
    print("\nPRODUCTS:")
    print("-"*40)
    
    has_changes = False
    current_set = set(current_products.keys())
    csv_set = set(csv_products.keys())
    
    new_products = csv_set - current_set
    if new_products:
        has_changes = True
        print(f"  NEW ({len(new_products)}):")
        for name in sorted(new_products)[:10]:
            print(f"     • {name} - ${csv_products[name]:.2f}")
        if len(new_products) > 10:
            print(f"     ... and {len(new_products) - 10} more")
    else:
        print("  No new products")
    
    deleted_products = current_set - csv_set
    if deleted_products:
        has_changes = True
        print(f"  DELETED ({len(deleted_products)}):")
        for name in sorted(deleted_products)[:10]:
            print(f"     • {name} - ${current_products[name]:.2f}")
        if len(deleted_products) > 10:
            print(f"     ... and {len(deleted_products) - 10} more")
    else:
        print("  No products will be deleted")
    
    changed_products = []
    for name in current_set & csv_set:
        if current_products[name] != csv_products[name]:
            changed_products.append((name, current_products[name], csv_products[name]))
            has_changes = True
    
    if changed_products:
        print(f"  CHANGED PRICE ({len(changed_products)}):")
        for name, old_price, new_price in changed_products[:10]:
            print(f"     • {name}: ${old_price:.2f} -> ${new_price:.2f}")
        if len(changed_products) > 10:
            print(f"     ... and {len(changed_products) - 10} more")
    else:
        print("  No price changes")
    
    unchanged_count = len(current_set & csv_set) - len(changed_products)
    if unchanged_count > 0:
        print(f"  {unchanged_count} products unchanged")
    
    print(f"\n  Products Summary:")
    print(f"     Current DB: {len(current_set)}")
    print(f"     CSV: {len(csv_set)}")
    print(f"     Net change: {len(csv_set) - len(current_set)}")
    
    return has_changes


def show_boms_field_diff(current_boms, csv_boms):
    """Show field-level diff for BOMs"""
    print("\nBOMS:")
    print("-"*40)
    
    has_changes = False
    current_bom_set = set(current_boms.keys())
    csv_bom_set = set(csv_boms.keys())
    
    new_boms = csv_bom_set - current_bom_set
    if new_boms:
        has_changes = True
        print(f"  NEW ({len(new_boms)}):")
        for name in sorted(new_boms)[:10]:
            print(f"     • {name}")
        if len(new_boms) > 10:
            print(f"     ... and {len(new_boms) - 10} more")
    else:
        print("  No new BOMs")
    
    deleted_boms = current_bom_set - csv_bom_set
    if deleted_boms:
        has_changes = True
        print(f"  DELETED ({len(deleted_boms)}):")
        for name in sorted(deleted_boms)[:10]:
            print(f"     • {name}")
        if len(deleted_boms) > 10:
            print(f"     ... and {len(deleted_boms) - 10} more")
    else:
        print("  No BOMs will be deleted")
    
    changed_boms = []
    for name in current_bom_set & csv_bom_set:
        if current_boms[name] != csv_boms[name]:
            changed_boms.append(name)
            has_changes = True
    
    if changed_boms:
        print(f"  CHANGED COMPONENTS ({len(changed_boms)}):")
        for name in changed_boms[:10]:
            print(f"     • {name}")
            try:
                current_comps = json.loads(current_boms[name]) if isinstance(current_boms[name], str) else current_boms[name]
                csv_comps = json.loads(csv_boms[name]) if isinstance(csv_boms[name], str) else csv_boms[name]
                
                current_dict = {c['product_name']: c['qty'] for c in current_comps}
                csv_dict = {c['product_name']: c['qty'] for c in csv_comps}
                
                added = set(csv_dict.keys()) - set(current_dict.keys())
                for prod in added:
                    print(f"        + ADDED: {csv_dict[prod]} x {prod}")
                
                removed = set(current_dict.keys()) - set(csv_dict.keys())
                for prod in removed:
                    print(f"        - REMOVED: {current_dict[prod]} x {prod}")
                
                common = set(current_dict.keys()) & set(csv_dict.keys())
                for prod in common:
                    if current_dict[prod] != csv_dict[prod]:
                        print(f"        ~ CHANGED: {prod}: {current_dict[prod]} -> {csv_dict[prod]}")
            except Exception as e:
                print(f"        Could not parse components: {e}")
        
        if len(changed_boms) > 10:
            print(f"     ... and {len(changed_boms) - 10} more")
    else:
        print("  No component changes")
    
    unchanged_bom_count = len(current_bom_set & csv_bom_set) - len(changed_boms)
    if unchanged_bom_count > 0:
        print(f"  {unchanged_bom_count} BOMs unchanged")
    
    print(f"\n  BOMs Summary:")
    print(f"     Current DB: {len(current_bom_set)}")
    print(f"     CSV: {len(csv_bom_set)}")
    print(f"     Net change: {len(csv_bom_set) - len(current_bom_set)}")
    
    return has_changes


def show_order_items_field_diff(current_order_items, csv_order_items):
    """Show field-level diff for Order Items"""
    print("\nORDER ITEMS:")
    print("-"*40)
    
    has_changes = False
    
    current_dict = {}
    for order_id, bom, qty in current_order_items:
        key = (order_id if order_id is not None else 'NULL', bom)
        current_dict[key] = qty
    
    csv_dict = {}
    for order_id, bom, qty in csv_order_items:
        key = (order_id if order_id is not None else 'NULL', bom)
        csv_dict[key] = qty
    
    current_keys = set(current_dict.keys())
    csv_keys = set(csv_dict.keys())
    
    new_items = csv_keys - current_keys
    if new_items:
        has_changes = True
        print(f"  NEW ({len(new_items)}):")
        for order_id, bom in list(new_items)[:10]:
            qty = csv_dict[(order_id, bom)]
            print(f"     • Order {order_id} -> {bom} x{qty}")
        if len(new_items) > 10:
            print(f"     ... and {len(new_items) - 10} more")
    else:
        print("  No new order items")
    
    deleted_items = current_keys - csv_keys
    if deleted_items:
        has_changes = True
        print(f"  DELETED ({len(deleted_items)}):")
        for order_id, bom in list(deleted_items)[:10]:
            qty = current_dict[(order_id, bom)]
            print(f"     • Order {order_id} -> {bom} x{qty}")
        if len(deleted_items) > 10:
            print(f"     ... and {len(deleted_items) - 10} more")
    else:
        print("  No order items will be deleted")
    
    changed_items = []
    for key in current_keys & csv_keys:
        if current_dict[key] != csv_dict[key]:
            changed_items.append((key, current_dict[key], csv_dict[key]))
            has_changes = True
    
    if changed_items:
        print(f"  CHANGED QUANTITY ({len(changed_items)}):")
        for (order_id, bom), old_qty, new_qty in changed_items[:10]:
            print(f"     • Order {order_id} -> {bom}: {old_qty} -> {new_qty}")
        if len(changed_items) > 10:
            print(f"     ... and {len(changed_items) - 10} more")
    else:
        print("  No quantity changes")
    
    unchanged_count = len(current_keys & csv_keys) - len(changed_items)
    if unchanged_count > 0:
        print(f"  {unchanged_count} order items unchanged")
    
    print(f"\n  Order Items Summary:")
    print(f"     Current DB: {len(current_keys)}")
    print(f"     CSV: {len(csv_keys)}")
    print(f"     Net change: {len(csv_keys) - len(current_keys)}")
    
    return has_changes


def show_diff_summary(current_products, csv_products, current_boms, csv_boms, current_order_items, csv_order_items):
    """Show complete field-level diff for all tables"""
    print("\n" + "="*60)
    print("DIFF CHECK: Current Database vs CSV Files")
    print("="*60)
    
    has_changes = False
    
    if show_products_field_diff(current_products, csv_products):
        has_changes = True
    
    if show_boms_field_diff(current_boms, csv_boms):
        has_changes = True
    
    if show_order_items_field_diff(current_order_items, csv_order_items):
        has_changes = True
    
    print("\n" + "="*60)
    if has_changes:
        print("CHANGES DETECTED! Import will update the database.")
    else:
        print("NO CHANGES DETECTED! Database is already up to date.")
    print("="*60)
    
    return has_changes


# ============================================================
# DRY RUN VALIDATION
# ============================================================

def run_dry_validation_enhanced():
    """Enhanced dry run with staging tables and field-level diff checking"""
    print("\n" + "="*60)
    print("DRY RUN VALIDATION")
    print("="*60)
    print("\nThis creates temporary tables to validate your data.")
    print("Validation follows dependency order: Products -> BOMs -> Order Items")
    print("No permanent changes will be made.\n")
    
    import_dir = 'import'
    
    if not os.path.exists(import_dir):
        print(f"  Import directory '{import_dir}' not found.")
        return False, [], [], False
    
    products_file = get_latest_csv_file(import_dir, 'product')
    boms_file = get_latest_csv_file(import_dir, 'bom')
    order_file = get_latest_csv_file(import_dir, 'order')
    
    print(f"  Products file: {os.path.basename(products_file) if products_file else 'NOT FOUND'}")
    print(f"  BOMs file: {os.path.basename(boms_file) if boms_file else 'NOT FOUND'}")
    print(f"  Order Items file: {os.path.basename(order_file) if order_file else 'NOT FOUND'}")
    print()
    
    if not products_file and not boms_file and not order_file:
        print("  No CSV files found in 'import/' folder.")
        return False, [], [], False
    
    # Create staging tables
    print("\n" + "="*60)
    print("CREATING STAGING TABLES")
    print("="*60)
    
    try:
        create_staging_tables()
        print("Staging tables created successfully")
    except Exception as e:
        print(f"Failed to create staging tables: {e}")
        return False, [], [], False
    
    # DIFF CHECK
    print("\n" + "="*60)
    print("DIFF CHECK: Comparing CSV with Current Database")
    print("="*60)
    
    current_products, current_boms, current_order_items = get_current_data()
    csv_products, csv_boms, csv_order_items = get_csv_data(products_file, boms_file, order_file)
    
    has_changes = show_diff_summary(current_products, csv_products, current_boms, csv_boms, current_order_items, csv_order_items)
    
    if not has_changes:
        print("\nNo changes needed. Database is already up to date.")
        return True, [], [], False
    
    all_critical = []
    all_warnings = []
    valid_counts = {'products': 0, 'boms': 0, 'order_items': 0}
    duplicate_counts = {'products': 0, 'boms': 0}
    
    product_names = set(csv_products.keys())

    try:
        existing = run_sql("SELECT product_name FROM booking_productmaster", fetch=True)
        product_names.update({p['product_name'] for p in existing})
    except:
        pass

    # In run_dry_validation_enhanced(), after product_names is built
    print(f"\n  DEBUG: Available product names for BOM validation:")
    for pn in sorted(product_names)[:20]:
        print(f"    - {pn}")
    if len(product_names) > 20:
        print(f"    ... and {len(product_names) - 20} more")
    
    bom_names = set(csv_boms.keys())
    try:
        existing = run_sql("SELECT bom_name FROM booking_productbom", fetch=True)
        bom_names.update({b['bom_name'] for b in existing})
    except:
        pass
    
    # LEVEL 1: Products
    print("\n" + "-"*40)
    print("LEVEL 1: Validating Products (no dependencies)")
    print("-"*40)
    
    if products_file:
        critical, warnings, valid, dup = validate_products_with_staging(products_file)
        all_critical.extend(critical)
        all_warnings.extend(warnings)
        valid_counts['products'] = valid
        duplicate_counts['products'] = dup
    
    if all_critical:
        print("\nCRITICAL errors found in Products. Stopping validation.")
        return False, all_critical, all_warnings, has_changes
    
    # LEVEL 2: BOMs
    print("\n" + "-"*40)
    print("LEVEL 2: Validating BOMs (depends on Products)")
    print("-"*40)
    
    if boms_file:
        critical, warnings, valid = validate_boms_with_staging(boms_file, product_names)
        all_critical.extend(critical)
        all_warnings.extend(warnings)
        valid_counts['boms'] = valid
    
    if all_critical:
        print("\nCRITICAL errors found in BOMs. Stopping validation.")
        return False, all_critical, all_warnings, has_changes
    
    # LEVEL 3: Order Items
    print("\n" + "-"*40)
    print("LEVEL 3: Validating Order Items (depends on BOMs)")
    print("-"*40)
    
    if order_file:
        critical, warnings, valid = validate_order_items_with_staging(order_file, bom_names)
        all_critical.extend(critical)
        all_warnings.extend(warnings)
        valid_counts['order_items'] = valid
    
    # Summary Report
    print("\n" + "="*60)
    print("DRY RUN VALIDATION REPORT")
    print("="*60)
    
    print(f"\nVALIDATION RESULTS (by dependency order):")
    print(f"   LEVEL 1 - Products:     {valid_counts['products']} valid")
    if duplicate_counts['products'] > 0:
        print(f"                         {duplicate_counts['products']} duplicates (will be skipped)")
    print(f"   LEVEL 2 - BOMs:         {valid_counts['boms']} valid")
    print(f"   LEVEL 3 - Order Items:  {valid_counts['order_items']} valid")
    
    if all_critical:
        print(f"\nCRITICAL ERRORS: {len(all_critical)} (MUST FIX)")
        for err in all_critical[:15]:
            print(f"     - {err}")
    else:
        print("\nNO CRITICAL ERRORS FOUND")
    
    if all_warnings:
        print(f"\nWARNINGS: {len(all_warnings)} (Review recommended)")
        for warn in all_warnings[:5]:
            print(f"     - {warn}")
    
    print("\n" + "="*60)
    return len(all_critical) == 0, all_critical, all_warnings, has_changes


# ============================================================
# IMPORT FUNCTIONS
# ============================================================

def clear_table(table_name):
    """Delete all records from a table"""
    try:
        run_sql(f"DELETE FROM {table_name}")
        print(f"  Cleared {table_name}")
        return True
    except Exception as e:
        print(f"  Failed to clear {table_name}: {e}")
        return False


def copy_staging_to_real():
    """Copy data from staging tables to real tables"""

    # Verify staging tables exist before proceeding
    try:
        run_sql("SELECT 1 FROM _tmp_productmaster LIMIT 1", fetch=True, use_persistent=True)
    except Exception as e:
        print("\n  ✗ Staging tables not found!")
        print("    This can happen if:")
        print("    1. You didn't run the dry run first")
        print("    2. The database connection was interrupted")
        print("    3. You ran import without completing dry run")
        print("\n  Please run Option 4 again.")
        return False
    
    product_count = run_sql("SELECT COUNT(*) as cnt FROM _tmp_productmaster", fetch=True, use_persistent=True)
    bom_count = run_sql("SELECT COUNT(*) as cnt FROM _tmp_productbom", fetch=True, use_persistent=True)
    order_count = run_sql("SELECT COUNT(*) as cnt FROM _tmp_orderitem", fetch=True, use_persistent=True)
    
    print(f"\n  Staging data summary:")
    print(f"    Products: {product_count[0]['cnt'] if product_count else 0}")
    print(f"    BOMs: {bom_count[0]['cnt'] if bom_count else 0}")
    print(f"    Order Items: {order_count[0]['cnt'] if order_count else 0}")
    
    print("\n  Clearing real tables in reverse dependency order...")
    
    run_sql("DELETE FROM booking_orderitem", use_persistent=True)
    print("    Cleared OrderItems")
    
    run_sql("DELETE FROM booking_productbom", use_persistent=True)
    print("    Cleared BOMs")
    
    run_sql("DELETE FROM booking_productmaster", use_persistent=True)
    print("    Cleared Products")
    
    print("\n  Copying data from staging to real tables...")
    
    # Products
    run_sql("""
        INSERT INTO booking_productmaster (product_name, unit_price)
        SELECT product_name, unit_price FROM _tmp_productmaster
    """, use_persistent=True)
    print("    Products copied")
    
    # BOMs
    run_sql("""
        INSERT INTO booking_productbom (bom_name, components)
        SELECT bom_name, components FROM _tmp_productbom
    """, use_persistent=True)
    print("    BOMs copied")
    
    # Order Items
    run_sql("""
        INSERT INTO booking_orderitem (order_id, bom_id, order_qty, order_description)
        SELECT 
            ti.order_id,
            tb.id,
            ti.order_qty,
            COALESCE(o.name, '')
        FROM _tmp_orderitem ti
        JOIN booking_productbom tb ON ti.bom_name = tb.bom_name
        LEFT JOIN booking_order o ON ti.order_id = o.id
    """, use_persistent=True)
    print("    Order Items copied")
    
    print("\n  All data copied successfully!")
    return True

def run_full_import():
    """Import with automatic dry run first"""
    print("\n" + "="*60)
    print("IMPORT DATA FROM CSV")
    print("="*60)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    import_dir = os.path.join(script_dir, 'import')
    
    if not os.path.exists(import_dir):
        print(f"\n  Import directory '{import_dir}' not found.")
        return False
    
    products_file = get_latest_csv_file(import_dir, 'product')
    boms_file = get_latest_csv_file(import_dir, 'bom')
    order_file = get_latest_csv_file(import_dir, 'order')
    
    print(f"\n  Products file: {os.path.basename(products_file) if products_file else 'NOT FOUND'}")
    print(f"  BOMs file: {os.path.basename(boms_file) if boms_file else 'NOT FOUND'}")
    print(f"  Order Items file: {os.path.basename(order_file) if order_file else 'NOT FOUND'}")
    print()
    
    if not products_file and not boms_file and not order_file:
        print("\n  No CSV files found in 'import/' folder.")
        return False
    
    print("\n" + "-"*40)
    print("TABLE DEPENDENCY ORDER:")
    print("-"*40)
    print("   LEVEL 1: Products (no dependencies)")
    print("   LEVEL 2: BOMs (depends on Products)")
    print("   LEVEL 3: Order Items (depends on BOMs and Orders)")
    print("-"*40)
    
    print("\n" + "="*60)
    print("STEP 1: DRY RUN VALIDATION (No database changes)")
    print("="*60)
    
    is_valid, critical_errors, warnings, has_changes = run_dry_validation_enhanced()
    
    if not has_changes:
        print("\n" + "="*60)
        print("NO CHANGES DETECTED!")
        print("="*60)
        print("\nYour CSV files match the current database.")
        print("No import needed.")
        return True
    
    if not is_valid:
        print("\n" + "="*60)
        print("VALIDATION FAILED!")
        print("="*60)
        print("\nPlease fix the CRITICAL errors above and try again.")
        print("\nNo changes were made to your database.")
        return False
    
    print("\n" + "="*60)
    print("VALIDATION PASSED!")
    print("="*60)
    
    if warnings:
        print(f"\nWARNINGS ({len(warnings)}):")
        for warn in warnings[:5]:
            print(f"     - {warn}")
    
    print("\nWhat will happen (in dependency order):")
    print("   LEVEL 1: All existing Products will be REPLACED")
    print("   LEVEL 2: All existing BOMs will be REPLACED")
    print("   LEVEL 3: All existing Order Items will be REPLACED")
    print("\n   This action CANNOT be undone!")
    
    print("\n" + "-"*40)
    confirm = input("Proceed with import? (yes/no): ").strip().lower()
    
    if confirm not in ['yes', 'y']:
        print("\nImport cancelled. No changes were made.")
        return False
    
    print("\n" + "="*60)
    print("STEP 2: COPYING DATA TO REAL TABLES")
    print("="*60)
    
    success = copy_staging_to_real()
    
    if success:
        print("\n" + "="*60)
        print("IMPORT COMPLETED SUCCESSFULLY!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("IMPORT FAILED!")
        print("="*60)
    
    return success


# ============================================================
# VIEW FUNCTIONS - Options 5-8 (WITH COLUMN HEADINGS)
# ============================================================

def show_products():
    """Display all products"""
    products = run_sql("SELECT id, product_name, unit_price FROM booking_productmaster ORDER BY product_name", fetch=True)
    
    if not products:
        print("\nNo products found.")
        return
    
    print("\n" + "="*70)
    print("PRODUCT MASTER LIST")
    print("="*70)
    print(f"{'ID':<6} {'Product Name':<45} {'Price':<12}")
    print("-"*70)
    
    for p in products:
        name = p['product_name'][:42] + '...' if len(p['product_name']) > 45 else p['product_name']
        print(f"{p['id']:<6} {name:<45} ${float(p['unit_price']):<10.2f}")
    
    print("-"*70)
    print(f"Total: {len(products)} products")
    print("="*70)


def show_boms():
    """Display all BOMs with column headings"""
    boms = run_sql("SELECT id, bom_name, components FROM booking_productbom ORDER BY bom_name", fetch=True)
    
    if not boms:
        print("\nNo BOMs found.")
        return
    
    print("\n" + "="*80)
    print(" " * 28 + "BILL OF MATERIALS (BOMs)")
    print("="*80)
    
    missing_products = set()
    
    for bom in boms:
        print(f"\n--- BOM ID: {bom['id']} | BOM Name: {bom['bom_name']} ---")
        print("-" * 80)
        print(f"{'Qty':<8} {'Product Name':<50} {'Status':<22}")
        print("-" * 80)
        
        comps = bom['components']
        
        if isinstance(comps, str):
            try:
                comps = json.loads(comps)
            except:
                print(f"{'ERROR':<8} {'Failed to parse JSON':<50} {'ERROR':<22}")
                print("-" * 80)
                continue
        
        if isinstance(comps, dict):
            comps = [comps]
        
        if not isinstance(comps, list):
            print(f"{'ERROR':<8} {'Unexpected format':<50} {'ERROR':<22}")
            print("-" * 80)
            continue
        
        for comp in comps:
            product_name = comp.get('product_name')
            qty = comp.get('qty')
            
            if not product_name:
                print(f"{'?':<8} {'Missing product name':<50} {'ERROR':<22}")
                continue
            
            if not qty:
                print(f"{'?':<8} {product_name:<50} {'Missing qty':<22}")
                continue
            
            try:
                result = run_sql(
                    "SELECT unit_price FROM booking_productmaster WHERE product_name = %s",
                    (product_name,), fetch=True, use_persistent=False
                )
                
                if result and len(result) > 0:
                    price = float(result[0]['unit_price'])
                    print(f"{qty:<8} {product_name:<50} {'FOUND @ $' + format(price, '.2f'):<22}")
                else:
                    print(f"{qty:<8} {product_name:<50} {'NOT FOUND':<22}")
                    missing_products.add(product_name)
            except:
                print(f"{qty:<8} {product_name:<50} {'ERROR':<22}")
                missing_products.add(product_name)
        
        print("-" * 80)
    
    print("\n" + "="*80)
    print(f"TOTAL BOMs: {len(boms)}")
    
    if missing_products:
        print("\n" + "="*80)
        print(" " * 25 + "MISSING PRODUCTS SUMMARY")
        print("="*80)
        print(f"{'Product Name':<50} {'Status':<30}")
        print("-" * 80)
        for prod in sorted(missing_products):
            print(f"{prod:<50} {'NOT FOUND in ProductMaster':<30}")
        print("-" * 80)
        print("\nTO FIX:")
        print("   1. Add these products to products.csv")
        print("   2. Run Option 4 to import")
    print("="*80)


def show_orders():
    """Display all order summaries - with Order Item ID for unlinked items"""
    items = run_sql("""
        SELECT 
            oi.id,
            oi.order_id, 
            oi.order_qty,
            oi.order_description,
            ob.bom_name,
            ob.components
        FROM booking_orderitem oi
        JOIN booking_productbom ob ON oi.bom_id = ob.id
        ORDER BY oi.id
    """, fetch=True)
    
    if not items:
        print("\n[WARNING] No order items found.")
        return
    
    # Track missing products across all orders
    all_missing_products = set()
    
    # Separate linked and unlinked items
    linked_items = [i for i in items if i['order_id'] is not None]
    unlinked_items = [i for i in items if i['order_id'] is None]
    
    print("\n" + "="*80)
    print(" " * 30 + "ORDER SUMMARY")
    print("="*80)
    
    # Show linked orders (with cost calculation)
    if linked_items:
        print("\n--- LINKED ORDERS (with costs) ---")
        print("-" * 80)
        print(f"{'Order ID':<12} {'Order Name':<35} {'Total Cost':<15} {'Status':<10}")
        print("-" * 80)
        
        # Group by order_id
        order_groups = {}
        for item in linked_items:
            order_id = item['order_id']
            if order_id not in order_groups:
                order_groups[order_id] = []
            order_groups[order_id].append(item)
        
        grand_total = 0
        for order_id, order_items in order_groups.items():
            # Get order name
            order_info = run_sql(
                "SELECT name FROM booking_order WHERE id = %s",
                (order_id,), fetch=True
            )
            order_name = order_info[0]['name'] if order_info else f"Order {order_id}"
            
            # Calculate total cost for this order
            total_cost = 0
            has_missing = False
            for item in order_items:
                comps = item['components']
                if isinstance(comps, str):
                    comps = json.loads(comps)
                if isinstance(comps, dict):
                    comps = [comps]
                
                for comp in comps:
                    product_name = comp.get('product_name')
                    qty = comp.get('qty', 0)
                    if product_name:
                        product = run_sql(
                            "SELECT unit_price FROM booking_productmaster WHERE product_name = %s",
                            (product_name,), fetch=True
                        )
                        if product:
                            total_cost += qty * item['order_qty'] * float(product[0]['unit_price'])
                        else:
                            all_missing_products.add(product_name)
                            has_missing = True
            
            grand_total += total_cost
            display_name = order_name[:32] + '..' if len(order_name) > 35 else order_name
            status = "MISSING" if has_missing else "OK"
            print(f"{order_id:<12} {display_name:<35} ${total_cost:<14.2f} {status:<10}")
        
        print("-" * 80)
        print(f"{'GRAND TOTAL':<47} ${grand_total:<14.2f}")
        print("-" * 80)
    
    # Show unlinked orders (NULL order_id) - WITH ORDER ITEM ID
    if unlinked_items:
        print("\n--- UNLINKED ORDER ITEMS (need to link in Admin) ---")
        print("-" * 80)
        print(f"{'ID':<6} {'Order Description':<40} {'BOM Name':<22} {'Qty':<6}")
        print("-" * 80)
        for item in unlinked_items:
            item_id = item['id']
            desc = item['order_description'][:37] + '..' if len(item['order_description']) > 40 else item['order_description']
            print(f"{item_id:<6} {desc:<40} {item['bom_name']:<22} {item['order_qty']:<6}")
        print("-" * 80)
        print("\n  TIP: Go to Django Admin -> Order Items -> Edit the ID above to link")
    
    # Show missing products summary
    if all_missing_products:
        print("\n" + "="*80)
        print(" " * 25 + "MISSING PRODUCTS ACROSS ALL ORDERS")
        print("="*80)
        print(f"{'Product Name':<50} {'Status':<30}")
        print("-" * 80)
        for prod in sorted(all_missing_products):
            print(f"{prod:<50} {'NOT FOUND in ProductMaster':<30}")
        print("-" * 80)
        print("\nTO FIX:")
        print("   1. Add these products to products.csv")
        print("   2. Run Option 4 to import")
    
    print("\n" + "="*80)

def show_order_detail():
    """Show detailed breakdown for a specific order with column headings"""
    orders = run_sql("""
        SELECT DISTINCT oi.order_id, o.name 
        FROM booking_orderitem oi 
        JOIN booking_order o ON oi.order_id = o.id 
        WHERE oi.order_id IS NOT NULL
        ORDER BY oi.order_id
    """, fetch=True)
    
    if not orders:
        print("\nNo linked order items found.")
        print("   (Items with NULL order_id will not appear here - link them in Admin first)")
        return
    
    print("\n" + "="*80)
    print(" " * 28 + "AVAILABLE ORDERS (Linked)")
    print("="*80)
    for i, order in enumerate(orders, 1):
        name = order['name'][:57] + '..' if len(order['name']) > 60 else order['name']
        print(f"  {i}. Order {order['order_id']}: {name}")
    
    try:
        choice = int(input("\nSelect order number: ")) - 1
        if 0 <= choice < len(orders):
            selected_order_id = orders[choice]['order_id']
            
            items = run_sql("""
                SELECT oi.order_qty, ob.components, ob.bom_name
                FROM booking_orderitem oi
                JOIN booking_productbom ob ON oi.bom_id = ob.id
                WHERE oi.order_id = %s
            """, (selected_order_id,), fetch=True)
            
            if not items:
                print("No items found for this order.")
                return
            
            total_cost = 0
            missing_products = set()
            
            print("\n" + "="*80)
            print(f" " * 30 + f"ORDER {selected_order_id} DETAILS")
            print("="*80)
            
            for item in items:
                components = item['components']
                if isinstance(components, str):
                    components = json.loads(components)
                if isinstance(components, dict):
                    components = [components]
                
                print(f"\n--- BOM: {item['bom_name']} | Quantity: {item['order_qty']} ---")
                print("-" * 80)
                print(f"{'Product Name':<35} {'Unit Price':<15} {'Qty Used':<12} {'Subtotal':<15}")
                print("-" * 80)
                
                item_cost = 0
                for comp in components:
                    product_name = comp.get('product_name')
                    bom_qty = comp.get('qty', 0)
                    
                    product = run_sql(
                        "SELECT product_name, unit_price FROM booking_productmaster WHERE product_name = %s",
                        (product_name,), fetch=True
                    )
                    
                    if product and len(product) > 0:
                        qty_used = bom_qty * item['order_qty']
                        unit_price = float(product[0]['unit_price'])
                        cost = qty_used * unit_price
                        item_cost += cost
                        display_name = product_name[:32] + '..' if len(product_name) > 35 else product_name
                        print(f"{display_name:<35} ${unit_price:<14.2f} {qty_used:<12} ${cost:<14.2f}")
                    else:
                        missing_products.add(product_name)
                        qty_used = bom_qty * item['order_qty']
                        display_name = product_name[:32] + '..' if len(product_name) > 35 else product_name
                        print(f"{display_name:<35} {'NOT FOUND':<15} {qty_used:<12} {'$0.00':<15}")
                
                print("-" * 80)
                print(f"{'BOM TOTAL':<62} ${item_cost:>14.2f}")
                print("-" * 80)
                total_cost += item_cost
            
            print("\n" + "="*80)
            print(f"{'ORDER GRAND TOTAL':<68} ${total_cost:>11.2f}")
            print("="*80)
            
            if missing_products:
                print("\n" + "="*80)
                print(" " * 25 + "MISSING PRODUCTS IN THIS ORDER")
                print("="*80)
                print(f"{'Product Name':<50} {'Status':<30}")
                print("-"*80)
                for prod in sorted(missing_products):
                    print(f"{prod:<50} {'NOT FOUND in ProductMaster':<30}")
                print("-"*80)
                print("\nTO FIX:")
                print("   1. Add these products to products.csv")
                print("   2. Run Option 4 to import")
                print("="*80)
        else:
            print("Invalid selection")
    except ValueError:
        print("Invalid input")


# ============================================================
# SYSTEM FUNCTIONS - Options 9-10
# ============================================================

def show_history_log():
    """Display pipeline error log in descending order"""
    print("\n" + "="*60)
    print("PIPELINE HISTORY LOG (Newest First)")
    print("="*60)
    
    log_file = "logs/pipeline_errors.log"
    
    if not os.path.exists(log_file):
        print("\nNo log file found. Pipeline history is empty.")
        return
    
    with open(log_file, 'r') as f:
        lines = f.readlines()
    
    if not lines:
        print("\nLog file is empty.")
        return
    
    reversed_lines = lines[::-1]
    show_count = min(20, len(reversed_lines))
    
    print(f"\nShowing last {show_count} of {len(lines)} total entries\n")
    print("-"*60)
    
    for line in reversed_lines[:show_count]:
        if "ERROR" in line:
            print(f"[ERROR] {line.strip()}")
        elif "WARNING" in line:
            print(f"[WARNING] {line.strip()}")
        elif "SUCCESS" in line:
            print(f"[SUCCESS] {line.strip()}")
        else:
            print(f"{line.strip()}")
    
    print("-"*60)
    
    if len(reversed_lines) > 20:
        print(f"\nTotal {len(lines)} entries. Showing last 20.")
        print(f"Full log: {os.path.abspath(log_file)}")
    
    print("="*60)


def generate_error_template():
    """Generate CSV template showing common errors"""
    print("\n" + "="*60)
    print("GENERATING ERROR TEMPLATE WITH COMMON ISSUES")
    print("="*60)
    
    script_dir = ensure_directories()
    templates_dir = os.path.join(script_dir, 'templates')
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    products_file = os.path.join(templates_dir, f"products_error_template_{timestamp}.csv")
    with open(products_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['product_name', 'unit_price'])
        writer.writerow(['# ERROR: Missing product_name'])
        writer.writerow(['', '15.00'])
        writer.writerow(['# ERROR: Invalid price (negative or zero)'])
        writer.writerow(['Invalid product', '-5.00'])
        writer.writerow(['Another product', '0.00'])
        writer.writerow(['# ERROR: Duplicate product name'])
        writer.writerow(['3-inch stainless hinge', '12.50'])
        writer.writerow(['3-inch stainless hinge', '15.00'])
        writer.writerow(['# CORRECT EXAMPLES'])
        writer.writerow(['Correct Product A', '25.00'])
        writer.writerow(['Correct Product B', '30.50'])
    print(f"✓ Created: {products_file}")
    
    boms_file = os.path.join(templates_dir, f"boms_error_template_{timestamp}.csv")
    with open(boms_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['bom_name', 'components'])
        writer.writerow(['# ERROR: Missing bom_name'])
        writer.writerow(['', '[{"product_name": "hinge", "qty": 2}]'])
        writer.writerow(['# ERROR: Invalid JSON'])
        writer.writerow(['Bad JSON', '{"product_name": "hinge", "qty": 2}'])
        writer.writerow(['# ERROR: Non-existent product'])
        writer.writerow(['Bad BOM', '[{"product_name": "Non-existent", "qty": 2}]'])
        writer.writerow(['# CORRECT EXAMPLES'])
        writer.writerow(['Good BOM', '[{"product_name": "3-inch stainless hinge", "qty": 2}]'])
    print(f"✓ Created: {boms_file}")
    
    order_file = os.path.join(templates_dir, f"order_items_error_template_{timestamp}.csv")
    with open(order_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['order_id', 'bom_name', 'order_qty'])
        writer.writerow(['# ERROR: Missing order_id'])
        writer.writerow(['', 'Hinge Repair Kit', '2'])
        writer.writerow(['# ERROR: Order ID not found in Order table'])
        writer.writerow(['9999', 'Hinge Repair Kit', '2'])
        writer.writerow(['# ERROR: Missing bom_name'])
        writer.writerow(['1001', '', '2'])
        writer.writerow(['# ERROR: Invalid quantity'])
        writer.writerow(['1001', 'Hinge Repair Kit', '0'])
        writer.writerow(['# CORRECT EXAMPLES'])
        writer.writerow(['1001', 'Hinge Repair Kit', '2'])
    print(f"✓ Created: {order_file}")
    
    print("\n" + "="*60)
    print("ERROR TEMPLATES GENERATED!")
    print(f"Location: {templates_dir}/")
    print("="*60)


def show_import_behavior_explanation():
    """Show explanation of import error handling"""
    print("\n" + "="*60)
    print("IMPORT BEHAVIOR EXPLANATION")
    print("="*60)
    print("""
HOW IMPORT HANDLES ERRORS
=========================

QUESTION: If some data has errors, will it affect all data import?

ANSWER: NO! Only bad rows are skipped. Good rows are imported.

EXAMPLE: Importing 10 products
    Row 1:  Good -> Imported
    Row 2:  Missing name -> SKIPPED
    Row 3:  Good -> Imported
    Row 4:  Invalid price -> SKIPPED
    Rows 5-10: All good -> Imported

    RESULT: 8 products imported, 2 errors reported

FEATURES:
    * FIELD-LEVEL DIFF: Shows exactly what changed in each table
    * AUTO SKIP: No changes? No import needed
    * Staging tables: Safe validation, no DB changes
    * Dependency order: Products -> BOMs -> Order Items
    * AUTO-FILL: order_description filled from Order.name during import
""")
    print("="*60)


def error_prevention_menu():
    """Sub-menu for error prevention tools"""
    while True:
        print("\n" + "="*50)
        print("ERROR PREVENTION & VALIDATION TOOLS")
        print("="*50)
        print("\n  1. Generate Error Templates (examples)")
        print("  2. Show Import Behavior Explanation")
        print("  3. Back to Main Menu")
        print("-"*50)
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            generate_error_template()
            input("\nPress Enter to continue...")
        elif choice == "2":
            show_import_behavior_explanation()
            input("\nPress Enter to continue...")
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
            input("\nPress Enter to continue...")


def test_connection():
    """Test database connectivity - silent"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        print(" Connection successful!")
        
        if table_exists('booking_productmaster'):
            print(" booking_productmaster table exists")
        else:
            print(" booking_productmaster missing - run migrations")
            
        if table_exists('booking_productbom'):
            print(" booking_productbom table exists")
        else:
            print(" booking_productbom missing - run migrations")
            
        if table_exists('booking_orderitem'):
            print(" booking_orderitem table exists")
        else:
            print(" booking_orderitem missing - run migrations")
            
    except Exception as e:
        print(f" Connection failed: {e}")


# ============================================================
# MAIN MENU
# ============================================================

def clear_screen():
    return

def print_menu():
    print("\n" + "="*55)
    print("       BOM SYSTEM MENU")
    print("="*55)
    print("  SETUP:")
    print("  1. Test Database Connection")
    print("  CSV OPERATIONS:")
    print("  2. Generate CSV Templates (SEED)")
    print("  3. Export Current Data to CSV")
    print("  4. Import Data from CSV (Auto Dry Run + Import)")
    print("  VIEW DATA:")
    print("  5. Show All Products")
    print("  6. Show All BOMs")
    print("  7. Show All Orders (Summary)")
    print("  8. Show Single Order Detail")
    print("  SYSTEM:")
    print("  9. Show History Log (Newest First)")
    print(" 10. Error Prevention & Validation Tools")
    print()
    print("  0. Exit")
    print("="*55)
    print("FEATURES:")
    print("   * Field-level diff for all tables")
    print("   * No changes? Skip import automatically")
    print("   * order_description auto-filled from Order.name")
    print("="*55)


def main():
    """Main program loop"""
    while True:
        clear_screen()
        print_menu()
        
        choice = input("Enter your choice (0-10): ").strip()
        
        if choice == "1":
            test_connection()
            input("\nPress Enter to continue...")
        
        elif choice == "2":
            generate_templates()
            input("\nPress Enter to continue...")
        
        elif choice == "3":
            export_all_to_csv()
            input("\nPress Enter to continue...")
        
        elif choice == "4":
            run_full_import()
            input("\nPress Enter to continue...")
        
        elif choice == "5":
            show_products()
            input("\nPress Enter to continue...")
        
        elif choice == "6":
            show_boms()
            input("\nPress Enter to continue...")
        
        elif choice == "7":
            show_orders()
            input("\nPress Enter to continue...")
        
        elif choice == "8":
            show_order_detail()
            input("\nPress Enter to continue...")
        
        elif choice == "9":
            show_history_log()
            input("\nPress Enter to continue...")
        
        elif choice == "10":
            error_prevention_menu()
        
        elif choice == "0":
            print("\nGoodbye!")
            sys.exit(0)
        
        else:
            print("Invalid choice. Please enter 0-10.")
            input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()