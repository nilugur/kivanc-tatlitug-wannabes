"""
URL configuration for mysite project.

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
from django.views.generic.base import RedirectView
from tracker import views

urlpatterns = [
    # Kök URL'e (localhost:8000/) gelen ziyaretçiyi otomatik olarak
    # /tracker/'a yönlendiriyoruz. RedirectView, Django'nun hazır
    # sunduğu bir "sınıf tabanlı view" — kendi view fonksiyonumuzu
    # yazmamıza gerek kalmadan, sadece "nereye" (pattern_name) diyerek
    # yönlendirme yapmamızı sağlıyor. .as_view() ise bu sınıfı, path()'in
    # beklediği çağrılabilir bir fonksiyona çeviriyor.
    path('', RedirectView.as_view(pattern_name="tracker:index")),
    path('admin/', admin.site.urls),
    path('tracker/', include('tracker.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', views.register_choice, name="register_choice"),
    path('accounts/register/clients/', views.register_client, name="register_client"),
    path('accounts/register/dietitian/', views.register_dietitian, name="register_dietitian"),
    ]
