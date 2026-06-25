# Path: academico/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import AreaConhecimento, Disciplina, Aula

# 1. Index: Catálogo geral de áreas e disciplinas órfãs
def index(request):
    areas = AreaConhecimento.objects.all()
    orfas = Disciplina.objects.filter(area__isnull=True)

    return render(request, 'academico/index.html', {
        'areas': areas,
        'orfas': orfas
    })

# 2. Listagem de Disciplinas do Professor Logado
@login_required
def listar_disciplinas(request):
    # Se for superuser, vê tudo; caso contrário, apenas as suas disciplinas
    if request.user.is_superuser:
        disciplinas = Disciplina.objects.all()
    else:
        disciplinas = Disciplina.objects.filter(professor=request.user)
    
    return render(request, 'academico/lista_disciplinas.html', {'disciplinas': disciplinas})

# 3. Gerenciamento de Aulas por Disciplina
@login_required
def gerenciar_aulas(request, disciplina_id):
    # Busca a disciplina garantindo que ela pertença ao professor
    disciplina = get_object_or_404(Disciplina, id=disciplina_id, professor=request.user)
    
    # Busca as aulas de forma explícita pelo modelo Aula
    aulas = Aula.objects.filter(disciplina=disciplina)
    
    return render(request, 'academico/gerenciar_aulas.html', {
        'disciplina': disciplina,
        'aulas': aulas
    })