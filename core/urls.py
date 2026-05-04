
from django.contrib import admin
from django.urls import path, include
from apps.users import views
from apps.users.views import home_page, profile_page
from django.conf.urls.static import static
from django.conf import settings
from apps.shop.views import shop_page, buy_product, pay_view
from apps.payments.views import transactions_view
from django.contrib.auth import views as auth_views
from apps.accounts.views import delete_account_view, manager_panel, settings_view, get_user_info, profile_edit_view # verify_profile_edit_view




urlpatterns = [
    path('xeron-store-boss/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('', home_page, name='home'), 
    path('shop/', shop_page, name='shop'),
    path('accounts/profile/', profile_page, name='profile'),
    path('buy/<int:product_id>/', buy_product, name='buy_product'),
    path('set-nickname/', views.set_nickname, name='set_nickname'),
    path('pay/', pay_view, name='pay'),
    path('transactions/', transactions_view, name='transactions'),
    path('settings/', settings_view, name='settings'),
    
    # Parolni o'zgartirish va o'chirish
    path('accounts/password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html',
        success_url='/settings/' 
    ), name='password_change'),
    path('delete-account/', delete_account_view, name='delete_account'),
    path('accounts/profile/edit/', profile_edit_view, name='profile_edit'),
    
    # Manager Panel yo'nalishlari
    path('manager/', manager_panel, name='manager_panel'),
    path('manager/get-user-info/', get_user_info, name='get_user_info'),
    # path('accounts/profile/edit/verify/', verify_profile_edit_view, name='verify_profile_edit'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'core.views.custom_404'
