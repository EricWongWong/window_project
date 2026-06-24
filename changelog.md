# CHANGELOG.md

## Release v1.3.2: WebSocket Real-Time + Login/Register Improvements 🚀

### 🆕 New Features

#### WebSocket Real-Time Dashboard
- **Real-Time Updates** - Dashboard updates instantly when orders change
- **Signal Triggers** - Automatic updates triggered by order creation/update/deletion
- **Multiple Client Support** - Multiple staff members can view real-time updates
- **Automatic Reconnection** - WebSocket reconnects automatically with exponential backoff strategy
- **Connection Status Indicator** - Visual indicator showing live/offline status
- **Polling Fallback** - Automatic fallback to polling (30-second interval) if WebSocket is unavailable

#### Login/Register Improvements
- **Email Field** - Users can now enter their email during registration
- **Profile Page** - Users can view and edit their profile information
- **Change Password** - Users can change their password from profile page
- **Always Visible Tabs** - Login/Register tabs are now always visible without hovering

### 🐛 Bug Fixes
- Email address is now properly saved when users register
- Profile page correctly displays user email
- Password change redirects to profile page instead of dashboard
- Registration shows detailed error messages instead of generic failures
- Fixed circular import issues in WebSocket implementation
- Fixed WebSocket consumer data handling

### 📁 Files Added/Changed

#### New Files
- `member/signals.py` - Signal triggers for auto-updates
- `member/utils.py` - Dashboard data utilities
- `booking/templates/booking/profile.html` - Profile page
- `booking/templates/booking/change_password.html` - Password change page
- `test_signals.py` - Signal testing script

#### Modified Files
- `member/consumers.py` - WebSocket consumer
- `member/views.py` - Email capture, profile view, change password
- `member/urls.py` - Profile and change password URLs, added `app_name = 'member'`
- `member/apps.py` - Signal registration
- `member/routing.py` - WebSocket routing
- `member/__init__.py` - App config registration
- `member/templates/member/register.html` - Email field, visible tabs
- `member/templates/member/login.html` - Visible tabs
- `templates/member/dashboard.html` - WebSocket UI with real-time updates
- `window_project/asgi.py` - WebSocket support
- `window_project/settings.py` - Channel layers configuration
- `templates/base.html` - Dashboard navigation link

### 🔧 Technical Implementation
- Django Channels for WebSocket support
- InMemoryChannelLayer for development (Redis ready for production)
- Signal-based auto-updates on order changes
- Alpine.js for reactive frontend and WebSocket handling
- Polling fallback every 30 seconds
- Real-time WebSocket updates when orders change

### 📦 Dependencies Added
```txt
channels==4.0.0
channels-redis==4.1.0
redis==5.0.1
daphne==4.0.0
```

### 📝 Testing Notes
- Login as staff and open dashboard
- WebSocket should connect automatically (connection indicator shows "Live")
- Add/update an order in admin
- Dashboard should update instantly without refresh
- Multiple staff should see updates simultaneously
- If WebSocket fails, polling will take over (30-second interval)
- Register a new account - email should be saved
- Login and go to profile - email should be visible
- Edit profile - changes should save correctly
- Change password - should redirect back to profile
- Login/Register tabs should be visible at all times

### 🎯 Summary
This release combines real-time WebSocket updates with improved user authentication and profile management. Staff can now see instant order updates, while users benefit from a better registration and profile experience. The dashboard features a hybrid approach with WebSocket as primary and polling as fallback for reliability.

---

## Release v1.3.1: BOM CLI Pipeline with Import/Export (fine tune release v1.1.0) 🚀

### 🆕 New Features

#### CLI Menu System
- **Interactive Menu** - 10+ options for managing BOM data via command line
- **CSV Templates** - Generate sample CSV templates with seed data for Products, BOMs, and Order Items
- **Export All Data** - Export current database to CSV files
- **View Data** - Display Products, BOMs, Order Summaries, and detailed Order breakdowns
- **Error Prevention Tools** - Generate error templates showing common import issues

#### Database & Validation Improvements
- **Table Dependency Validation** - Prevents orphaned records by validating dependencies
- **Comprehensive Error Reporting** - Detailed error messages with row numbers
- **Connection Testing** - Test database connectivity and verify table existence
- **History Logging** - All pipeline operations logged with timestamps

### 🐛 Bug Fixes
- Fixed import validation to handle edge cases (empty files, malformed JSON)
- Fixed BOM component validation to properly detect missing products
- Fixed order item validation allowing NULL order_id with warning
- Fixed duplicate handling - duplicates now skipped instead of failing entire import
- Improved error messages with row numbers for easier debugging

### 📁 Files Added/Changed

