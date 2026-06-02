from django.contrib import admin
from .models import Order, Report

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id','name','phone','service_type','booking_date','status')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id','order','qp_name','is_safe')
