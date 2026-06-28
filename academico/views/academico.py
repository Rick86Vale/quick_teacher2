# Path: academico/views/academico.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from ..models import AreaConhecimento, Disciplina, Turma, Instituicao, Aluno
from ..forms import TurmaForm, InstituicaoForm, DisciplinaForm, AreaConhecimentoForm
from usuarios.views import eh_professor
from itertools import groupby

# --- 0. UTILS ---
def verificar_senha_e_executar(request, acao_func, pk=None):
    """Função utilitária para exigir senha antes de ações destrutivas."""
    if request.method == 'POST':
        senha = request.POST.get('password_confirm')
        if request.user.check_password(senha):
            return acao_func(request, pk)
        else:
            messages.error(request, "Senha incorreta. Ação cancelada.")
    return render(request, 'academico/confirmar_senha.html', {'pk': pk})

# --- 1. INDEX ---
def index(request):
    areas = AreaConhecimento.objects.all()
    orfas = Disciplina.objects.filter(area__isnull=True)
    return render(request, 'academico/index.html', {'areas': areas, 'orfas': orfas})

# --- 2. INSTITUIÇÕES ---
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

# --- 3. TURMAS ---
@login_required
def criar_turma(request):
    if request.method == 'POST':
        form = TurmaForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('listar_turmas')
    return render(request, 'academico/turmas/criar_turma.html', {'form': TurmaForm(user=request.user)})

@login_required
def listar_turmas(request):
    turmas = Turma.objects.filter(instituicao__professor=request.user).order_by('instituicao__nome', 'nome')
    return render(request, 'academico/turmas/listar_turmas.html', {'turmas': turmas})

@login_required
def detalhes_turma(request, pk):
    turma = get_object_or_404(Turma, pk=pk, instituicao__professor=request.user)
    return render(request, 'academico/turmas/detalhes_turma.html', {'turma': turma})

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
    return render(request, 'academico/turmas/criar_turma.html', {'form': form})

@login_required
def excluir_turma(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Turma, pk=p, instituicao__professor=req.user).delete()
        return redirect('listar_turmas')
    return verificar_senha_e_executar(request, acao_excluir, pk)

@login_required
@user_passes_test(eh_professor)
def remover_aluno_turma(request, aluno_id):
    # Nota: Lógica mantida caso você utilize ForeignKey simples, adapte conforme migração para M2M
    aluno = get_object_or_404(Aluno, pk=aluno_id, turmas__instituicao__professor=request.user)
    aluno.turma = None
    aluno.save()
    messages.success(request, f"Matrícula do aluno {aluno.user.username} removida com sucesso.")
    return redirect('listar_alunos_turma', turma_id=aluno.turma_id if aluno.turma else 1)

# --- 4. ÁREAS DO CONHECIMENTO ---
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

# --- 5. DISCIPLINAS ---
@login_required
def criar_disciplina(request):
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, user=request.user)
        if form.is_valid():
            d = form.save(commit=False)
            d.professor = request.user
            d.save()
            return redirect('listar_disciplinas')
    return render(request, 'academico/disciplinas/criar_disciplina.html', {'form': DisciplinaForm(user=request.user)})



def listar_disciplinas(request):
    # Busca as disciplinas ordenadas por área para o groupby funcionar
    disciplinas = Disciplina.objects.filter(professor=request.user).order_by('area__nome')
    
    # Agrupa no Python ou use um dicionário manual
    disciplinas_por_area = {}
    for d in disciplinas:
        nome_area = d.area.nome if d.area else "Sem Área Definida"
        if nome_area not in disciplinas_por_area:
            disciplinas_por_area[nome_area] = []
        disciplinas_por_area[nome_area].append(d)
        
    return render(request, 'academico/disciplinas/lista_disciplinas.html', {
        'disciplinas_por_area': disciplinas_por_area
    })

@login_required
def detalhes_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    # Define se o usuário atual é o professor
    e_autor = (request.user == disciplina.professor or request.user.is_staff)
    
    # Verifica se é aluno matriculado (apenas para garantir segurança)
    e_aluno = Aluno.objects.filter(user=request.user, turmas__disciplinas=disciplina).exists()
    
    if not e_autor and not e_aluno:
        raise PermissionDenied("Você não tem acesso a esta disciplina.")

    return render(request, 'academico/disciplinas/detalhes_disciplina.html', {
        'disciplina': disciplina,
        'e_autor': e_autor
    })


@login_required
def editar_disciplina(request, pk):
    disc = get_object_or_404(Disciplina, pk=pk, professor=request.user)
    def acao_editar(req, p):
        form = DisciplinaForm(req.POST, instance=disc, user=req.user)
        if form.is_valid():
            form.save()
            return redirect('listar_disciplinas')
        return render(req, 'academico/disciplinas/criar_disciplina.html', {'form': form})
    
    if request.method == 'POST': 
        return verificar_senha_e_executar(request, acao_editar, pk)
        
    return render(request, 'academico/disciplinas/criar_disciplina.html', {'form': DisciplinaForm(instance=disc, user=request.user)})

@login_required
def excluir_disciplina(request, pk):
    def acao_excluir(req, p):
        get_object_or_404(Disciplina, pk=p, professor=req.user).delete()
        return redirect('listar_disciplinas')
    return verificar_senha_e_executar(request, acao_excluir, pk)