# Path: usuarios/urls.py

from django.urls import path
from .views import (
    AlunoRegisterView, 
    ProfessorRegisterView, 
    RegistroSucessoView, 
    dashboard_aluno, 
    dashboard_professor, 
    CustomLoginView
)

urlpatterns = [
    # Cadastro de Aluno
    path('registro/', AlunoRegisterView.as_view(), name='registro'),
    path('registro/sucesso/', RegistroSucessoView.as_view(), name='registro_sucesso'),
    
    # Cadastro de Professor
    path('professor/registro/', ProfessorRegisterView.as_view(), name='registro_professor'),
    
    # Login e Dashboards
    path('login/', CustomLoginView.as_view(), name='login'),
    path('dashboard/', dashboard_aluno, name='dashboard'),
    path('professor/dashboard/', dashboard_professor, name='dashboard_professor'),
]