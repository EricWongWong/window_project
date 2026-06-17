from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # ⭐ IMPORTANT: Include member URLs with /member/ prefix
    path('member/', include('member.urls')),  # ⭐ ADD THIS LINE

    # Booking app second (main site content)
    path('', include('booking.urls')),  # This gives you /services/, /booking/, etc.
    
    # Core app (if you have home, about, contact)
    path('', include('core.urls')),
    
    # Django built-in auth (optional, you may not need this)
    # path('accounts/', include('django.contrib.auth.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
