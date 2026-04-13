from django.db import models

# Create your models here.
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    image = models.ImageField(upload_to='categories/', verbose_name="O'yin rasmi")
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=200, verbose_name="Mahsulot nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narxi")
    image = models.ImageField(upload_to='products/', verbose_name="Mahsulot rasmi")
    is_active = models.BooleanField(default=True, verbose_name="Sotuvda bormi?")

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    @property
    def stock_count(self):
        # Omborimizda nechta ishlatilmagan kod borligini hisoblaydi
        return self.codes.filter(is_used=False).count()

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

class RedeemCode(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='codes')
    code = models.CharField(max_length=100, unique=True, verbose_name="Redeem Kod")
    is_used = models.BooleanField(default=False, verbose_name="Ishlatildimi?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.code}"

    class Meta:
        verbose_name = "Redeem Kod"
        verbose_name_plural = "Redeem Kodlar"