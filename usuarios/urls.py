# Path: usuarios/urls.py

from django.urls import path
from .views import (
    AlunoRegisterView, 
    RegistroSucessoView, 
    dashboard_aluno, 
    dashboard_professor, 
    CustomLoginView
)

urlpatterns = [
    path('registro/', AlunoRegisterView.as_view(), name='registro'),
    path('registro/sucesso/', RegistroSucessoView.as_view(), name='registro_sucesso'),
    # Usando a CustomLoginView que criaremos no views.py
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/', dashboard_aluno, name='dashboard'),
    path('professor/dashboard/', dashboard_professor, name='dashboard_professor'),
]