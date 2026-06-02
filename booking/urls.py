from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.services, name='services'),
    path('window-schedule/', views.window_schedule, name='window_schedule'),
    path('price/', views.price, name='price'),
    path('cases/', views.cases, name='cases'),
    path('booking/', views.booking, name='booking'),
    path('knowledge/', views.knowledge, name='knowledge'),
]
