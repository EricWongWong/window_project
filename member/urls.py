from django.urls import path
from . import views

# 如果你之前設置了 app_name，請保留這行（這就是為什麼之前需要使用 member:dashboard 的原因）
app_name = 'member' 

urlpatterns = [
    # 1. 指向正確的 views 函數名
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # 2. 會員中心路由
    path('dashboard/', views.dashboard, name='dashboard'),
]
