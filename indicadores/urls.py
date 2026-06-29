# indicadores/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.dashboard_indicadores, name='dashboard_indicadores'),
]