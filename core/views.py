from django.shortcuts import render

def home(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

# 🔥 【核心修復：立刻補上這 2 行】
def price(request):
    return render(request, 'price.html')

def services(request):
    return render(request, 'services.html') # 或者是你具体的功能模版

def window_schedule(request):
    return render(request, 'window_schedule.html') # 或者是你具体的功能模版


def booking(request):
    return render(request, 'booking.html') # 或者是你具体的功能模版

def cases(request):
    return render(request, 'cases.html') # 或者是你具体的功能模版

def knowledge(request):
    return render(request, 'knowledge.html') # 或者是你具体的功能模版