#### New Files
- `main.py` - Interactive CLI menu system
- `test_env.py` - Environment variable testing
- `test_staging.py` - Staging table testing
- `data/imports/` - CSV import directory
- `data/exports/` - CSV export directory
- `data/logs/` - Pipeline log directory
- `docs/` - Documentation folder with UML and presentation

#### Modified Files
- None - this is a new CLI layer that interacts with existing database tables

### 🔧 Technical Implementation
- Raw SQL execution with persistent connection support
- Staging table validation before committing to real tables
- JSON validation for BOM components
- Dependency order enforcement (Products → BOMs → Order Items)
- Database-agnostic (works with PostgreSQL and other Django-supported databases)
- Logging with timestamps for all operations

### 📦 New Features in Detail

#### Import Process Flow
1. **Dry Run Validation** - Creates staging tables, validates data
2. **Diff Check** - Compares CSV with current database
3. **Validation** - Checks in dependency order, reports errors
4. **Confirmation** - Asks user to confirm before making changes
5. **Import** - Copies data from staging to real tables

#### CLI Menu Options
| Option | Description |
|--------|-------------|
| 1 | Test Database Connection |
| 2 | Generate CSV Templates (SEED) |
| 3 | Export Current Data to CSV |
| 4 | Import Data from CSV (Auto Dry Run + Import) |
| 5 | Show All Products |
| 6 | Show All BOMs |
| 7 | Show All Orders (Summary) |
| 8 | Show Single Order Detail |
| 9 | Show History Log (Newest First) |
| 10 | Error Prevention & Validation Tools |

### 📝 Testing Notes
- Run `python main.py` to launch interactive CLI
- Select option 2 to generate templates with sample data
- Place CSV files in `data/imports/` folder
- Run option 4 for dry run validation before import
- Check `data/logs/pipeline_errors.log` for operation history
- Import validates in dependency order and skips problematic rows

### 🎯 Summary
This release adds a powerful CLI import/export pipeline with safe staging table validation, field-level diff checking, and dependency-aware import. The interactive menu system makes BOM data management accessible via command line, with comprehensive error handling and logging.

---

## Release v1.3.0: Hybrid Dashboard with WebSocket + Polling

### 🆕 New Features
- **Real-Time WebSocket Updates** - Dashboard updates instantly when orders change
- **Automatic Polling Fallback** - 30-second interval if WebSocket is unavailable
- **Admin Dashboard** - Order statistics at a glance
- **Order Charts** - Daily/Weekly/Monthly order visualization
- **Status Distribution** - Visual breakdown of order statuses
- **Staff-Only Access** - Dashboard restricted to staff members
- **Connection Status Indicator** - Shows live/offline status

### 🔧 Technical Implementation
- Django Channels 4.0.0 for WebSocket support
- Daphne ASGI server for async handling
- Alpine.js for reactive frontend
- Hong Kong timezone support (Asia/Hong_Kong)
- InMemoryChannelLayer for development

---

## Release v1.2.0: User Profile, My Orders, Report Notes, and Admin Sidebar 🚀

### 🆕 New Features

#### User Profile
- **Profile Page** - Users can view and edit their profile information
- **Change Password** - Users can change their password from profile page
- **Email Display** - User email is displayed in profile

#### My Orders
- **Order History** - Users can view their own order history
- **Order Details** - Users can view detailed breakdown of each order

#### Report Notes
- **Order Notes** - Staff can add notes to orders
- **Note History** - View history of notes on each order

#### Admin Sidebar
- **Improved Navigation** - Sidebar for quick access to admin functions
- **Quick Actions** - Common admin tasks accessible from sidebar

### 🐛 Bug Fixes
- Fixed profile page email display
- Fixed password change redirect
- Fixed order history filtering by user

---

## Release v1.1.0: BOM CSV Pipeline with Import/Export

### 🆕 New Features

#### CSV Import/Export Pipeline
- **Product Import** - Import products from CSV with validation
- **BOM Import** - Import BOMs with component validation
- **Order Item Import** - Import order items with dependency checking
- **Export All Data** - Export Products, BOMs, and Order Items to CSV

#### Validation
- **Duplicate Detection** - Skips duplicate products and BOMs
- **Dependency Validation** - Ensures products exist before BOM import
- **BOM Existence Check** - Ensures BOMs exist before order item import

### 🔧 Technical Implementation
- Raw SQL execution with psycopg2
- Staging table validation
- JSON validation for BOM components
- Dependency order enforcement

---

## Release v1.0.0: Initial Release

### 🆕 New Features
- **BOM Management** - Create and manage Bills of Materials
- **Product Management** - Create and manage products
- **Order Management** - Create and manage orders
- **User Authentication** - Login/Register system
- **Admin Interface** - Django admin for data management

### 🔧 Technical Stack
- Django 4.x
- PostgreSQL
- Bootstrap 5
- Alpine.js


