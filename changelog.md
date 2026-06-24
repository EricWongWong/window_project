# CHANGELOG.md

## Release v1.3.2: Documentation Updates & Merge 🚀

### 📝 Documentation Updates
- **README.md** - Updated with PDF links and project documentation
- **Installation Guide** - Added comprehensive setup instructions
- **UML Diagrams** - Fixed rendering issues for GitHub viewing
- **File Organization** - Moved and reorganized markdown files

### 🔧 Technical Changes
- Merge: Complete merge of feature branches
- Dashboard: Clean layout with pie chart and bar charts

### 📁 Files Changed
- `README.md` - Updated with PDF documentation
- `installation.md` - Added installation guide
- `uml.md` - Fixed diagram rendering for GitHub
- Various markdown files reorganized

---

## Release v1.3.1: Installation Guide & Login/Register Enhancements 🚀

### 🆕 New Features
- **Installation Guide** - Comprehensive setup documentation added
- **Login/Register Fine-Tuning** - Improved user authentication flow

### 🐛 Bug Fixes
- Fixed registration and login functions
- Improved user experience during authentication
- Updated project documentation

### 📁 Files Added
- `installation.md` - Complete installation guide
- Project PDF with student information

### 🔧 Technical Implementation
- Signal integration for WebSocket auto-updates
- WebSocket auto-update dashboard functionality

---

## Release v1.3.0: Staff Dashboard with WebSocket + Polling 🚀

### 🆕 New Features
- **Staff-Only Dashboard** - Dedicated dashboard for staff members
- **WebSocket Real-Time Updates** - Instant updates when orders change
- **Polling Fallback** - Automatic fallback to polling (30-second interval)
- **Order Statistics** - Daily/Weekly/Monthly order visualization
- **Status Distribution** - Visual breakdown of order statuses
- **Connection Status Indicator** - Shows live/offline status

### 📁 Files Added
- Dashboard templates for staff
- WebSocket consumer implementation
- Polling fallback mechanism

### 🔧 Technical Implementation
- Django Channels for WebSocket support
- Alpine.js for reactive frontend
- InMemoryChannelLayer for development
- Hong Kong timezone support

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
- Updated `.gitignore` to exclude cache and runtime files

### 📁 Files Changed
- `main.py` - Moved from root to `scripts/` folder
- `.gitignore` - Updated to exclude `__pycache__` and `.pyc` files
- Various model updates

---

## Release v1.1.0: BOM CSV Pipeline with Import/Export 🚀

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

### 📁 Files Added
- `main.py` - Interactive CLI menu system
- Import/export utilities
- CSV template generation

---

## Release v1.0.0: Initial Stable Release 🎉

### 🆕 New Features
- **BOM Management** - Create and manage Bills of Materials
- **Product Management** - Create and manage products
- **Order Management** - Create and manage orders
- **User Authentication** - Login/Register system with email support
- **Admin Interface** - Django admin for data management
- **Carousel** - Home page carousel added
- **Password Management** - Password stored securely using dotenv

### 🐛 Bug Fixes
- Fixed routing issues
- Fixed login redirect (now goes to home page instead of dashboard)
- Fixed burger menu
- Fixed endpoints for register, login, logout

### 🔧 Technical Implementation
- Django 4.x
- PostgreSQL
- Bootstrap 5
- Environment variables (.env) for sensitive data

### 📁 Files Added
- Core models (ProductMaster, ProductBOM, Order, OrderItem)
- Authentication endpoints
- Home page with carousel
- Environment configuration

---

## Release v0.9.0: Beta Release

### 🆕 New Features
- **Core Models** - ProductMaster, ProductBOM, Order, OrderItem
- **Basic CRUD** - Create, Read, Update, Delete operations
- **User Registration** - Basic registration system
- **User Login** - Basic login system
- **Admin Panel** - Django admin interface

### 🐛 Known Issues
- No real-time updates
- No CSV import/export
- Limited user profile features

---

## Release v0.8.0: Alpha Release

### 🆕 New Features
- **Initial Project Setup** - Django project initialization
- **Database Models** - Initial database schema design
- **Basic Templates** - Base HTML templates
- **URL Routing** - Basic URL structure
- **Static Files** - CSS and JavaScript setup

### 🛠️ Development Setup
- Python 3.9+
- Django 3.2+
- PostgreSQL
- Virtual Environment (venv)

---

## Pre-v0.8.0: Project Initiation

### 📁 Initial Commits
- `c755884` - Initial commit of window_project
- Project structure created
- Basic Django setup completed