# Path: academico/urls.py
from django.urls import path
from .views import academico, admin, aluno, aulas, disciplinas



urlpatterns = [
    # 0. Index
    path('', academico.index, name='index'),

    # 1. Administrador (views/admin.py)
    path('dashboard-administrativo/', admin.dashboard_administrativo, name='admin_dashboard'),
    path('gestao/excluir-turma/<int:turma_id>/', admin.excluir_turma_admin, name='excluir_turma_admin'),
    
    # 2. Instituições (views/academico.py)
    path('instituicoes/', academico.listar_instituicoes, name='listar_instituicoes'),
    path('instituicao/nova/', academico.criar_instituicao, name='criar_instituicao'),
    path('instituicao/editar/<int:pk>/', academico.editar_instituicao, name='editar_instituicao'),
    path('instituicao/excluir/<int:pk>/', academico.excluir_instituicao, name='excluir_instituicao'),
    
    # 3. Turmas (views/academico.py)
    path('turmas/', academico.listar_turmas, name='listar_turmas'),
    path('turmas/nova/', academico.criar_turma, name='criar_turma'),
    path('turma/editar/<int:pk>/', academico.editar_turma, name='editar_turma'),
    path('turma/excluir/<int:pk>/', academico.excluir_turma, name='excluir_turma'),
    path('turma/<int:pk>/', academico.detalhes_turma, name='detalhes_turma'),
    path('turma/<int:turma_id>/alunos/', aluno.listar_alunos_turma, name='listar_alunos_turma'),
    #path('aluno/remover/<int:aluno_id>/', academico.remover_aluno_turma, name='remover_aluno'),
    
    # 4. Áreas de Conhecimento (views/academico.py)
    path('areas/', academico.listar_areas, name='listar_areas'),
    path('area/nova/', academico.criar_area, name='criar_area'),
    path('area/editar/<int:pk>/', academico.editar_area, name='editar_area'),
    path('area/excluir/<int:pk>/', academico.excluir_area, name='excluir_area'),
    
    # 5. Disciplinas (views/academico.py)
    path('minhas-disciplinas/', disciplinas.listar_disciplinas, name='listar_disciplinas'),
    path('disciplina/nova/', disciplinas.criar_disciplina, name='criar_disciplina'),
    path('disciplina/editar/<int:pk>/', disciplinas.editar_disciplina, name='editar_disciplina'),
    path('disciplina/excluir/<int:pk>/', disciplinas.excluir_disciplina, name='excluir_disciplina'),
    path('disciplina/<int:pk>/', disciplinas.detalhes_disciplina, name='detalhes_disciplina'),
    # Exportar/Importar disciplina
    path('disciplina/<int:disciplina_id>/exportar/', disciplinas.exportar_disciplina, name='exportar_disciplina'),
    path('disciplina/importar/', disciplinas.importar_disciplina, name='importar_disciplina'),

    # 6. Aulas (views/academico.py)
    path('disciplina/<int:disciplina_id>/aulas/', aulas.gerenciar_aulas, name='gerenciar_aulas'),
    path('disciplina/<int:disciplina_id>/aula/nova/', aulas.criar_aula, name='criar_aula'),
    path('aula/<int:pk>/editar/', aulas.editar_aula, name='editar_aula'),
    path('aula/<int:aula_id>/alternar-publicacao/', aulas.alternar_publicacao, name='alternar_publicacao'),
    path('aula/<int:aula_id>/', aulas.visualizar_aula, name='visualizar_aula'),
    path('aula/selecionar-disciplina/', aulas.selecionar_disciplina_para_aula, name='selecionar_disciplina_para_aula'),
    path('aula/<int:pk>/excluir/', aulas.excluir_aula, name='excluir_aula'),

    
    # 6.1 Recursos (views/academico.py)
    path('aula/<int:aula_id>/recursos/', aulas.menu_recursos, name='menu_recursos'),
    path('aula/<int:aula_id>/videos/', aulas.gerenciar_videos, name='gerenciar_videos'),
    path('aula/<int:aula_id>/pdfs/', aulas.gerenciar_pdfs, name='gerenciar_pdfs'),
    path('aula/<int:aula_id>/links/', aulas.gerenciar_links, name='gerenciar_links'),
    
    # 7. Aluno (views/aluno.py)
    path('aluno/minhas-disciplinas/', aluno.ver_disciplinas_do_aluno, name='ver_disciplinas_aluno'),
    path('aluno/matricular-manual/', aluno.matricular_aluno_manual, name='matricular_aluno_manual'),
    path('aluno/matricular-manual/<int:turma_id>/', aluno.matricular_aluno_manual, name='matricular_aluno'),
    path('turma/<int:turma_id>/remover-aluno/<int:aluno_id>/', aluno.remover_aluno_turma, name='remover_aluno_da_turma'),
    
]
