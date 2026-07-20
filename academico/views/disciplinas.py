import json, os
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.db import transaction
from django.urls import reverse
from django.conf import settings
from academico.forms import EventoForm

# Importações dos seus módulos locais
from ..models import Disciplina, Aula, Aluno, Turma, Aviso, Evento
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

@login_required
def listar_disciplinas(request):
    disciplinas = Disciplina.objects.filter(professor=request.user).order_by('area__nome')
    
    # Lista de cores oficiais da sua identidade visual
    cores_disponiveis = ['#16ac75', '#061c78', '#f92672', '#ae81ff']
    
    disciplinas_por_area = {}
    for d in disciplinas:
        # Atribui a cor fixa baseada no ID único (pk) da disciplina
        d.cor_final = cores_disponiveis[d.pk % len(cores_disponiveis)]
        
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
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    if request.method == 'POST':
        form = DisciplinaForm(request.POST, instance=disciplina)
        if form.is_valid():
            disciplina_salva = form.save()
            # Redireciona para o novo template de sucesso pós-edição
            return render(request, 'academico/disciplinas/disciplina_editada_detalhe.html', {
                'disciplina': disciplina_salva
            })
    else:
        form = DisciplinaForm(instance=disciplina)
    
    return render(request, 'academico/disciplinas/criar_disciplina.html', {'form': form})


@login_required
def excluir_disciplina(request, pk):
    # Use get_object_or_404 de forma segura. 
    # Se o seu modelo Disciplina usa 'professor=request.user', certifique-se de que o ID 28 pertence a ele.
    disciplina = get_object_or_404(Disciplina, pk=pk)
    
    def acao_excluir_e_baixar(req, p):
        data = {
            'disciplina': disciplina.nome,
            'codigo': disciplina.codigo,
            'descricao': disciplina.descricao,
            'aulas': list(disciplina.aulas.values('titulo', 'ordem', 'publicado', 'conteudo'))
        }
        
        response = HttpResponse(json.dumps(data, indent=4), content_type="application/json")
        response['Content-Disposition'] = f'attachment; filename="backup_{disciplina.codigo}.json"'
        
        disciplina.delete()
        response.set_cookie('download_backup_realizado', 'true', max_age=10)
        return response

    return verificar_senha_e_executar(request, acao_excluir_e_baixar, pk)

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

@login_required
@user_passes_test(eh_professor)
def progresso_aluno_individual(request, turma_id, aluno_id):
    from academico.models import Turma, Aluno, Aula, AulaLida, Disciplina
    
    turma = get_object_or_404(Turma, pk=turma_id, instituicao__professor=request.user)
    aluno = get_object_or_404(Aluno, pk=aluno_id, turmas=turma)
    
    disciplinas = turma.disciplinas.all()
    aulas = Aula.objects.filter(disciplina__in=disciplinas, publicado=True)
    total_aulas = aulas.count()
    
    # Busca quais dessas aulas o aluno já marcou como lidas
    aulas_lidas_ids = AulaLida.objects.filter(
        aluno=aluno, 
        aula__in=aulas
    ).values_list('aula_id', flat=True)
    
    progresso_por_disciplina = []
    for disc in disciplinas:
        aulas_disc = aulas.filter(disciplina=disc)
        total = aulas_disc.count()
        lidas = aulas_disc.filter(pk__in=aulas_lidas_ids).count()
        porcentagem = (lidas / total * 100) if total > 0 else 0
        
        progresso_por_disciplina.append({
            'disciplina': disc,
            'total': total,
            'lidas': lidas,
            'porcentagem': round(porcentagem, 1)
        })

    return render(request, 'academico/progresso_alunos.html', {
        'aluno': aluno,
        'turma': turma,
        'progresso_por_disciplina': progresso_por_disciplina,
        # Adicione isto para corrigir o erro:
        'disciplina': disciplinas.first() if disciplinas.exists() else None 
    })


