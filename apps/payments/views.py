from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from apps.users.models import Transaction

@login_required
def transactions_view(request):
    # Foydalanuvchiga tegishli barcha tranzaksiyalar
    transactions = Transaction.objects.filter(user=request.user).order_by('-timestamp')
    
    # Kirimlar summasi (miqdori 0 dan katta bo'lganlar)
    total_income = transactions.filter(amount__gt=0).aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Chiqimlar summasi (miqdori 0 dan kichik bo'lganlar)
    # abs() funksiyasi manfiy sonni musbat qilib ko'rsatadi (-5000 -> 5000)
    total_expense = transactions.filter(amount__lt=0).aggregate(Sum('amount'))['amount__sum'] or 0
    
    context = {
        'transactions': transactions,
        'total_income': total_income,
        'total_expense': abs(total_expense),
    }
    
    return render(request, 'transactions.html', context)