from django.urls import path
from . import views

urlpatterns = [
    # ✅ 新增三個案例詳情頁路由 (Detail route)
    path('cases/taikoo-shing/', views.taikoo_shing, name='taikoo_shing'),
    path('cases/whampoa-garden/', views.whampoa_garden, name='whampoa_garden'),
    path('cases/laguna-city/', views.laguna_city, name='laguna_city'),
    # ✅ General routes LAST
    path('services/', views.services, name='services'),
    path('window-schedule/', views.window_schedule, name='window_schedule'),
    path('price/', views.price, name='price'),
    path('cases/', views.cases, name='cases'),
    path('booking/', views.booking, name='booking'),
    path('knowledge/', views.knowledge, name='knowledge'),    
    # Profile & password
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password, name='change_password'),


    # My Orders & report note
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order/<int:order_id>/', views.order_detail_with_report, name='order_detail_with_report'),


]
