import random
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from decimal import Decimal
from django.utils import timezone

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
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None 
    nickname = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(unique=True)
    

    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name="Profil rasmi"
    )
    
    uid = models.CharField(
        max_length=7, 
        unique=True, 
        editable=False, 
        verbose_name="UID"
    )
    
    balance = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        default=Decimal('0.00'),
        verbose_name="Balans"
    )

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if not self.uid:
            while True:
                potential_uid = str(random.randint(7000000, 7999999))
                if not User.objects.filter(uid=potential_uid).exists():
                    self.uid = potential_uid
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.uid})"

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"


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
        # phone_number o'rniga email va uid ishlatiladi
        return f"{self.user.email} | {self.type} | {self.amount}"


class SMSCode(models.Model):
    phone_number = models.CharField(max_length=15)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        return (timezone.now() - self.created_at).seconds > 120

    class Meta:
        verbose_name = "SMS Kod"
        verbose_name_plural = "SMS Kodlar"