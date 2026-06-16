from django.db import models
from django.contrib.auth.models import User

SERVICE_CHOICES = (
    ('inspection', '強制驗窗'),
    ('repair', '鋁窗維修'),
    ('waterproof', '防水工程'),
)

STATUS_CHOICES = (
    ('pending', '待處理'),
    ('cancelled', '取消'),
    ('completed', '已完成'),
)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    booking_date = models.DateField()
    remark = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Report(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    qp_name = models.CharField(max_length=50)
    result = models.TextField()
    is_safe = models.BooleanField(default=False)
    customer_note = models.TextField(blank=True, null=True)   # ← new line
    
    def __str__(self):
        return f"Report for Order {self.order.id}"

# ============================================================
# NEW BOM MODELS (Add these at the bottom)
# ============================================================

class ProductMaster(models.Model):
    """Basic parts / raw materials for BOM components"""
    product_name = models.CharField(max_length=200, unique=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product_name} - ${self.unit_price}"

    class Meta:
        verbose_name = "Product Master"
        verbose_name_plural = "Product Masters"


class ProductBOM(models.Model):
    """
    Bill of Materials - service packages/recipes
    Components use product_name (not ID) for human readability
    """
    bom_name = models.CharField(max_length=200, unique=True)
    components = models.JSONField(
        help_text='JSON format: [{"product_name": "3-inch stainless hinge", "qty": 2}, {"product_name": "Stainless steel rivet", "qty": 8}]'
    )

    def __str__(self):
        return self.bom_name

    class Meta:
        verbose_name = "Product BOM"
        verbose_name_plural = "Product BOMs"


class OrderItem(models.Model):
    """
    Links orders to BOMs - tracks which BOM kits are used per order
    
    Note: order_id is optional (can be linked to existing Order later)
    order_description is required for identifying the order
    """
    # Optional foreign key to existing Order (can be null)
    order = models.ForeignKey(
        'Order', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    
    # Required description for the order
    order_description = models.CharField(
        max_length=200, 
        blank=True,
        help_text="Auto fill from orders name or you can manual edit such as Customer: John Doe, Date: 2024-01-15"
    )
    
    # BOM reference (required)
    bom = models.ForeignKey(ProductBOM, on_delete=models.PROTECT)
    
    # Quantity
    order_qty = models.PositiveIntegerField(default=1)
    

    def __str__(self):
        if self.order:
            return f"Order {self.order.id} - {self.bom.bom_name} x{self.order_qty}"
        else:
            return f"{self.order_description[:50]} - {self.bom.bom_name} x{self.order_qty}"
        
    def save(self, *args, **kwargs):
        # Auto-fill order_description from Order.name if order is set
        if self.order and not self.order_description:
            self.order_description = self.order.name
        super().save(*args, **kwargs)



    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"