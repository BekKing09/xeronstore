"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from apps.users import views
from apps.users.views import home_page, profile_page
from django.conf.urls.static import static
from django.conf import settings
from apps.shop.views import shop_page, buy_product, pay_view







urlpatterns = [
    path('xeron-store-boss/', admin.site.urls),
    path('accounts/', include('allauth.urls')), 
    path('', home_page, name='home'), 
    path('shop/', shop_page, name='shop'),
    path('accounts/profile/', profile_page, name='profile'),
    path('buy/<int:product_id>/', buy_product, name='buy_product'),
    path('set-nickname/', views.set_nickname, name='set_nickname'),
    path('pay/', pay_view, name='pay'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
handler404 = 'core.views.custom_404'
