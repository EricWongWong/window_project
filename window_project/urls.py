from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')), # Home, about, contact
    path('', include('booking.urls')),
    path('member/', include('member.urls')),
    # 4. 认证系统：直接引入 Django 内置的登录（Login）和登出（Logout）路由
    # 引入后，你无需手写登录逻辑，直接访问 /accounts/login/ 即可使用
    path('accounts/', include('django.contrib.auth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
