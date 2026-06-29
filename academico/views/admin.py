# Path: academico/views/admin.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Turma, Instituicao, Aluno, Disciplina

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