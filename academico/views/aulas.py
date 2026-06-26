# Path: academico/views/aulas.py
import markdown
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST

# Importações dos modelos e formulários
from ..models import Disciplina, Aula, Aluno
from ..forms import AulaForm, RecursoFormSet

# --- 5. AULAS ---

@login_required
def gerenciar_aulas(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    
    # 1. Identificar papéis
    e_autor = (request.user == disciplina.professor or request.user.is_staff)
    
    # Verifica se o aluno está matriculado em alguma turma que tenha esta disciplina
    # Ajuste 'turma__disciplinas' conforme o relacionamento no seu models.py
    e_aluno = Aluno.objects.filter(user=request.user, turma__disciplinas=disciplina).exists()
    
    # 2. Proteção: Bloquear quem não é autor nem aluno matriculado
    if not e_autor and not e_aluno:
        raise PermissionDenied("Você não está matriculado nesta disciplina.")
    
    # 3. Filtrar aulas: Alunos só veem as publicadas
    if e_aluno and not e_autor:
        aulas = Aula.objects.filter(disciplina=disciplina, publicado=True).order_by('ordem')
    else:
        aulas = Aula.objects.filter(disciplina=disciplina).order_by('ordem')
        
    return render(request, 'academico/gerenciar_aulas.html', {
        'disciplina': disciplina,
        'aulas': aulas,
        'e_autor': e_autor
    })

@login_required
def criar_aula(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    
    if not (request.user == disciplina.professor or request.user.is_staff):
        raise PermissionDenied("Você não pode criar aulas nesta disciplina.")
    
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.disciplina = disciplina
            aula.ordem = Aula.objects.filter(disciplina=disciplina).count() + 1
            aula.save()
            messages.success(request, "Aula criada! Agora adicione os recursos.")
            return redirect('gerenciar_recursos', aula_id=aula.pk) 
    else:
        form = AulaForm()
        
    return render(request, 'academico/criar_aula.html', {'form': form, 'disciplina': disciplina})

@login_required
def gerenciar_recursos(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if not (request.user == aula.disciplina.professor or request.user.is_staff):
        raise PermissionDenied("Acesso negado.")
    
    if request.method == 'POST':
        formset = RecursoFormSet(request.POST, request.FILES, instance=aula)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Recursos salvos!")
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        formset = RecursoFormSet(instance=aula)
        
    return render(request, 'academico/gerenciar_recursos.html', {'aula': aula, 'formset': formset})

@login_required
@require_POST
def alternar_publicacao(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    if request.user == aula.disciplina.professor or request.user.is_staff:
        aula.publicado = not aula.publicado
        aula.save()
    return redirect('gerenciar_aulas', disciplina_id=aula.disciplina.id)

def visualizar_aula(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    disciplina = aula.disciplina
    
    e_autor = (request.user == disciplina.professor or request.user.is_staff)
    
    # Bloqueia alunos de acessar rascunhos, mas permite que autores editem
    if not aula.publicado and not e_autor:
        raise PermissionDenied("Esta aula ainda não foi publicada.")
    
    conteudo_html = mark_safe(markdown.markdown(
        aula.conteudo, 
        extensions=['fenced_code', 'tables', 'nl2br']
    ))
        
    return render(request, 'academico/visualizar_aula.html', {
        'aula': aula,
        'disciplina': disciplina,
        'conteudo_html': conteudo_html,
        'e_autor': e_autor
    })

@login_required
def editar_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if not (request.user == aula.disciplina.professor or request.user.is_staff):
        raise PermissionDenied("Sem permissão.")

    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        form = AulaForm(instance=aula)
        
    return render(request, 'academico/editar_aula.html', {'form': form, 'aula': aula})

@login_required
def selecionar_disciplina_para_aula(request):
    # Lista apenas as disciplinas que pertencem a este professor
    disciplinas = Disciplina.objects.filter(professor=request.user)
    
    if request.method == 'POST':
        disciplina_id = request.POST.get('disciplina_id')
        return redirect('criar_aula', disciplina_id=disciplina_id)
        
    return render(request, 'academico/selecionar_disciplina.html', {'disciplinas': disciplinas})