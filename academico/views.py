# Path: academico/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from usuarios.views import eh_professor
from .models import AreaConhecimento, Disciplina, Aula, Turma, Instituicao, Aluno
from .forms import TurmaForm, InstituicaoForm, DisciplinaForm, AreaConhecimentoForm
from django.db.models import Count
from django.contrib.admin.views.decorators import staff_member_required

# --- ADMINISTRADOR ---
@staff_member_required
def excluir_turma_admin(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    nome_turma = turma.nome
    turma.delete()
    messages.success(request, f"Turma '{nome_turma}' excluída com sucesso.")
    return redirect('admin_dashboard')

@staff_member_required # Garante que apenas administradores vejam
def dashboard_administrativo(request):
    turmas = Turma.objects.annotate(total_alunos=Count('alunos'))
    return render(request, 'academico/admin_dashboard.html', {'turmas': turmas})


# --- UTILS ---
def verificar_senha_e_executar(request, acao_func, pk=None):
    if request.method == 'POST':
        senha = request.POST.get('password_confirm')
        if request.user.check_password(senha):
            return acao_func(request, pk)
        else:
            messages.error(request, "Senha incorreta. Ação cancelada.")
    return render(request, 'academico/confirmar_senha.html', {'pk': pk})

# --- 0. INDEX ---
def index(request):
    areas = AreaConhecimento.objects.all()
    orfas = Disciplina.objects.filter(area__isnull=True)
    return render(request, 'academico/index.html', {'areas': areas, 'orfas': orfas})

# --- 1. INSTITUIÇÕES ---
@login_required
@user_passes_test(eh_professor)
def criar_instituicao(request):
    if request.method == 'POST':
        form = InstituicaoForm(request.POST)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.professor = request.user
            inst.save()
            return redirect('listar_instituicoes')
    return render(request, 'academico/criar_instituicao.html', {'form': InstituicaoForm()})

@login_required
def listar_instituicoes(request):
    instituicoes = Instituicao.objects.filter(professor=request.user)
    return render(request, 'academico/listar_instituicoes.html', {'instituicoes': instituicoes})

@login_required
def editar_instituicao(request, pk):
    inst = get_object_or_404(Instituicao, pk=pk, professor=request.user)
    def acao_editar(req, p):
        form = InstituicaoForm(req.POST, instance=inst)
        if form.is_valid():
            form.save()
            return redirect('listar_instituicoes')
        return render(req, 'academico/criar_instituicao.html', {'form': form})
    if request.method == 'POST': return verificar_senha_e_executar(request, acao_editar, pk)
    return render(request, 'academico/criar_instituicao.html', {'form': InstituicaoForm(instance=inst)})

@login_required
def excluir_instituicao(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Instituicao, pk=p, professor=req.user).delete()
        return redirect('listar_instituicoes')
    return verificar_senha_e_executar(request, acao_excluir, pk)

# --- 2. TURMAS ---
@login_required
def criar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('listar_turmas')
    return render(request, 'academico/criar_turma.html', {'form': TurmaForm(user=request.user)})

@login_required
def listar_turmas(request):
    turmas = Turma.objects.filter(instituicao__professor=request.user).order_by('instituicao__nome', 'nome')
    return render(request, 'academico/listar_turmas.html', {'turmas': turmas})

@login_required
def detalhes_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk, instituicao__professor=request.user)
    return render(request, 'academico/detalhes_turma.html', {'turma': turma})

@login_required
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
def excluir_turma(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Turma, pk=p, instituicao__professor=req.user).delete()
        return redirect('listar_turmas')
    return verificar_senha_e_executar(request, acao_excluir, pk)

@login_required
@user_passes_test(eh_professor)
def remover_aluno_turma(request, aluno_id):
    aluno = get_object_or_404(Aluno, pk=aluno_id, turma__instituicao__professor=request.user)
    aluno.turma = None
    aluno.save()
    messages.success(request, f"Matrícula do aluno {aluno.user.username} removida com sucesso.")
    return redirect('listar_alunos_turma', turma_id=aluno.turma_id if aluno.turma else 1) # Ajuste aqui se necessário

# --- 3. ÁREAS DO CONHECIMENTO ---
@login_required
def criar_area(request):
    if request.method == 'POST':
        form = AreaConhecimentoForm(request.POST)
        if form.is_valid():
            area = form.save(commit=False)
            area.professor = request.user
            area.save()
            return redirect('listar_areas')
    return render(request, 'academico/criar_area.html', {'form': AreaConhecimentoForm()})

