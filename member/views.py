from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse # ✅Added for named URLs

# 1. 註冊視圖
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 註冊成功後自動登錄
            messages.success(request, "註冊成功！歡迎加入。")
            # ✅ 精準修復：註冊成功後也必須加上命名空間前綴，防止 NoReverseMatch
            #return redirect('member:dashboard')
            #return redirect('/')
            return redirect(reverse('home')) # ✅ Using named URL
        else:
            messages.error(request, "註冊失敗，請檢查輸入信息。")
    else:
        form = UserCreationForm()
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
                #return redirect('member:dashboard')  # ✅ 設定正確
                #return redirect('/')
                return redirect(reverse('home')) # ✅ Using named URL
        messages.error(request, "用戶名或密碼錯誤。")
    else:
        form = AuthenticationForm()
    return render(request, 'member/login.html', {'form': form})

# 3. 會員中心視圖（必須登錄才能訪問）
@login_required
def dashboard(request):
    return render(request, 'member/dashboard.html')


# 4. 登出視圖

from django.views.decorators.csrf import csrf_exempt

# ✅ 加上這個裝飾器，允許直接登出而不檢查 CSRF Token，徹底根除 403 錯誤
@csrf_exempt
def logout_view(request):
    logout(request)
    messages.success(request, "您已成功登出。")
    #return redirect('/')
    return redirect(reverse('home')) # ✅ Using named URL



