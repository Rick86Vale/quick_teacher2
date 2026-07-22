from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
import markdown

from ..models import Tutorial
from ..forms import TutorialForm
from usuarios.views import eh_professor

# Restrição unificada: Permite acesso se for Professor ou Staff/Admin
def eh_professor_ou_admin(user):
    return user.is_authenticated and (user.is_staff or eh_professor(user))

@login_required
@user_passes_test(eh_professor_ou_admin)
def criar_tutorial(request):
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        if form.is_valid():
            tutorial = form.save(commit=False)
            tutorial.professor = request.user
            if not tutorial.slug:
                tutorial.slug = slugify(tutorial.titulo)
            tutorial.save()
            messages.success(request, "Tutorial criado! Agora você pode editar o conteúdo avançado.")
            return redirect('editar_conteudo_tutorial', pk=tutorial.pk)
    else:
        form = TutorialForm()
    return render(request, 'academico/tutoriais/criar_tutorial.html', {'form': form})

@login_required
@user_passes_test(eh_professor_ou_admin)
def editar_tutorial(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if not request.user.is_staff and tutorial.professor != request.user:
        raise PermissionDenied("Você só pode editar seus próprios tutoriais.")
        
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES, instance=tutorial)
        if form.is_valid():
            form.save()
            messages.success(request, "Informações básicas atualizadas com sucesso!")
            return redirect('listar_tutoriais')
    else:
        form = TutorialForm(instance=tutorial)
    return render(request, 'academico/tutoriais/editar_tutorial.html', {'form': form, 'tutorial': tutorial})

@login_required
@user_passes_test(eh_professor_ou_admin)
def excluir_tutorial(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if not request.user.is_staff and tutorial.professor != request.user:
        raise PermissionDenied("Você só pode excluir seus próprios tutoriais.")
        
    if request.method == 'POST':
        tutorial.delete()
        messages.success(request, "Tutorial excluído com sucesso!")
        return redirect('listar_tutoriais')
    return render(request, 'academico/tutoriais/excluir_tutorial.html', {'tutorial': tutorial})

@login_required
@user_passes_test(eh_professor_ou_admin)
def editar_conteudo_tutorial(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if not request.user.is_staff and tutorial.professor != request.user:
        raise PermissionDenied("Acesso negado.")
        
    if request.method == 'POST':
        tutorial.titulo = request.POST.get('titulo', tutorial.titulo)
        tutorial.conteudo = request.POST.get('conteudo', '')
        tutorial.save()
        messages.success(request, "Conteúdo do tutorial atualizado com sucesso!")
        return redirect('detalhe_tutorial', pk=tutorial.pk)
        
    return render(request, 'academico/tutoriais/editar_conteudo_tutorial.html', {'tutorial': tutorial})

@login_required
def listar_tutoriais(request):
    user = request.user
    if user.is_staff:
        tutoriais = Tutorial.objects.all().order_by('-data_criacao')
    elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'PROFESSOR':
        # Professor vê os tutoriais criados por ele
        tutoriais = Tutorial.objects.filter(professor=user).order_by('-data_criacao')
    else:
        # Aluno vê os tutoriais dos professores das turmas em que está matriculado
        from academico.models import Aluno
        try:
            aluno = Aluno.objects.get(user=user)
            # Pega os professores associados às turmas do aluno
            professores_das_turmas = [turma.professor for turma in aluno.turmas.all() if hasattr(turma, 'professor')]
            
            tutoriais = Tutorial.objects.filter(
                publicado=True,
                professor__in=professores_das_turmas
            ).distinct().order_by('-data_criacao')
        except Aluno.DoesNotExist:
            tutoriais = Tutorial.none()
            
    return render(request, 'academico/tutoriais/listar_tutoriais.html', {'tutoriais': tutoriais})

@login_required
def detalhe_tutorial(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    user = request.user
    
    e_autor = (user == tutorial.professor or user.is_staff)
    if not e_autor:
        from academico.models import Aluno
        try:
            aluno = Aluno.objects.get(user=user)
            # Verifica se o professor do tutorial leciona em alguma turma do aluno
            tem_acesso = aluno.turmas.filter(professor=tutorial.professor).exists()
        except Exception:
            tem_acesso = False
            
        if not tem_acesso or not tutorial.publicado:
            raise PermissionDenied("Você não tem permissão para visualizar este tutorial.")

    conteudo_html = markdown.markdown(tutorial.conteudo or "", extensions=['fenced_code', 'codehilite'])
    
    return render(request, 'academico/tutoriais/detalhe_tutorial.html', {
        'tutorial': tutorial,
        'conteudo_html': conteudo_html,
        'e_autor': e_autor
    })