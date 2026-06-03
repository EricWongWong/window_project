from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # 🔥 【全新加入】配置價目表的網址，對接剛剛寫好的 views.price
    path('price/', views.price, name='price'),

    # 🔥 【精准修复】在这里加上缺失的 services 路由
    path('services/', views.services, name='services'), 
    path('window_schedule/', views.window_schedule, name='window_schedule'), 
    path('booking/', views.booking, name='booking'),
    path('cases/', views.cases, name='cases'),
    path('knowledge/', views.knowledge, name='knowledge'),
        # 🔥 【全新精準加入】1. 太古城案例網址（對接 /cases/taikoo-shing/）
    path('cases/taikoo-shing/', views.taikoo_shing, name='taikoo_shing'),
    
    # 🔥 【全新精準加入】2. 黃埔花園案例網址（對接 /cases/whampoa-garden/）
    path('cases/whampoa-garden/', views.whampoa_garden, name='whampoa_garden'),
    
    # 🔥 【全新精準加入】3. 麗港城案例網址（對接 /cases/laguna-city/）
    path('cases/laguna-city/', views.laguna_city, name='laguna_city'),
]
