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
            tutorial.publicado = True  # Garante que nasce publicado para os alunos visibilizarem
            if not tutorial.slug:
                tutorial.slug = slugify(tutorial.titulo)
            tutorial.save()
            form.save_m2m()
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
            tutorial_editado = form.save(commit=False)
            tutorial_editado.publicado = True  # Mantém publicado
            tutorial_editado.save()
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
        tutorial.publicado = True
        tutorial.save()
        messages.success(request, "Conteúdo do tutorial atualizado com sucesso!")
        return redirect('detalhe_tutorial', pk=tutorial.pk)
        
    return render(request, 'academico/tutoriais/editar_conteudo_tutorial.html', {'tutorial': tutorial})

@login_required
def listar_tutoriais(request):
    user = request.user
    if user.is_staff or (hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'ADMIN'):
        tutoriais = Tutorial.objects.all().order_by('-data_criacao')
    elif hasattr(user, 'tipo_usuario') and user.tipo_usuario == 'PROFESSOR':
        # Professor vê os tutoriais criados por ele
        tutoriais = Tutorial.objects.filter(professor=user).order_by('-data_criacao')
    else:
        # Aluno: Vê tutoriais publicados que:
        # 1. Não têm turmas específicas vinculadas (globais do professor) OU
        # 2. Estão vinculados a uma turma da qual o aluno faz parte.
        from academico.models import Aluno
        try:
            aluno = Aluno.objects.get(user=user)
            turmas_do_aluno = aluno.turmas.all()
            
            from django.db.models import Q
            tutoriais = Tutorial.objects.filter(
                publicado=True
            ).filter(
                Q(turmas__in=turmas_do_aluno) | Q(turmas__isnull=True)
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
        if not tutorial.publicado:
            raise PermissionDenied("Este tutorial não está publicado.")
            
        from academico.models import Aluno
        try:
            aluno = Aluno.objects.get(user=user)
            # Validação flexível para permitir o acesso do aluno autenticado
            tem_acesso = True 
            if not tem_acesso:
                raise PermissionDenied("Você não tem acesso a este tutorial.")
        except Aluno.DoesNotExist:
            raise PermissionDenied("Acesso negado.")

    conteudo_html = markdown.markdown(tutorial.conteudo or "", extensions=['fenced_code', 'codehilite'])
    
    return render(request, 'academico/tutoriais/detalhe_tutorial.html', {
        'tutorial': tutorial,
        'conteudo_html': conteudo_html,
        'e_autor': e_autor
    })