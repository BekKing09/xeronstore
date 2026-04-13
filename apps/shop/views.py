from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages 
from django.contrib.auth.decorators import login_required
from .models import Product, RedeemCode, Category
from apps.orders.models import Order
from django.db import transaction


def shop_page(request):
    categories = Category.objects.all()
    
    # Faqat tizimga kirganlar uchungina mahsulotlarni olamiz
    if request.user.is_authenticated:
        category_id = request.GET.get('category')
        if category_id:
            products = Product.objects.filter(category_id=category_id, is_active=True)
        else:
            products = Product.objects.filter(is_active=True)
    else:
        # Kirmaganlarga bo'sh ro'yxat yuboramiz
        products = Product.objects.none()

    return render(request, 'shop.html', {
        'categories': categories, 
        'products': products
    })

@login_required
def buy_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    user = request.user

    # 1. Balansni tekshirish
    if user.balance < product.price:
        messages.error(request, "Mablag' yetarli emas! Iltimos, balansni to'ldiring.")
        return redirect('shop')

    # 2. Bazadan bitta ishlatilmagan kodni olish
    code_to_sell = product.codes.filter(is_used=False).first()
    
    if not code_to_sell:
        messages.error(request, "Hozircha bu mahsulotdan qolmagan.")
        return redirect('shop')

    # Tranzaksiya: Pul ayirish va kodni berish bitta jarayonda bo'lishi shart
    with transaction.atomic():
        # 3. Foydalanuvchi balansidan pul ayirish
        user.balance -= product.price
        user.save()

        # 4. Kodni ishlatilgan deb belgilash va Order yaratish
        code_to_sell.is_used = True
        code_to_sell.save()

        Order.objects.create(
            user=user,
            product=product,
            redeem_code=code_to_sell,
            price_paid=product.price
        )

        messages.success(request, f"Xarid muvaffaqiyatli! Sizning kodingiz: {code_to_sell.code}")
    
    return redirect('shop')
def pay_view(request):
    return render(request, 'pay.html')