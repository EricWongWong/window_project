# member/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta  # ⭐ FIXED: Added datetime import
from django.contrib.auth.models import User
from booking.models import Order
import logging
from .utils import get_dashboard_data

logger = logging.getLogger(__name__)

# ============================================================
# AUTHENTICATION VIEWS
# ============================================================

# 1. 註冊視圖
def register_view(request):
    if request.method == 'POST':
        # ⭐ Get email from POST data
        email = request.POST.get('email')
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # ⭐ Create user but don't save yet
            user = form.save(commit=False)
            user.email = email  # ⭐ Save email
            user = form.save()
            login(request, user)
            messages.success(request, "註冊成功！歡迎加入。")
            # ⭐ KEEP: Redirect to home page
            return redirect(reverse('home'))
        else:
            # Show detailed error messages
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'username':
                        messages.error(request, f"用戶名問題: {error}")
                    elif field == 'password1':
                        messages.error(request, f"密碼問題: {error}")
                    elif field == 'password2':
                        messages.error(request, f"密碼確認問題: {error}")
                    else:
                        messages.error(request, error)
    else:
        form = UserCreationForm()
    # ⭐ KEEP: Use member/login.html
    return render(request, 'member/register.html', {'form': form})


# 2. 登錄視圖
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"歡迎回來，{username}！")
                # ⭐ KEEP: Redirect to home page
                return redirect(reverse('home'))
        messages.error(request, "用戶名或密碼錯誤。")
    else:
        form = AuthenticationForm()
    # ⭐ KEEP: Use member/login.html
    return render(request, 'member/login.html', {'form': form})


# 3. 登出視圖
@csrf_exempt
def logout_view(request):
    logout(request)
    messages.success(request, "您已成功登出。")
    # ⭐ KEEP: Redirect to home page
    return redirect(reverse('home'))


# ============================================================
# DASHBOARD VIEWS (Staff Only)
# ============================================================

# 4. 會員中心視圖（必須登錄才能訪問）
@login_required
def dashboard(request):
    """Main dashboard view - Staff only"""
    # ⭐ Only staff can access dashboard
    if not request.user.is_staff:
        messages.warning(request, '您沒有權限訪問管理儀表板。')
        return redirect('home')
    return render(request, 'member/dashboard.html')


