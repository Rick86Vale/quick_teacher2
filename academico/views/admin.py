# Path: academico/views/admin.py
import os
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Turma, Instituicao, Aluno, Disciplina
from academico.models import Aula

from django.contrib.auth import get_user_model

User = get_user_model()

# --- ADMINISTRADOR ---
@staff_member_required
def dashboard_administrativo(request):
    # Buscamos professores com suas instituições e disciplinas, 
    # sem tentar prefetchar campos inexistentes na Turma
    professores = User.objects.filter(tipo_usuario='PROFESSOR').prefetch_related(
        'instituicao_set', 
        'disciplina_set'
    )
    
    turmas = Turma.objects.all() # Prefetch simplificado

    context = {
        'professores': professores,
        'turmas': turmas,
        'total_disciplinas_geral': Disciplina.objects.count(),
        'total_alunos_geral': Aluno.objects.count(),
    }
    return render(request, 'academico/admin_dashboard.html', context)



@staff_member_required
def excluir_turma_admin(request, turma_id):
    """Exclusão de turmas com permissão de administrador."""
    turma = get_object_or_404(Turma, pk=turma_id)
    nome_turma = turma.nome
    turma.delete()
    messages.success(request, f"Turma '{nome_turma}' excluída com sucesso.")
    return redirect('admin_dashboard')

from collections import defaultdict




def dashboard(request):
    disciplinas = Disciplina.objects.all().select_related('professor')
    disciplinas_por_professor = defaultdict(list)
    
    for d in disciplinas:
        disciplinas_por_professor[d.professor].append(d)
        
    return render(request, 'dashboard.html', {
        'disciplinas_por_professor': dict(disciplinas_por_professor)
    })


@staff_member_required
def gerenciar_imagens(request):
    media_path = os.path.join(settings.MEDIA_ROOT, 'aulas')
    if not os.path.exists(media_path):
        os.makedirs(media_path)
    
    imagens = []
    for nome_arquivo in os.listdir(media_path):
        caminho_url = os.path.join(settings.MEDIA_URL, 'aulas', nome_arquivo)
        # Verifica se o nome do arquivo está em alguma aula
        esta_em_uso = Aula.objects.filter(conteudo__contains=nome_arquivo).exists()
        
        imagens.append({
            'nome': nome_arquivo,
            'url': caminho_url,
            'em_uso': esta_em_uso
        })
    
    return render(request, 'academico/admin/gerenciar_imagens.html', {'imagens': imagens})

@staff_member_required
def excluir_imagem(request, nome_imagem):
    caminho_completo = os.path.join(settings.MEDIA_ROOT, 'aulas', nome_imagem)
    
    # Checagem de segurança
    if Aula.objects.filter(conteudo__contains=nome_imagem).exists():
        messages.error(request, "Esta imagem está sendo usada em uma aula e não pode ser excluída.")
    else:
        if os.path.exists(caminho_completo):
            os.remove(caminho_completo)
            messages.success(request, f"Imagem {nome_imagem} excluída com sucesso.")
    
    return redirect('gerenciar_imagens')

@staff_member_required
def excluir_imagens_selecionadas(request):
    if request.method == 'POST':
        ids_para_excluir = request.POST.getlist('imagens_selecionadas')
        contagem = 0
        
        for nome_imagem in ids_para_excluir:
            # Verifica novamente se não está em uso (segurança)
            if not Aula.objects.filter(conteudo__contains=nome_imagem).exists():
                caminho = os.path.join(settings.MEDIA_ROOT, 'aulas', nome_imagem)
                if os.path.exists(caminho):
                    os.remove(caminho)
                    contagem += 1
        
        if contagem > 0:
            messages.success(request, f"{contagem} imagem(ns) excluída(s) com sucesso.")
        else:
            messages.warning(request, "Nenhuma imagem válida foi selecionada.")
            
    return redirect('gerenciar_imagens')

@staff_member_required
def excluir_tudo_nao_usado(request):
    media_path = os.path.join(settings.MEDIA_ROOT, 'aulas')
    contagem = 0
    
    if os.path.exists(media_path):
        for nome_arquivo in os.listdir(media_path):
            # Verifica se NÃO está em uso
            if not Aula.objects.filter(conteudo__contains=nome_arquivo).exists():
                caminho_completo = os.path.join(media_path, nome_arquivo)
                if os.path.exists(caminho_completo):
                    os.remove(caminho_completo)
                    contagem += 1
    
    if contagem > 0:
        messages.success(request, f"Limpeza concluída! {contagem} imagens não utilizadas foram removidas.")
    else:
        messages.info(request, "Nenhuma imagem desnecessária foi encontrada para excluir.")
        
    return redirect('gerenciar_imagens')