import markdown
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST
from django.forms import inlineformset_factory
from academico.models import Aula, Disciplina, Aluno

# Importações dos modelos e formulários
from ..models import Disciplina, Aula, Aluno, Video, PDF, LinkUtil
from ..forms import AulaForm, VideoFormSet, PDFFormSet, LinkUtilFormSet




# --- GESTÃO DE AULAS
# 1. Listagem de Aulas
@login_required
def gerenciar_aulas(request, disciplina_id):
    # Fluxo estrito do PROFESSOR
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    # A lógica aqui pode ser focada apenas em EDITAR/CRIAR
    aulas = Aula.objects.filter(disciplina=disciplina).order_by('ordem')
    return render(request, 'academico/aulas/gerenciar_aulas.html', {'disciplina': disciplina, 'aulas': aulas})


# 2. Criação de Aula
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
            # Em criar_aula, após salvar a aula:
            return redirect('menu_recursos', aula_id=aula.pk)
    else:
        form = AulaForm()
    return render(request, 'academico/aulas/criar_aula.html', {'form': form, 'disciplina': disciplina})

# 3. Excluir Aula
@login_required
def excluir_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    # Opcional: checar se o usuário é o professor da disciplina
    disciplina_id = aula.disciplina.id
    aula.delete()
    return redirect('gerenciar_aulas', disciplina_id=disciplina_id)

# 4. Edição de Aula
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

# 5. Visualizar Aula
def visualizar_aula(request, aula_id):
    # Busca a aula pelo ID
    aula = get_object_or_404(Aula, pk=aula_id)
    
    # Define se o usuário tem permissão de autor ou staff
    e_autor = (request.user == aula.disciplina.professor or request.user.is_staff)
    
    # Verifica a permissão de visualização (se não publicado e não for autor)
    if not aula.publicado and not e_autor:
        raise PermissionDenied("Esta aula ainda não foi publicada.")
    
    # A MUDANÇA PRINCIPAL:
    # Passamos o texto puro (aula.conteudo) diretamente para o template.
    # A renderização e a aplicação de cores (codehilite) acontecerão
    # através do filtro personalizado que criamos no 'markdown_extras.py'.
    
    return render(request, 'academico/aulas/visualizar_aula.html', {
        'aula': aula, 
        'disciplina': aula.disciplina, 
        'conteudo_html': aula.conteudo, 
        'e_autor': e_autor
    })


# 6. Alternar Publicação
@login_required
@require_POST
def alternar_publicacao(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    if request.user == aula.disciplina.professor or request.user.is_staff:
        aula.publicado = not aula.publicado
        aula.save()
    return redirect('gerenciar_aulas', disciplina_id=aula.disciplina.id)

# 7. Seletor de Disciplina
@login_required
def selecionar_disciplina_para_aula(request):
    disciplinas = Disciplina.objects.filter(professor=request.user)
    if request.method == 'POST':
        return redirect('criar_aula', disciplina_id=request.POST.get('disciplina_id'))
    return render(request, 'academico/disciplinas/selecionar_disciplina.html', {'disciplinas': disciplinas})

# 7. Recursos
# -- 7.1 Menu de Recursos
@login_required
def menu_recursos(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    return render(request, 'academico/recursos/menu_recursos.html', {'aula': aula})

# -- 7.1.1 Videos
@login_required
def gerenciar_videos(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if request.method == 'POST':
        formset = VideoFormSet(request.POST, instance=aula)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Vídeos atualizados com sucesso!")
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        formset = VideoFormSet(instance=aula)
        
    return render(request, 'academico/recursos/gerenciar_videos.html', {
        'aula': aula,
        'formset': formset
    })

# -- 7.1.2 PDF
@login_required
def gerenciar_pdfs(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if request.method == 'POST':
        formset = PDFFormSet(request.POST, instance=aula)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Links de PDF atualizados!")
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        formset = PDFFormSet(instance=aula)
        
    return render(request, 'academico/recursos/gerenciar_pdfs.html', {
        'aula': aula,
        'formset': formset
    })

# -- 7.1.3 Links Úteis
@login_required
def gerenciar_links(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if request.method == 'POST':
        formset = LinkUtilFormSet(request.POST, instance=aula)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Links úteis atualizados!")
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        formset = LinkUtilFormSet(instance=aula)
        
    return render(request, 'academico/recursos/gerenciar_links.html', {
        'aula': aula,
        'formset': formset
    })

