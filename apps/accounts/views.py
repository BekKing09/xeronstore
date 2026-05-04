from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from apps.accounts.decorator import manager_required
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.users.models import Transaction
from decimal import Decimal
from django.http import JsonResponse
from .forms import ProfileEditForm

User = get_user_model()

@login_required
def settings_view(request):
    """
    Foydalanuvchi sozlamalari sahifasi
    """
    return render(request, 'settings.html')


@login_required
def delete_account_view(request):
    if request.method == "POST":
        user = request.user
        user.delete() 
        messages.success(request, "Hisobingiz muvaffaqiyatli o'chirildi.")
        return redirect('home')
    return redirect('settings')


@login_required
@manager_required
def manager_panel(request):
    users = User.objects.all().order_by('-id')
    
    if request.method == "POST" and request.POST.get('action') == 'add_balance':
        target_uid = request.POST.get('uid')
        amount_str = request.POST.get('amount')
        security_pass = request.POST.get('security_password')
        description = request.POST.get('description', "Admin tomonidan to'ldirildi")
        
        # Xavfsizlik parolini tekshirish
        if security_pass != "xeron_security_balance_plus":
            messages.error(request, "Xavfsizlik paroli noto'g'ri!")
            return redirect('manager_panel')
            
        try:
            # Decimal formatiga o'tkazish
            amount = Decimal(amount_str)
            target_user = get_object_or_404(User, uid=target_uid)
            
            with transaction.atomic():
                target_user.balance += amount
                target_user.save()

                Transaction.objects.create(
                    user=target_user,
                    amount=amount,
                    type="DEPOSIT",
                    description=description
                )
            
            messages.success(request, f"Muvaffaqiyatli! {target_user.email} balansiga {amount} so'm qo'shildi.")
        except ValueError:
            messages.error(request, "Summa yoki UID xato formatda kiritilgan.")
        except User.DoesNotExist:
            messages.error(request, "Bunday UIDga ega foydalanuvchi topilmadi.")
        except Exception as e:
            messages.error(request, f"Xatolik yuz berdi: {str(e)}")
            
        return redirect('manager_panel')

    return render(request, 'manager/dashboard.html', {'users': users})


@login_required
@manager_required
def get_user_info(request):
    uid = request.GET.get('uid')
    if uid:
        try:
            target_user = User.objects.get(uid=uid)
            return JsonResponse({
                'success': True,
                'username': target_user.email,  # Username o'rniga email ishlatiladi
                'nickname': target_user.nickname or "Kiritilmagan",
                'balance': float(target_user.balance)
            })
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'message': "Foydalanuvchi topilmadi"})
    return JsonResponse({'success': False, 'message': "UID kiritilmadi"})


@login_required
def profile_edit_view(request):
    """
    Foydalanuvchi ma'lumotlarini tahrirlash (Rasm va Nickname)
    """
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profilingiz muvaffaqiyatli yangilandi.")
            return redirect('profile') # 'profile' sahifasiga qaytaradi
    else:
        form = ProfileEditForm(instance=request.user)
        
    context = {
        'form': form
    }
    return render(request, 'account/profile_edit.html', context)