import requests
import random
from django.core.cache import cache

def send_sms_code(phone_number):
    # 1. Kod yaratish
    code = str(random.randint(100000, 999999))
    
    # 2. Rate Limiting (Bir raqamga har 2 minutda faqat 1ta kod)
    cache_key = f"sms_limit_{phone_number}"
    if cache.get(cache_key):
        return False, "Iltimos, biroz kutib qaytadan urining."

    # 3. Eskiz API orqali yuborish (Sodda ko'rinishi)
    # Haqiqiy loyihada bu yerda requests.post bo'ladi
    print(f"ESKIZ: {phone_number} raqamiga kod ketdi: {code}")
    
    # 4. Limitni o'rnatish (120 soniya)
    cache.set(cache_key, True, 120)
    
    # 5. Bazaga saqlash
    from .models import SMSCode
    SMSCode.objects.create(phone_number=phone_number, code=code)
    
    return True, "Kod yuborildi"