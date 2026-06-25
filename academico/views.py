# Path: academico/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from usuarios.views import eh_professor
from .models import AreaConhecimento, Disciplina, Aula, Turma, Instituicao
from .forms import TurmaForm, InstituicaoForm, DisciplinaForm, AreaConhecimentoForm

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
# 1.1 Criar
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

# 1.2 Listar
@login_required
def listar_instituicoes(request):
    instituicoes = Instituicao.objects.filter(professor=request.user)
    return render(request, 'academico/listar_instituicoes.html', {'instituicoes': instituicoes})

# 1.4 Editar
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

# 1.5 Excluir
@login_required
def excluir_instituicao(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Instituicao, pk=p, professor=req.user).delete()
        return redirect('listar_instituicoes')
    return verificar_senha_e_executar(request, acao_excluir, pk)

# --- 2. TURMAS ---
# 2.1 Criar
@login_required
def criar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('listar_turmas')
    return render(request, 'academico/criar_turma.html', {'form': TurmaForm(user=request.user)})

# 2.2 Listar
@login_required
def listar_turmas(request):
    turmas = Turma.objects.filter(instituicao__professor=request.user).order_by('instituicao__nome', 'nome')
    return render(request, 'academico/listar_turmas.html', {'turmas': turmas})

# 2.3 Detalhes
@login_required
def detalhes_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk, instituicao__professor=request.user)
    return render(request, 'academico/detalhes_turma.html', {'turma': turma})

# 2.4 Editar
@login_required
def editar_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk, instituicao__professor=request.user)
    if request.method == 'POST':
        # Passar a instância no primeiro argumento é fundamental
        form = TurmaForm(request.POST, instance=turma, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('listar_turmas')
    else:
        form = TurmaForm(instance=turma, user=request.user)
    
    return render(request, 'academico/criar_turma.html', {'form': form})

# 2.5 Excluir
@login_required
def excluir_turma(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Turma, pk=p, instituicao__professor=req.user).delete()
        return redirect('listar_turmas')
    return verificar_senha_e_executar(request, acao_excluir, pk)

# --- 3. ÁREAS DO CONHECIMENTO ---
# 3.1 Criar
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

# 3.2 Listar
@login_required
def listar_areas(request):
    areas = AreaConhecimento.objects.filter(professor=request.user)
    return render(request, 'academico/lista_areas.html', {'areas': areas})

# 3.4 Editar
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

# 3.5 Excluir
@login_required
def excluir_area(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(AreaConhecimento, pk=p, professor=req.user).delete()
        return redirect('listar_areas')
    return verificar_senha_e_executar(request, acao_excluir, pk)

# --- 4. DISCIPLINAS ---
# 4.1 Criar
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

# 4.2 Listar
@login_required
def listar_disciplinas(request):
    disciplinas = Disciplina.objects.filter(professor=request.user)
    return render(request, 'academico/lista_disciplinas.html', {'disciplinas': disciplinas})

# 4.3 Detalhes
@login_required
def detalhes_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk, professor=request.user)
    return render(request, 'academico/detalhes_disciplina.html', {'disciplina': disciplina})

# 4.4 Editar
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
    return render(request, 'academico/criar_disciplina.html', {'form': DisciplinaForm(instance=disc, user=request.user)})

# 4.5 Excluir
@login_required
def excluir_disciplina(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Disciplina, pk=p, professor=req.user).delete()
        return redirect('listar_disciplinas')
    return verificar_senha_e_executar(request, acao_excluir, pk)

# --- 5. AULAS ---
# 5.1 Gerenciar
@login_required
def gerenciar_aulas(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, id=disciplina_id, professor=request.user)
    aulas = Aula.objects.filter(disciplina=disciplina)
    return render(request, 'academico/gerenciar_aulas.html', {
        'disciplina': disciplina, 'aulas': aulas
    })

# --- 6. ALUNO ---
# Aqui você insere as novas views de vinculação e controle do aluno
@login_required
def vincular_aluno_turma(request, turma_id):
    # Lógica que você irá criar para vincular o request.user a uma turma
    pass

# 6.1 Disciplinas do Aluno
@login_required
def ver_disciplinas_do_aluno(request):
    # Assume que você criou um método para pegar o aluno logado
    aluno = request.user.aluno 
    turma = aluno.turma
    
    if turma:
        # O aluno acessa as disciplinas via relação many-to-many da turma
        disciplinas = turma.disciplinas.all()
    else:
        disciplinas = []
        
    return render(request, 'academico/disciplinas_aluno.html', {'disciplinas': disciplinas})