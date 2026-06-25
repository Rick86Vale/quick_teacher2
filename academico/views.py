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

# 3. Turmas
@login_required
def listar_turmas(request):
    if request.user.is_superuser:
        turmas = Turma.objects.all()
    else:
        turmas = Turma.objects.filter(instituicao__professor=request.user)
    return render(request, 'academico/listar_turmas.html', {'turmas': turmas})

@login_required
def criar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST, user=request.user) # Passando o usuário para filtrar
        if form.is_valid():
            turma = form.save()
            form.save_m2m()
            return redirect('listar_turmas')
    else:
        form = TurmaForm(user=request.user)
    return render(request, 'academico/criar_turma.html', {'form': form})

# 4. Disciplinas
@login_required
def listar_disciplinas(request):
    if request.user.is_superuser:
        disciplinas = Disciplina.objects.all()
    else:
        disciplinas = Disciplina.objects.filter(professor=request.user)
    return render(request, 'academico/lista_disciplinas.html', {'disciplinas': disciplinas})

# 5. Aulas
@login_required
def gerenciar_aulas(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id, professor=request.user)
    aulas = Aula.objects.filter(disciplina=disciplina)
    return render(request, 'academico/gerenciar_aulas.html', {
        'disciplina': disciplina,
        'aulas': aulas
    })