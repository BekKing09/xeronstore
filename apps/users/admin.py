from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    # 1. Ro'yxatda nimalar ko'rinishi
    list_display = ('email', 'balance', 'is_staff', 'is_active')
    
    # 2. Qidiruvda faqat email ishlatilsin (username emas!)
    search_fields = ('email', 'nickname')
    
    # 3. Filtrlash
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    # 4. Saralash
    ordering = ('email',)

    # 5. Tahrirlash sahifasi (Barcha maydonlarni o'zingizning modelingizga mosladik)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Shaxsiy ma\'lumotlar', {'fields': ('nickname', 'balance', 'is_verified')}),
        ('Huquqlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
    )

    # 6. Yangi foydalanuvchi qo'shish sahifasi
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password', 'balance'),
        }),
    )

    # 7. MUHIM: filter_horizontal ichida username'ni qidiradigan standartlarni o'chiramiz
    filter_horizontal = ('groups', 'user_permissions')

    # 8. UserAdmin ichidagi "username"ga bog'liq qismlarni tozalaymiz
    # Bu qism xatolikni butunlay yo'q qiladi
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Standart UserAdmin username talab qilmasligi uchun uni None qilamiz
        self.username_field = 'email'
    class Media:
        css = {
            'all': ('css/style.css',)
        }