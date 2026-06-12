from django.contrib import admin
#from .models import Order, Report
from .models import Order, Report, ProductMaster, ProductBOM, OrderItem   # ← Updated import line

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'phone', 'service_type', 'booking_date', 'status', 'created_at')
    list_filter = ('service_type', 'status')
    search_fields = ('name', 'phone', 'address')
    list_editable = ('status',)
    raw_id_fields = ('user',)
    date_hierarchy = 'booking_date'

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'qp_name', 'is_safe')
    list_filter = ('is_safe',)
    search_fields = ('qp_name', 'result')
    raw_id_fields = ('order',)

# Add at the bottom of admin.py

@admin.register(ProductMaster)
class ProductMasterAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'unit_price')
    list_display_links = ('id', 'product_name')
    search_fields = ('product_name',)
    list_editable = ('unit_price',)
    ordering = ('product_name',)

@admin.register(ProductBOM)
class ProductBOMAdmin(admin.ModelAdmin):
    list_display = ('id', 'bom_name', 'components_preview')
    search_fields = ('bom_name',)
    def components_preview(self, obj):
        """Show preview of components in list view"""
        import json
        if isinstance(obj.components, list):
            return f"{len(obj.components)} items"
        return "View details"
    components_preview.short_description = 'Components'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'order_description', 'bom', 'order_qty')
    list_filter = ('bom',)
    search_fields = ('order_description',)
    raw_id_fields = ('order', 'bom')
    
    def save_model(self, request, obj, form, change):
        # Auto-fill order_description from Order.name if order is set
        if obj.order and not obj.order_description:
            obj.order_description = obj.order.name
        super().save_model(request, obj, form, change)