@login_required
def get_dashboard_data(request):
    """
    API endpoint for polling fallback.
    Returns dashboard statistics as JSON.
    Staff only - checks user is staff.
    """
    # Only allow staff to access this data
    if not request.user.is_staff:
        return JsonResponse({
            'error': 'Access denied. Staff only.',
            'stats': {
                'total_members': 0,
                'total_orders': 0,
                'today_orders': 0,
                'this_week_orders': 0,
                'this_month_orders': 0,
            },
            'daily_orders': [],
            'weekly_orders': [],
            'monthly_orders': [],
            'status_counts': {},
            'recent_orders': [],
            'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }, status=403)
    
    try:
        today = timezone.now().date()
        
        # ============ TOTAL COUNTS ============
        total_members = User.objects.count()
        total_orders = Order.objects.count()
        
        # ============ TODAY'S ORDERS ============
        today_start = datetime.combine(today, datetime.min.time())
        today_start = timezone.make_aware(today_start) if not timezone.is_aware(today_start) else today_start
        today_end = datetime.combine(today, datetime.max.time())
        today_end = timezone.make_aware(today_end) if not timezone.is_aware(today_end) else today_end
        
        today_orders = Order.objects.filter(
            created_at__gte=today_start,
            created_at__lte=today_end
        ).count()
        
        # ============ THIS WEEK ORDERS (Last 7 days) ============
        week_ago = today - timedelta(days=7)
        week_start = datetime.combine(week_ago, datetime.min.time())
        week_start = timezone.make_aware(week_start) if not timezone.is_aware(week_start) else week_start
        this_week_orders = Order.objects.filter(
            created_at__gte=week_start
        ).count()
        
        # ============ THIS MONTH ORDERS ============
        month_start = datetime(today.year, today.month, 1)
        month_start = timezone.make_aware(month_start) if not timezone.is_aware(month_start) else month_start
        this_month_orders = Order.objects.filter(
            created_at__gte=month_start
        ).count()
        
        # ============ DAILY ORDER COUNT (Last 7 days) ============
        daily_orders = []
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_start = datetime.combine(date, datetime.min.time())
            date_start = timezone.make_aware(date_start) if not timezone.is_aware(date_start) else date_start
            date_end = datetime.combine(date, datetime.max.time())
            date_end = timezone.make_aware(date_end) if not timezone.is_aware(date_end) else date_end
            
            count = Order.objects.filter(
                created_at__gte=date_start,
                created_at__lte=date_end
            ).count()
            
            daily_orders.append({
                'date': date.strftime('%m/%d'),
                'count': count,
                'day': date.strftime('%A')[:3]
            })
        
        # ============ WEEKLY ORDER COUNT (Last 4 weeks) ============
        weekly_orders = []
        for i in range(3, -1, -1):
            week_start_date = today - timedelta(days=today.weekday() + (7 * i))
            week_end_date = week_start_date + timedelta(days=6)
            
            week_start_datetime = datetime.combine(week_start_date, datetime.min.time())
            week_start_datetime = timezone.make_aware(week_start_datetime) if not timezone.is_aware(week_start_datetime) else week_start_datetime
            week_end_datetime = datetime.combine(week_end_date, datetime.max.time())
            week_end_datetime = timezone.make_aware(week_end_datetime) if not timezone.is_aware(week_end_datetime) else week_end_datetime
            
            count = Order.objects.filter(
                created_at__gte=week_start_datetime,
                created_at__lte=week_end_datetime
            ).count()
            
            # ⭐ Better week labels
            week_number = (today - week_start_date).days // 7 + 1
            if week_number == 1:
                week_label = "本週"
            elif week_number == 2:
                week_label = "上週"
            else:
                week_label = f"{week_number}週前"
            
            weekly_orders.append({
                'week': week_label,
                'date_range': f"{week_start_date.strftime('%m/%d')} - {week_end_date.strftime('%m/%d')}",
                'count': count
            })
        
        # ============ MONTHLY ORDER COUNT (Last 6 months) ============
        monthly_orders = []
        for i in range(5, -1, -1):
            month = today.month - i
            year = today.year
            
            if month <= 0:
                month += 12
                year -= 1
            
            month_start = datetime(year, month, 1)
            month_start = timezone.make_aware(month_start) if not timezone.is_aware(month_start) else month_start
            
            if month == 12:
                month_end = datetime(year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = datetime(year, month + 1, 1) - timedelta(days=1)
            month_end = timezone.make_aware(month_end) if not timezone.is_aware(month_end) else month_end
            
            count = Order.objects.filter(
                created_at__gte=month_start,
                created_at__lte=month_end
            ).count()
            
            monthly_orders.append({
                'month': month_start.strftime('%Y-%m'),
                'month_name': month_start.strftime('%b %Y'),
                'count': count
            })
        
        # ============ STATUS DISTRIBUTION ============
        status_counts = {
            'pending': Order.objects.filter(status='pending').count(),
            'confirmed': Order.objects.filter(status='confirmed').count(),
            'in_progress': Order.objects.filter(status='in_progress').count(),
            'completed': Order.objects.filter(status='completed').count(),
            'cancelled': Order.objects.filter(status='cancelled').count(),
        }
        
        # ============ RECENT ORDERS (Last 10) ============
        recent_orders = []
        recent_orders_query = Order.objects.order_by('-created_at')[:10]
        
        for order in recent_orders_query:
            recent_orders.append({
                'id': order.id,
                'customer': order.name if order.name else 'N/A',
                'phone': order.phone if order.phone else 'N/A',
                'service_type': order.service_type if order.service_type else 'N/A',
                'booking_date': order.booking_date.strftime('%Y-%m-%d') if order.booking_date else '',
                'status': order.status if order.status else 'pending',
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M') if order.created_at else '',
            })
        
        data = {
            'stats': {
                'total_members': total_members,
                'total_orders': total_orders,
                'today_orders': today_orders,
                'this_week_orders': this_week_orders,
                'this_month_orders': this_month_orders,
            },
            'daily_orders': daily_orders,
            'weekly_orders': weekly_orders,
            'monthly_orders': monthly_orders,
            'status_counts': status_counts,
            'recent_orders': recent_orders,
            'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Dashboard API error: {str(e)}")
        
        return JsonResponse({
            'error': str(e),
            'stats': {
                'total_members': 0,
                'total_orders': 0,
                'today_orders': 0,
                'this_week_orders': 0,
                'this_month_orders': 0,
            },
            'daily_orders': [],
            'weekly_orders': [],
            'monthly_orders': [],
            'status_counts': {},
            'recent_orders': [],
            'last_updated': timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        }, status=500)
    
@login_required
def dashboard_api(request):  # ⭐ Renamed from get_dashboard_data
    """API endpoint for polling fallback"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    try:
        # ⭐ Use the utility function
        data = get_dashboard_data()
        return JsonResponse(data)
    except Exception as e:
        logger.error(f"Dashboard API error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
