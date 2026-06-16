from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Member app first (authentication)
    path('', include('member.urls')),  # This gives you /register/, /login/, /logout/
    
    # Booking app second (main site content)
    path('', include('booking.urls')),  # This gives you /services/, /booking/, etc.
    
    # Core app (if you have home, about, contact)
    path('', include('core.urls')),
    
    # Django built-in auth (optional, you may not need this)
    # path('accounts/', include('django.contrib.auth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
