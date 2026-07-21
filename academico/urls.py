# Path: academico/urls.py
from django.urls import path
from .views import academico, admin, aluno, aulas, disciplinas, tutoriais
from academico.views import disciplinas
from academico.views import admin as admin_views
from . import views


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
    # Rota para abrir a tela de reordenação
    path('disciplina/<int:pk>/reordenar/', aulas.reordenar_aulas_template, name='reordenar_aulas_template'),
    # Rota que o JavaScript chama para salvar a nova ordem
    path('disciplina/<int:pk>/reordenar/salvar/', aulas.reordenar_aulas_salvar, name='reordenar_aulas'),
    path('disciplina/<int:pk>/reordenar/confirmar/', aulas.reordenar_confirmacao, name='reordenar_confirmacao'),
    path('aula/<int:aula_id>/marcar-lida/', aulas.marcar_aula_lida, name='marcar_aula_lida'),
    # Rota para salvar e excluir a imagem copiada
    path('upload-imagem/', views.upload_imagem_ajax, name='upload_imagem_ajax'),
    path('admin/imagens/excluir-selecionadas/', admin_views.excluir_imagens_selecionadas, name='excluir_imagens_selecionadas'),
    path('admin/imagens/excluir-tudo/', admin_views.excluir_tudo_nao_usado, name='excluir_tudo_nao_usado'),
    #Comentário do professor
    path('aula/<int:aula_pk>/comentario/adicionar/', views.adicionar_comentario_contextual, name='adicionar_comentario_contextual'),
    path('comentario/<int:comentario_pk>/excluir/', views.excluir_comentario_contextual, name='excluir_comentario_contextual'),
    
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
    # Progresso Aluno
    path('turma/<int:turma_id>/aluno/<int:aluno_id>/progresso/', disciplinas.progresso_aluno_individual, name='progresso_aluno_individual'),
    
    path('aluno/turmas/', academico .listar_turmas_aluno, name='listar_turmas_aluno'),

    # 8. Tutorias
    path('tutoriais/', tutoriais.listar_tutoriais, name='listar_tutoriais'),
    path('tutoriais/criar/', tutoriais.criar_tutorial, name='criar_tutorial'),
    path('tutoriais/<int:pk>/', tutoriais.detalhe_tutorial, name='detalhe_tutorial'),

    path('tutoriais/<int:pk>/editar/', tutoriais.editar_tutorial, name='editar_tutorial'),
    path('tutoriais/<int:pk>/excluir/', tutoriais.excluir_tutorial, name='excluir_tutorial'),

    #9. Avisos e Eventos
    path('turma/<int:pk>/avisos/', disciplinas.listar_avisos, name='listar_avisos'),
    path('turma/<int:turma_pk>/aviso/novo/', disciplinas.criar_aviso, name='criar_aviso'),
    path('aviso/<int:pk>/editar/', disciplinas.editar_aviso, name='editar_aviso'),
    path('aviso/<int:pk>/excluir/', disciplinas.excluir_aviso, name='excluir_aviso'),
    path('turma/<int:turma_pk>/evento/novo/', disciplinas.criar_evento, name='criar_evento'),
    path('evento/<int:pk>/editar/', disciplinas.editar_evento, name='editar_evento'),
    path('evento/<int:pk>/excluir/', disciplinas.excluir_evento, name='excluir_evento'),

    #10.Criaçao de Slides
    path('aula/<int:aula_id>/baixar-slides/', aulas.baixar_slides, name='baixar_slides'),
    path('aula/<int:aula_id>/editar-slide/', aulas.editar_conteudo_slide, name='editar_conteudo_slide'),

]

urlpatterns += [
    path('admin/imagens/', admin_views.gerenciar_imagens, name='gerenciar_imagens'),
    path('admin/imagens/excluir/<str:nome_imagem>/', admin_views.excluir_imagem, name='excluir_imagem'),
]
    
