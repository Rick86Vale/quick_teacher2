# core/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('usuarios.urls')),
    path('academico/', include('academico.urls')),
    
    # Nova inclusão das URLs do app indicadores
    path('indicadores/', include('indicadores.urls')),
]