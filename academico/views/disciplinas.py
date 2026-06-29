import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

# Importações dos seus módulos locais
from ..models import Disciplina, Aula, Aluno
from ..forms import DisciplinaForm
from usuarios.views import eh_professor
from .academico import verificar_senha_e_executar

logger = logging.getLogger(__name__)

# --- Disciplinas ---

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
    disciplinas = Disciplina.objects.filter(professor=request.user).order_by('area__nome')
    disciplinas_por_area = {}
    for d in disciplinas:
        nome_area = d.area.nome if d.area else "Sem Área Definida"
        if nome_area not in disciplinas_por_area:
            disciplinas_por_area[nome_area] = []
        disciplinas_por_area[nome_area].append(d)
    return render(request, 'academico/disciplinas/lista_disciplinas.html', {'disciplinas_por_area': disciplinas_por_area})

@login_required
def detalhes_disciplina(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    e_autor = (request.user == disciplina.professor or request.user.is_staff)
    e_aluno = Aluno.objects.filter(user=request.user, turmas__disciplinas=disciplina).exists()
    
    if not e_autor and not e_aluno:
        raise PermissionDenied("Você não tem acesso a esta disciplina.")

    # Se for aluno, buscamos as aulas que ele marcou como lidas
    aulas_lidas_ids = []
    if e_aluno:
        # Import local ou no topo para evitar dependência circular
        from academico.models import AulaLida
        aluno = Aluno.objects.get(user=request.user)
        aulas_lidas_ids = AulaLida.objects.filter(aluno=aluno, aula__disciplina=disciplina).values_list('aula_id', flat=True)

    return render(request, 'academico/disciplinas/detalhes_disciplina.html', {
        'disciplina': disciplina,
        'e_autor': e_autor,
        'aulas_lidas_ids': aulas_lidas_ids # Passamos a lista de IDs para o template
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

# --- Importação/Exportação ---

@login_required
@user_passes_test(eh_professor)
def exportar_disciplina(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id, professor=request.user)
    data = {
        'disciplina': disciplina.nome,
        'descricao': disciplina.descricao,
        'aulas': list(disciplina.aulas.values('titulo', 'ordem', 'publicado', 'conteudo'))
    }
    response = HttpResponse(json.dumps(data, indent=4), content_type="application/json")
    response['Content-Disposition'] = f'attachment; filename="disciplina_{disciplina.codigo}.json"'
    return response

@login_required
@user_passes_test(eh_professor)
def importar_disciplina(request):
    if request.method == 'POST' and request.FILES.get('arquivo'):
        try:
            data = json.load(request.FILES['arquivo'])
            nova_disciplina = Disciplina.objects.create(
                nome=data.get('disciplina', 'Disciplina Importada'),
                descricao=data.get('descricao', ''),
                professor=request.user
            )
            for aula_data in data.get('aulas', []):
                Aula.objects.create(disciplina=nova_disciplina, **aula_data)
            messages.success(request, "Disciplina importada com sucesso!")
        except Exception as e:
            messages.error(request, f"Erro na importação: {str(e)}")
    return redirect('listar_disciplinas')

