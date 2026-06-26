# academico/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # 0. Index
    path('', views.index, name='index'),

    # 1. Administrador (Removido o prefixo 'admin/' para evitar conflito)
    path('dashboard-administrativo/', views.dashboard_administrativo, name='admin_dashboard'),
    path('gestao/excluir-turma/<int:turma_id>/', views.excluir_turma_admin, name='excluir_turma_admin'),
    
    # 2. Instituições (CRUD Completo)
    path('instituicoes/', views.listar_instituicoes, name='listar_instituicoes'),
    path('instituicao/nova/', views.criar_instituicao, name='criar_instituicao'),
    path('instituicao/editar/<int:pk>/', views.editar_instituicao, name='editar_instituicao'),
    path('instituicao/excluir/<int:pk>/', views.excluir_instituicao, name='excluir_instituicao'),
    
    # 3. Turmas
    path('turmas/', views.listar_turmas, name='listar_turmas'),
    path('turmas/nova/', views.criar_turma, name='criar_turma'),
    path('turma/editar/<int:pk>/', views.editar_turma, name='editar_turma'),
    path('turma/excluir/<int:pk>/', views.excluir_turma, name='excluir_turma'),
    path('turma/<int:pk>/', views.detalhes_turma, name='detalhes_turma'),
    path('turma/<int:turma_id>/alunos/', views.listar_alunos_turma, name='listar_alunos_turma'),
    path('aluno/remover/<int:aluno_id>/', views.remover_aluno_turma, name='remover_aluno'),
    
    # 4. Áreas de Conhecimento
    path('areas/', views.listar_areas, name='listar_areas'),
    path('area/nova/', views.criar_area, name='criar_area'),
    path('area/editar/<int:pk>/', views.editar_area, name='editar_area'),
    path('area/excluir/<int:pk>/', views.excluir_area, name='excluir_area'),
    
    # 5. Disciplinas (CRUD)
    path('minhas-disciplinas/', views.listar_disciplinas, name='listar_disciplinas'),
    path('disciplina/nova/', views.criar_disciplina, name='criar_disciplina'),
    path('disciplina/editar/<int:pk>/', views.editar_disciplina, name='editar_disciplina'),
    path('disciplina/excluir/<int:pk>/', views.excluir_disciplina, name='excluir_disciplina'),
    path('disciplina/<int:pk>/', views.detalhes_disciplina, name='detalhes_disciplina'),

    # 6. Aulas
    path('disciplina/<int:disciplina_id>/aulas/', views.gerenciar_aulas, name='gerenciar_aulas'),
    path('disciplina/<int:disciplina_id>/aula/nova/', views.criar_aula, name='criar_aula'),
    path('aula/<int:pk>/editar/', views.editar_aula, name='editar_aula'),
    path('aula/<int:aula_id>/alternar-publicacao/', views.alternar_publicacao, name='alternar_publicacao'),
    path('aula/<int:aula_id>/', views.visualizar_aula, name='visualizar_aula'),
    path('aula/<int:aula_id>/recursos/', views.gerenciar_recursos, name='gerenciar_recursos'),
    path('aula/selecionar-disciplina/', views.selecionar_disciplina_para_aula, name='selecionar_disciplina_para_aula'),
    

    # 7. Aluno (Vínculos e Visualização)
    path('aluno/minhas-disciplinas/', views.ver_disciplinas_do_aluno, name='ver_disciplinas_aluno'),
    # A view abaixo deve ser implementada no views.py para funcionar
    path('aluno/matricular/<int:turma_id>/', views.matricular_aluno, name='matricular_aluno'),
    path('aluno/matricular-manual/', views.matricular_aluno_manual, name='matricular_aluno_manual'),
]