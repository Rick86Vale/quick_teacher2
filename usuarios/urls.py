# Path: usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # <--- Importe isto
from .views import (
    AlunoRegisterView, 
    ProfessorRegisterView, 
    RegistroSucessoView, 
    dashboard_aluno, 
    dashboard_professor, 
    CustomLoginView
)

urlpatterns = [
    path('registro/', AlunoRegisterView.as_view(), name='registro'),
    path('registro/sucesso/', RegistroSucessoView.as_view(), name='registro_sucesso'),
    path('professor/registro/', ProfessorRegisterView.as_view(), name='registro_professor'),
    
    # Login e LOGOUT
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'), # <--- Adicione esta linha
    
    path('dashboard/', dashboard_aluno, name='dashboard'),
    path('professor/dashboard/', dashboard_professor, name='dashboard_professor'),
]