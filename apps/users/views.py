from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import User, SMSCode
from apps.orders.models import Order # Xaridlar tarixini olish uchun
from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import send_sms_code

# --- API qismi (Mavjud kodlar) ---
class SendOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        if not phone:
            return Response({"error": "Telefon raqami shart"}, status=400)
        send_sms_code(phone)
        return Response({"message": "Kod yuborildi"})

class VerifyOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        code = request.data.get('code')
        sms_record = SMSCode.objects.filter(phone_number=phone, code=code, is_used=False).last()
        
        if sms_record and not sms_record.is_expired():
            sms_record.is_used = True
            sms_record.save()
            user, created = User.objects.get_or_create(phone_number=phone)
            return Response({"message": "Muvaffaqiyatli", "is_new": created})
        return Response({"error": "Kod xato yoki muddati o'tgan"}, status=400)

# --- Template Views qismi ---

def home_page(request):
    return render(request, 'welcome.html')

@login_required
def profile_page(request):
    # Foydalanuvchining xaridlarini sanasi bo'yicha saralab olamiz
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'profile.html', context)

from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def set_nickname(request):
    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        if nickname:
            user = request.user
            user.nickname = nickname
            user.save()
            messages.success(request, f"Nickname muvaffaqiyatli o'rnatildi: {nickname}")
    return redirect('profile') # 'profile' o'rniga profilingizni url nomini yozing
