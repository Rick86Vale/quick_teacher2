from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
import markdown

from ..models import Tutorial
from ..forms import TutorialForm

# Restrição: Apenas administradores
def eh_admin(user):
    return user.is_staff

@login_required
def listar_tutoriais(request):
    tutoriais = Tutorial.objects.all().order_by('-data_criacao')
    return render(request, 'academico/tutoriais/listar_tutoriais.html', {'tutoriais': tutoriais})

@login_required
@user_passes_test(eh_admin)
def criar_tutorial(request):
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_tutoriais')
    else:
        form = TutorialForm()
    return render(request, 'academico/tutoriais/criar_tutorial.html', {'form': form})

@login_required
def detalhe_tutorial(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    # Converte o conteúdo Markdown para HTML
    conteudo_html = markdown.markdown(tutorial.conteudo, extensions=['fenced_code', 'codehilite'])
    
    return render(request, 'academico/tutoriais/detalhe_tutorial.html', {
        'tutorial': tutorial,
        'conteudo_html': conteudo_html
    })

@staff_member_required
def editar_tutorial(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES, instance=tutorial)
        if form.is_valid():
            form.save()
            return redirect('listar_tutoriais')
    else:
        form = TutorialForm(instance=tutorial)
    return render(request, 'academico/tutoriais/editar_tutorial.html', {'form': form, 'tutorial': tutorial})

@staff_member_required
def excluir_tutorial(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if request.method == 'POST':
        tutorial.delete()
        return redirect('listar_tutoriais')
    return render(request, 'academico/tutoriais/excluir_tutorial.html', {'tutorial': tutorial})