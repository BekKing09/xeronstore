from django.contrib.auth.models import AbstractUser, BaseUserManager # BaseUserManager qo'shildi
from django.db import models
from decimal import Decimal

# 1. Maxsus Manager yaratamiz
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email kiritilishi shart")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser is_staff=True bo\'lishi shart.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser is_superuser=True bo\'lishi shart.')

        return self.create_user(email, password, **extra_fields)

# 2. User modeli
class User(AbstractUser):
    username = None # Username o'chirilgan
    nickname = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Balans"
    )

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # Managerani modelga bog'laymiz
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Bu yer bo'sh bo'lishi kerak

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

### tranzaksiyalarni saqlash

class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ("DEPOSIT", "To'ldirish"),
        ("PURCHASE", "Xarid"),
        ("REFUND", "Qaytarish"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    description = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone_number} | {self.type} | {self.amount}"


### sms kod

class SMSCode(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        # Kod 2 daqiqa davomida amal qiladi
        from django.utils import timezone
        return (timezone.now() - self.created_at).seconds > 120

    class Meta:
        verbose_name = "SMS Kod"
        verbose_name_plural = "SMS Kodlar"