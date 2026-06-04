from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Order

def services(request):
    return render(request, 'booking/services.html')

def window_schedule(request):
    return render(request, 'booking/window_schedule.html')

def price(request):
    return render(request, 'booking/price.html')

def cases(request):
    return render(request, 'cases/case_list.html')

def knowledge(request):
    return render(request, 'booking/knowledge.html')

def booking(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        booking_date = request.POST.get('booking_date')
        service_type = request.POST.get('service_type')
        remark = request.POST.get('remark', '')

        if not all([name, phone, address, booking_date, service_type]):
            messages.error(request, '請填寫所有必要欄位')
            return render(request, 'booking.html')

        Order.objects.create(
            user=None,
            name=name,
            phone=phone,
            address=address,
            service_type=service_type,
            booking_date=booking_date,
            remark=remark,
            status='pending'
        )
        messages.success(request, '預約成功！我們會盡快與你聯絡。')
        return redirect('booking')
    return render(request, 'booking/booking.html')

# 太古城案例詳情頁
def taikoo_shing(request):
    return render(request, 'cases/taikoo-shing.html')

# 黃埔花園案例詳情頁
def whampoa_garden(request):    
    return render(request, 'cases/whampoa-garden.html')
# 麗港城案例詳情頁
def laguna_city(request):
    return render(request, 'cases/laguna-city.html')
