from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Category, Product, RedeemCode

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_count', 'is_active']
    list_filter = ['category', 'is_active']

@admin.register(RedeemCode)
class RedeemCodeAdmin(admin.ModelAdmin):
    list_display = ['code', 'product', 'is_used', 'created_at']
    list_filter = ['is_used', 'product__category']