@login_required
def listar_areas(request):
    areas = AreaConhecimento.objects.filter(professor=request.user)
    return render(request, 'academico/lista_areas.html', {'areas': areas})

@login_required
def editar_area(request, pk):
    area = get_object_or_404(AreaConhecimento, pk=pk, professor=request.user)
    def acao_editar(req, p):
        form = AreaConhecimentoForm(req.POST, instance=area)
        if form.is_valid():
            form.save()
            return redirect('listar_areas')
        return render(req, 'academico/criar_area.html', {'form': form})
    if request.method == 'POST': return verificar_senha_e_executar(request, acao_editar, pk)
    return render(request, 'academico/criar_area.html', {'form': AreaConhecimentoForm(instance=area)})

@login_required
def excluir_area(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(AreaConhecimento, pk=p, professor=req.user).delete()
        return redirect('listar_areas')
    return verificar_senha_e_executar(request, acao_excluir, pk)

# --- 4. DISCIPLINAS ---
@login_required
def criar_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, user=request.user)
        if form.is_valid():
            d = form.save(commit=False)
            d.professor = request.user
            d.save()
            return redirect('listar_disciplinas')
    return render(request, 'academico/criar_disciplina.html', {'form': DisciplinaForm(user=request.user)})

@login_required
def listar_disciplinas(request):
    disciplinas = Disciplina.objects.filter(professor=request.user)
    return render(request, 'academico/lista_disciplinas.html', {'disciplinas': disciplinas})

@login_required
def detalhes_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk, professor=request.user)
    return render(request, 'academico/detalhes_disciplina.html', {'disciplina': disciplina})

@login_required
def editar_disciplina(request, pk):
    disc = get_object_or_404(Disciplina, pk=pk, professor=request.user)
    def acao_editar(req, p):
        form = DisciplinaForm(req.POST, instance=disc, user=req.user)
        if form.is_valid():
            form.save()
            return redirect('listar_disciplinas')
        return render(req, 'academico/criar_disciplina.html', {'form': form})
    if request.method == 'POST': return verificar_senha_e_executar(request, acao_editar, pk)
    return render(request, 'academico/criar_disciplina.html', {'form': DisciplinaForm(instance=disc, user=req.user)})

@login_required
def excluir_disciplina(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Disciplina, pk=p, professor=req.user).delete()
        return redirect('listar_disciplinas')
    return verificar_senha_e_executar(request, acao_excluir, pk)

# --- 5. AULAS ---
@login_required
def gerenciar_aulas(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id, professor=request.user)
    aulas = Aula.objects.filter(disciplina=disciplina)
    return render(request, 'academico/gerenciar_aulas.html', {
        'disciplina': disciplina, 'aulas': aulas
    })

# --- 6. ALUNO ---
@login_required
def ver_disciplinas_do_aluno(request):
    aluno = getattr(request.user, 'aluno', None)
    turma = aluno.turma if aluno else None
    disciplinas = turma.disciplinas.all() if turma else []
    return render(request, 'academico/disciplinas_aluno.html', {'disciplinas': disciplinas})

# --- 7. MATRÍCULAS ---
@login_required
@user_passes_test(eh_professor)
def listar_alunos_turma(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id, instituicao__professor=request.user)
    alunos = Aluno.objects.filter(turma=turma)
    return render(request, 'academico/listar_alunos_turma.html', {'turma': turma, 'alunos': alunos})

@login_required
def matricular_aluno(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    aluno, created = Aluno.objects.get_or_create(user=request.user)
    aluno.turma = turma
    aluno.save()
    messages.success(request, f"Matrícula realizada na turma: {turma.nome}!")
    return redirect('ver_disciplinas_aluno')

# --- 8. MATRÍCULA MANUAL (Adicionar ao views.py) ---
@login_required
def matricular_aluno_manual(request):
    if request.method == 'POST':
        turma_id = request.POST.get('turma_id')
        try:
            turma = Turma.objects.get(pk=turma_id)
            aluno, created = Aluno.objects.get_or_create(user=request.user)
            aluno.turma = turma
            aluno.save()
            messages.success(request, f"Matrícula realizada na turma: {turma.nome}!")
        except Turma.DoesNotExist:
            messages.error(request, "Turma não encontrada. Verifique o ID.")
    return redirect('ver_disciplinas_aluno')