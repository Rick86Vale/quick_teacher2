# Path: academico/views/aulas.py
import markdown
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.forms import inlineformset_factory

# Importações dos modelos e formulários
from ..models import Disciplina, Aula, Aluno, Recurso
from ..forms import AulaForm, RecursoFormSet

# --- 5. AULAS E RECURSOS ---

# 5.1. Listagem de Aulas
@login_required
def gerenciar_aulas(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    e_autor = (request.user == disciplina.professor or request.user.is_staff)
    e_aluno = Aluno.objects.filter(user=request.user, turma__disciplinas=disciplina).exists()
    
    if not e_autor and not e_aluno:
        raise PermissionDenied("Você não está matriculado nesta disciplina.")
    
    if e_aluno and not e_autor:
        aulas = Aula.objects.filter(disciplina=disciplina, publicado=True).order_by('ordem')
    else:
        aulas = Aula.objects.filter(disciplina=disciplina).order_by('ordem')
        
    return render(request, 'academico/aulas/gerenciar_aulas.html', {'disciplina': disciplina, 'aulas': aulas, 'e_autor': e_autor})

# 5.2. Criação de Aula
@login_required
def criar_aula(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    if not (request.user == disciplina.professor or request.user.is_staff):
        raise PermissionDenied("Acesso negado.")
    
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.disciplina = disciplina
            aula.ordem = Aula.objects.filter(disciplina=disciplina).count() + 1
            aula.save()
            return redirect('menu_recursos', aula_id=aula.pk) 
    else:
        form = AulaForm()
    return render(request, 'academico/aulas/criar_aula.html', {'form': form, 'disciplina': disciplina})

# 5.3. Menu Central de Recursos
@login_required
def menu_recursos(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    return render(request, 'academico/recursos/menu_recursos.html', {'aula': aula})

# 5.4. Gestão de Recursos por Tipo
@login_required
def gerenciar_recursos_por_tipo(request, aula_id, tipo):
    aula = get_object_or_404(Aula, pk=aula_id)
    RecursoFormSet = inlineformset_factory(Aula, Recurso, fields=('titulo', 'url', 'arquivo', 'thumbnail', 'tipo'), extra=1)
    
    if request.method == 'POST':
        formset = RecursoFormSet(request.POST, request.FILES, instance=aula, queryset=Recurso.objects.filter(tipo=tipo))
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data:
                    form.instance.tipo = tipo
            formset.save()
            return redirect('menu_recursos', aula_id=aula.pk)
    else:
        formset = RecursoFormSet(instance=aula, queryset=Recurso.objects.filter(tipo=tipo))
    
    return render(request, 'academico/recursos/gerenciar_tipo.html', {'aula': aula, 'formset': formset, 'tipo': tipo})

# 5.5. Alternar Publicação
@login_required
@require_POST
def alternar_publicacao(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    if request.user == aula.disciplina.professor or request.user.is_staff:
        aula.publicado = not aula.publicado
        aula.save()
    return redirect('gerenciar_aulas', disciplina_id=aula.disciplina.id)

# 5.6. Visualizar Aula
def visualizar_aula(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    # A variável disciplina já está disponível através de aula.disciplina
    
    e_autor = (request.user == aula.disciplina.professor or request.user.is_staff)
    if not aula.publicado and not e_autor:
        raise PermissionDenied("Esta aula ainda não foi publicada.")
    
    conteudo_html = mark_safe(markdown.markdown(aula.conteudo, extensions=['fenced_code', 'tables', 'nl2br']))
    
    # Certifique-se de passar o objeto aula no contexto
    return render(request, 'academico/aulas/visualizar_aula.html', {
        'aula': aula, 
        'disciplina': aula.disciplina, # <--- ADICIONE ESTA LINHA SE ELA NÃO EXISTIR
        'conteudo_html': conteudo_html, 
        'e_autor': e_autor
    })

# 5.7. Editar Aula
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
    return render(request, 'academico/aulas/editar_aula.html', {'form': form, 'aula': aula})

# 5.8. Seletor de Disciplina
@login_required
def selecionar_disciplina_para_aula(request):
    disciplinas = Disciplina.objects.filter(professor=request.user)
    if request.method == 'POST':
        return redirect('criar_aula', disciplina_id=request.POST.get('disciplina_id'))
    return render(request, 'academico/disciplinas/selecionar_disciplina.html', {'disciplinas': disciplinas})