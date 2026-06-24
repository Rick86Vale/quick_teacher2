# Path: academico/views.py
from django.shortcuts import render
from .models import AreaConhecimento, Disciplina # Importe os nomes corretos

def index(request):
    areas = AreaConhecimento.objects.all()
    orfas = Disciplina.objects.filter(area__isnull=True)

    return render(request, 'academico/index.html', {
        'areas': areas,
        'orfas': orfas
    })