# Path: academico/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('minhas-disciplinas/', views.listar_disciplinas, name='listar_disciplinas'),
    path('disciplina/<int:disciplina_id>/aulas/', views.gerenciar_aulas, name='gerenciar_aulas'),
    # Novas rotas de Turmas
    path('turmas/', views.listar_turmas, name='listar_turmas'),
    path('turmas/nova/', views.criar_turma, name='criar_turma'),
    path('disciplina/<int:disciplina_id>/aulas/', views.gerenciar_aulas, name='gerenciar_aulas'),
]
    

