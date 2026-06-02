from django.db import models
from django.contrib.auth.models import User

SERVICE_CHOICES = (
    ('inspection', '強制驗窗'),
    ('repair', '鋁窗維修'),
    ('waterproof', '防水工程'),
)

STATUS_CHOICES = (
    ('pending', '待處理'),
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
