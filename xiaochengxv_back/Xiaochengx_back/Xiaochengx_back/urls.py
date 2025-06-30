"""
URL configuration for Xiaochengx_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path

from app01 import views
from app01.views import update_profile

from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('index/',views.index),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('send_code/', views.send_verification_code, name='send_code'),
    path('register/', views.register, name='register'),
    # path('update-profile/', update_profile, name='update_profile'),
    path('api/update-profile/', views.update_profile),
    path('api/update-avatar/', views.update_avatar, name='update_avatar'),
    path('api/update-nickname/', views.update_nickname, name='update_nickname'),
    path('api/get-user-info/', views.get_user_info, name='get_user_info'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# 添加媒体文件的访问路径
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
