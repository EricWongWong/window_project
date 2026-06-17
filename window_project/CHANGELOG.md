# CHANGELOG.md

## [v1.3.0] - 2026-06-17

### Added
- Hybrid Dashboard with real-time WebSocket updates
- Automatic fallback to polling when WebSocket is unavailable
- Connection status indicator with live/offline status
- Auto-reconnect with exponential backoff strategy
- Dashboard statistics cards for key metrics
- Recent orders table in dashboard
- API endpoint for polling fallback (`/member/api/dashboard-data/`)
- Django Channels support for WebSocket
- Alpine.js for reactive frontend

### Changed
- Updated ASGI configuration for WebSocket support
- Added Channels to INSTALLED_APPS
- Added `app_name = 'member'` to member URLs for namespace
- Updated settings.py with channel layers configuration
- Updated base.html with dashboard navigation link

### Dependencies Added
- channels==4.0.0
- channels-redis==4.1.0
- redis==5.0.1
- daphne==4.0.0