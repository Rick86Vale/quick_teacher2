# Path: academico/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from usuarios.views import eh_professor
from .models import AreaConhecimento, Disciplina, Aula, Turma, Instituicao
from .forms import TurmaForm, InstituicaoForm

# 1. Index
def index(request):
    areas = AreaConhecimento.objects.all()
    orfas = Disciplina.objects.filter(area__isnull=True)
    return render(request, 'academico/index.html', {'areas': areas, 'orfas': orfas})

# 2. Instituições
@login_required
@user_passes_test(eh_professor, login_url='login')
def criar_instituicao(request):
    if request.method == 'POST':
        form = InstituicaoForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.professor = request.user
            inst.save()
            return redirect('dashboard_professor')
    else:
        form = InstituicaoForm()
    return render(request, 'academico/criar_instituicao.html', {'form': form})

@login_required
@user_passes_test(eh_professor)
def listar_instituicoes(request):
    instituicoes = Instituicao.objects.filter(professor=request.user)
    return render(request, 'academico/listar_instituicoes.html', {'instituicoes': instituicoes})

@login_required
@user_passes_test(eh_professor)
def editar_instituicao(request, pk):
    inst = get_object_or_404(Instituicao, pk=pk, professor=request.user)
    if request.method == 'POST':
        form = InstituicaoForm(request.POST, instance=inst)
        if form.is_valid():
            form.save()
            return redirect('listar_instituicoes')
    else:
        form = InstituicaoForm(instance=inst)
    return render(request, 'academico/criar_instituicao.html', {'form': form})

@login_required
@user_passes_test(eh_professor)
def excluir_instituicao(request, pk):
    inst = get_object_or_404(Instituicao, pk=pk, professor=request.user)
    if request.method == 'POST':
        inst.delete()
        return redirect('listar_instituicoes')
    return render(request, 'academico/confirmar_exclusao.html', {'item': inst})

# 3. Turmas
@login_required
def listar_turmas(request):
    if request.user.is_superuser:
        turmas = Turma.objects.all().order_by('instituicao__nome', 'nome')
    else:
        # Ordenamos por instituicao para o regroup do template funcionar
        turmas = Turma.objects.filter(instituicao__professor=request.user).order_by('instituicao__nome', 'nome')
    
    return render(request, 'academico/listar_turmas.html', {'turmas': turmas})

@login_required
def detalhes_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk, instituicao__professor=request.user)
    return render(request, 'academico/detalhes_turma.html', {'turma': turma})

@login_required
def criar_turma(request):
    if not Instituicao.objects.filter(professor=request.user).exists():
        return render(request, 'academico/sem_instituicao.html')
    
    if request.method == 'POST':
        form = TurmaForm(request.POST, user=request.user)
        if form.is_valid():
            form.save() 
            return redirect('listar_turmas')
    else:
        form = TurmaForm(user=request.user)
    return render(request, 'academico/criar_turma.html', {'form': form})

@login_required
@user_passes_test(eh_professor)
def editar_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk, instituicao__professor=request.user)
    if request.method == 'POST':
        form = TurmaForm(request.POST, instance=turma, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('listar_turmas')
    else:
        form = TurmaForm(instance=turma, user=request.user)
    return render(request, 'academico/criar_turma.html', {'form': form})

@login_required
@user_passes_test(eh_professor)
def excluir_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk, instituicao__professor=request.user)
    if request.method == 'POST':
        turma.delete()
        return redirect('listar_turmas')
    return render(request, 'academico/confirmar_exclusao.html', {'item': turma})

# 4. Disciplinas (CRUD Completo)
@login_required
@user_passes_test(eh_professor)
def criar_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST)
        if form.is_valid():
            disciplina = form.save(commit=False)
            disciplina.professor = request.user
            disciplina.save()
            return redirect('listar_disciplinas')
    else:
        form = DisciplinaForm()
    return render(request, 'academico/criar_disciplina.html', {'form': form})

@login_required
@user_passes_test(eh_professor)
def listar_disciplinas(request):
    if request.user.is_superuser:
        disciplinas = Disciplina.objects.all()
    else:
        disciplinas = Disciplina.objects.filter(professor=request.user)
    return render(request, 'academico/lista_disciplinas.html', {'disciplinas': disciplinas})

@login_required
@user_passes_test(eh_professor)
def editar_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk, professor=request.user)
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            form.save()
            return redirect('listar_disciplinas')
    else:
        form = DisciplinaForm(instance=disciplina)
    return render(request, 'academico/criar_disciplina.html', {'form': form})

@login_required
@user_passes_test(eh_professor)
def excluir_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk, professor=request.user)
    if request.method == 'POST':
        disciplina.delete()
        return redirect('listar_disciplinas')
    return render(request, 'academico/confirmar_exclusao.html', {'item': disciplina})


# 5. Aulas
@login_required
def gerenciar_aulas(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id, professor=request.user)
    aulas = Aula.objects.filter(disciplina=disciplina)
    return render(request, 'academico/gerenciar_aulas.html', {
        'disciplina': disciplina,
        'aulas': aulas
    })