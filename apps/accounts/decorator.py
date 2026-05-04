from django.core.exceptions import PermissionDenied
from functools import wraps

def manager_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Faqat superuser yoki 'Manager' guruhidagi foydalanuvchilar kira oladi
        # is_staff bo'lishi shart emas!
        if request.user.is_authenticated and (request.user.is_superuser or request.user.groups.filter(name='Manager').exists()):
            return view_func(request, *args, **kwargs)
        raise PermissionDenied # Kirish taqiqlangan xatosini qaytaradi
    return _wrapped_view