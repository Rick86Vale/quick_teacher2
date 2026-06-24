# Path: core/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('academico.urls')),
    # 1. Incluindo as rotas de usuários
    path('usuarios/', include('usuarios.urls')), 
]