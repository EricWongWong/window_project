# CHANGELOG.md

# Release v1.3.1: WebSocket Real-Time + Login/Register Improvements 🚀

## 🆕 New Features

### WebSocket Real-Time Dashboard
- **Real-Time Updates** - Dashboard updates instantly when orders change
- **Signal Triggers** - Automatic updates triggered by order creation/update/deletion
- **Multiple Client Support** - Multiple staff members can view real-time updates
- **Automatic Reconnection** - WebSocket reconnects automatically with exponential backoff strategy
- **Connection Status Indicator** - Visual indicator showing live/offline status
- **Polling Fallback** - Automatic fallback to polling (30-second interval) if WebSocket is unavailable

### Login/Register Improvements
- **Email Field** - Users can now enter their email during registration
- **Profile Page** - Users can view and edit their profile information
- **Change Password** - Users can change their password from profile page
- **Always Visible Tabs** - Login/Register tabs are now always visible without hovering

## 🐛 Bug Fixes
- Email address is now properly saved when users register
- Profile page correctly displays user email
- Password change redirects to profile page instead of dashboard
- Registration shows detailed error messages instead of generic failures
- Fixed circular import issues in WebSocket implementation
- Fixed WebSocket consumer data handling

## 📁 Files Added/Changed

### New Files
- `member/signals.py` - Signal triggers for auto-updates
- `member/utils.py` - Dashboard data utilities
- `booking/templates/booking/profile.html` - Profile page
- `booking/templates/booking/change_password.html` - Password change page
- `test_signals.py` - Signal testing script

### Modified Files
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

## 🔧 Technical Implementation
- Django Channels for WebSocket support
- InMemoryChannelLayer for development (Redis ready for production)
- Signal-based auto-updates on order changes
- Alpine.js for reactive frontend and WebSocket handling
- Polling fallback every 30 seconds
- Real-time WebSocket updates when orders change

## 📦 Dependencies Added
```txt
channels==4.0.0
channels-redis==4.1.0
redis==5.0.1
daphne==4.0.0

📝 Testing Notes
Login as staff and open dashboard

WebSocket should connect automatically (connection indicator shows "Live")

Add/update an order in admin

Dashboard should update instantly without refresh

Multiple staff should see updates simultaneously

If WebSocket fails, polling will take over (30-second interval)

Register a new account - email should be saved

Login and go to profile - email should be visible

Edit profile - changes should save correctly

Change password - should redirect back to profile

Login/Register tabs should be visible at all times

🎯 Summary
This release combines real-time WebSocket updates with improved user authentication and profile management. Staff can now see instant order updates, while users benefit from a better registration and profile experience. The dashboard features a hybrid approach with WebSocket as primary and polling as fallback for reliability.