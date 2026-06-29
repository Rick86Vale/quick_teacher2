# Path: academico/views/admin.py
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required
from ..models import Turma

# --- ADMINISTRADOR ---
@staff_member_required
def dashboard_administrativo(request):
    """Exibe o painel de controle administrativo com contagem de alunos."""
    turmas = Turma.objects.annotate(total_alunos=Count('alunos'))
    return render(request, 'academico/admin_dashboard.html', {'turmas': turmas})

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