# --- Quadro de Avisos
@login_required
def listar_avisos(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    
    # 1. Defina as permissões primeiro
    e_autor = (request.user == turma.instituicao.professor or request.user.is_staff)
    e_aluno = Aluno.objects.filter(user=request.user, turmas=turma).exists()
    
    if not e_autor and not e_aluno:
        raise PermissionDenied()

    # 2. Busque os dados
    avisos = Aviso.objects.filter(turma=turma).order_by('-fixado', '-data_criacao')
    eventos = Evento.objects.filter(turma=turma).order_by('data')
    
    # 3. Retorne tudo no contexto
    return render(request, 'academico/avisos.html', {
        'turma': turma,
        'avisos': avisos,
        'eventos': eventos, # Certifique-se que isso está aqui
        'e_autor': e_autor  # A variável que o template está cobrando
    })


@login_required
def criar_aviso(request, turma_pk):
    turma = get_object_or_404(Turma, pk=turma_pk)
    
    # Validação: Só o professor daquela turma (ou staff) pode criar
    e_autor = (request.user == turma.instituicao.professor or request.user.is_staff)
    
    if not e_autor:
        raise PermissionDenied("Apenas o professor desta turma pode criar avisos.")
    
    if request.method == 'POST':
        Aviso.objects.create(
            turma=turma,
            titulo=request.POST.get('titulo'),
            conteudo=request.POST.get('conteudo'),
            prioridade=request.POST.get('prioridade'),
            fixado=(request.POST.get('fixado') == 'on')
        )
        return redirect('listar_avisos', pk=turma.pk)
        
    return render(request, 'academico/form_aviso.html', {'turma': turma})

@login_required
@user_passes_test(eh_professor)
def editar_aviso(request, pk):
    aviso = get_object_or_404(Aviso, pk=pk)
    turma = aviso.turma
    
    if request.method == 'POST':
        # Atualiza os dados
        aviso.titulo = request.POST.get('titulo')
        aviso.conteudo = request.POST.get('conteudo')
        aviso.prioridade = request.POST.get('prioridade')
        aviso.fixado = (request.POST.get('fixado') == 'on')
        aviso.save()
        return redirect('listar_avisos', pk=turma.pk)
        
    return render(request, 'academico/form_aviso.html', {'aviso': aviso, 'turma': turma})

@login_required
def excluir_aviso(request, pk):
    # 1. Busca o aviso
    aviso = get_object_or_404(Aviso, pk=pk)
    turma = aviso.turma
    
    # 2. Validação de permissão (apenas o professor da turma pode excluir)
    # Ajuste 'eh_professor' para a sua função de permissão real
    e_autor = (request.user == turma.instituicao.professor or request.user.is_staff)
    
    if not e_autor:
        raise PermissionDenied("Você não tem permissão para excluir este aviso.")
    
    # 3. Processa a exclusão
    if request.method == 'POST':
        aviso.delete()
        return redirect('listar_avisos', pk=turma.pk)
    
    # 4. Renderiza uma página de confirmação (opcional, mas recomendado)
    return render(request, 'academico/confirmar_exclusao_aviso.html', {'aviso': aviso})

# Eventos (são mostrados no template de avisos - são as datas programadas para atividades e provas)
@login_required
@user_passes_test(eh_professor)
def criar_evento(request, turma_pk):
    turma = get_object_or_404(Turma, pk=turma_pk)
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            evento = form.save(commit=False)
            evento.turma = turma
            evento.save()
            return redirect('listar_avisos', pk=turma.pk)
    else:
        form = EventoForm()
    return render(request, 'academico/form_evento.html', {'form': form, 'turma': turma})

@login_required
@user_passes_test(eh_professor)
def editar_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    turma = evento.turma
    if request.method == 'POST':
        form = EventoForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            return redirect('listar_avisos', pk=turma.pk)
    else:
        form = EventoForm(instance=evento)
    return render(request, 'academico/form_evento.html', {'form': form, 'turma': turma, 'evento': evento})

@login_required
@user_passes_test(eh_professor)
def excluir_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    turma = evento.turma
    if request.method == 'POST':
        evento.delete()
        return redirect('listar_avisos', pk=turma.pk)
    return render(request, 'academico/confirmar_exclusao_evento.html', {'evento': evento, 'turma': turma})