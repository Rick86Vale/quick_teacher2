from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    # Lógica para filtrar o que cada usuário vê
    context = {}
    
    # Se for professor, busca disciplinas
    if request.user.tipo_usuario == 'PROFESSOR':
        context['disciplinas'] = Disciplina.objects.filter(professor=request.user)
    
    # Se for aluno, busca disciplinas onde ele está matriculado
    elif request.user.tipo_usuario == 'ALUNO':
        context['disciplinas'] = Disciplina.objects.filter(alunos=request.user)
        
    return render(request, 'home.html', context)