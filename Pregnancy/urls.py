"""Pregnancy URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from Main import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index', ),
    path('login/', views.login, name='login', ),
    path('logout/', views.logout, name='logout', ),
    path('user/list', views.user_list, name='userlist', ),
    path('logs/list', views.logs_list, name='logslist', ),
    path('export/', views.xml_export, name='export', ),
    path('card/<int:card_id>/show', views.card_show, name='card', ),
    path('card/<int:card_id>/download', views.xml_download, name='download', ),
    path('card/<int:card_id>/print', views.card_print, name='print', ),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
