# Installation Guide - Window Project 🪟

## 📋 System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **PostgreSQL**: 12 or higher
- **Redis**: 6.0 or higher (optional, for production)
- **Node.js**: 16.0 or higher (optional, for asset compilation)
- **Git**: 2.0 or higher

### Recommended
- **Python**: 3.10.20
- **PostgreSQL**: 15
- **Redis**: 7.0
- **Ubuntu 22.04** / **Windows 11** / **macOS Ventura**

---

## 🚀 Quick Installation

### 1. Clone the Repository

```bash
# Clone the project
git clone https://github.com/EricWongWong/window_project.git
cd window_project

# Checkout the latest version
git checkout v1.3.1

2. Create Virtual Environment
Linux/macOS:

bash
python3 -m venv venv
source venv/bin/activate
Windows:

bash
python -m venv venv
venv\Scripts\activate

3. Install Dependencies
bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt

4. Configure Environment Variables
Create a .env file in the project root:

bash
# Create .env file
touch .env
Add the following variables:

env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# Database Settings
DB_NAME=window_db
DB_USER=postgres
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis Settings (Optional - for production WebSocket)
REDIS_URL=redis://localhost:6379/0

5. Setup Database
bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE window_db;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE window_db TO your_user;
\q

# Or use PostgreSQL with Windows:
# Open pgAdmin and create database manually

6. Run Migrations
bash
# Apply database migrations
python manage.py makemigrations
python manage.py migrate
7. Create Superuser
bash
# Create admin account
python manage.py createsuperuser
# Follow the prompts to set username, email, and password
8. Collect Static Files
bash
# Collect all static files
python manage.py collectstatic
9. Run Development Server
Option A: Using Django's Development Server (Basic)

bash
python manage.py runserver
Option B: Using Daphne (Recommended - with WebSocket)

bash
# Start Daphne server with WebSocket support
daphne -b 127.0.0.1 -p 8000 window_project.asgi:application
10. Access the Application
Homepage: http://localhost:8000/

Admin Panel: http://localhost:8000/admin/

Dashboard: http://localhost:8000/member/dashboard/ (staff only)

Login: http://localhost:8000/member/login/

Register: http://localhost:8000/member/register/

🔧 Advanced Configuration
Production Setup
1. Update .env for Production
env
# Django Settings
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database Settings
DB_NAME=window_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Redis Settings (Required for production WebSocket)
REDIS_URL=redis://localhost:6379/0
2. Configure ASGI Server
bash
# Install Daphne globally or in virtual environment
pip install daphne

# Run with multiple workers
daphne -b 0.0.0.0 -p 8000 -w 4 window_project.asgi:application
3. Using Gunicorn + Daphne
bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -k uvicorn.workers.UvicornWorker window_project.asgi:application
4. Nginx Configuration (Optional)
nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /static/ {
        alias /path/to/window_project/staticfiles/;
    }

    location /media/ {
        alias /path/to/window_project/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}

📦 Dependencies
Core Dependencies
txt
# Django and Web Framework
Django==5.2.14
django-widget-tweaks==1.5.0
django-taggit==6.1.0
django-humanize==0.1.2

# Database
psycopg2-binary==2.9.10

# WebSocket (Channels)
channels==4.0.0
channels-redis==4.1.0
redis==5.0.1
daphne==4.0.0

# Environment Variables
python-dotenv==1.0.0

# Utilities
python-magic==0.4.27

# Authentication
django-allauth==0.60.0  # Optional
Development Dependencies
txt
# Development
pytest==7.4.4
pytest-django==4.8.0
black==23.12.1
flake8==7.0.0
pre-commit==3.6.0
Frontend Dependencies
txt
# Alpine.js
alpinejs==3.14.3

# Bootstrap
bootstrap==5.3.2

# Font Awesome
font-awesome==6.5.1
🧪 Running Tests
bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test member
python manage.py test booking

# Run with coverage
pip install coverage
coverage run manage.py test
coverage report



