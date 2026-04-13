from django.db import models

# Create your models here.
from django.db import models
from apps.users.models import User
from apps.shop.models import Product, RedeemCode

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    redeem_code = models.OneToOneField(RedeemCode, on_delete=models.PROTECT)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.product.name}"