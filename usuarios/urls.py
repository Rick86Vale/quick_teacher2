# Path: usuarios/urls.py
from django.urls import path, include   
from . import views
from django.contrib.auth import views as auth_views 
from .views import (
    AlunoRegisterView, 
    ProfessorRegisterView, 
    RegistroSucessoView, 
    dashboard_aluno, 
    dashboard_professor, 
    CustomLoginView
)

urlpatterns = [
    # Rotas de Registro
    path('registro/', AlunoRegisterView.as_view(), name='registro'),
    path('registro/sucesso/', RegistroSucessoView.as_view(), name='registro_sucesso'),
    path('professor/registro/', ProfessorRegisterView.as_view(), name='registro_professor'),
    
    # Login e Logout - Usando a sua CustomLoginView
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboards
    path('dashboard/', dashboard_aluno, name='dashboard'),
    path('professor/dashboard/', dashboard_professor, name='dashboard_professor'),

    #Usuários
    path('', include('django.contrib.auth.urls')), # <--- ISSO adiciona 'password_change', 'login', 'logout', etc.
    path('perfil/', views.perfil_usuario, name='perfil_usuario'),
]
