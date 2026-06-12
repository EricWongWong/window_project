from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .models import Order, Report

# ---------- Profile & Password ----------
@login_required
def profile_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '').strip()
        user.last_name = request.POST.get('last_name', '').strip()
        user.email = request.POST.get('email', '').strip()
        user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    return render(request, 'booking/profile.html', {'user': request.user})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'booking/change_password.html', {'form': form})

# ---------- My Orders & Report Note ----------
@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'booking/my_orders.html', {'orders': orders})

@login_required
def order_detail_with_report(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    report = getattr(order, 'report', None)   # one-to-one may not exist
    if request.method == 'POST' and report:
        # Only allow updating the customer_note
        report.customer_note = request.POST.get('customer_note', '')
        report.save()
        messages.success(request, 'Your note has been saved.')
        return redirect('order_detail_with_report', order_id=order.id)
    return render(request, 'booking/order_detail_with_report.html', {
        'order': order,
        'report': report,
    })

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
