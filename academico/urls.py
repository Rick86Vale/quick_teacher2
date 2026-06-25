# Path: academico/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Index
    path('', views.index, name='index'),
    
    # Instituições (CRUD Completo)
    path('instituicoes/', views.listar_instituicoes, name='listar_instituicoes'),
    path('instituicao/nova/', views.criar_instituicao, name='criar_instituicao'),
    path('instituicao/editar/<int:pk>/', views.editar_instituicao, name='editar_instituicao'),
    path('instituicao/excluir/<int:pk>/', views.excluir_instituicao, name='excluir_instituicao'),
    
    # Turmas
    path('turmas/', views.listar_turmas, name='listar_turmas'),
    path('turmas/nova/', views.criar_turma, name='criar_turma'),
    path('turma/editar/<int:pk>/', views.editar_turma, name='editar_turma'),
    path('turma/excluir/<int:pk>/', views.excluir_turma, name='excluir_turma'),
    path('turma/<int:pk>/', views.detalhes_turma, name='detalhes_turma'),
    
    # Disciplinas (CRUD)
    path('minhas-disciplinas/', views.listar_disciplinas, name='listar_disciplinas'),
    path('disciplina/nova/', views.criar_disciplina, name='criar_disciplina'),
    path('disciplina/editar/<int:pk>/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplina/excluir/<int:pk>/', views.excluir_disciplina, name='excluir_disciplina'),

    # Aulas
    path('disciplina/<int:disciplina_id>/aulas/', views.gerenciar_aulas, name='gerenciar_aulas'),
]