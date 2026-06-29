# Path: academico/views/aluno.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test 
from ..models import Aluno, Turma
from django.contrib import messages
from usuarios.views import eh_professor



@login_required
def listar_alunos_turma(request, turma_id):
    # Busca a turma com segurança e otimização
    turma = get_object_or_404(Turma, pk=turma_id, instituicao__professor=request.user)
    
    # Busca os alunos matriculados nesta turma
    alunos = Aluno.objects.filter(turmas=turma).select_related('user')
    
    # Busca as disciplinas vinculadas a esta turma
    disciplinas = turma.disciplinas.all()
    
    return render(request, 'academico/listar_alunos_turma.html', {
        'turma': turma, 
        'alunos': alunos,
        'disciplinas': disciplinas
    })

@login_required
def ver_disciplinas_do_aluno(request):
    # Tenta buscar o aluno, se não existir, evita o erro 404
    aluno, created = Aluno.objects.get_or_create(user=request.user)
    
    # Se o aluno acabou de ser criado (ex: primeiro acesso), 
    # ele ainda não terá turmas, então turmas será um QuerySet vazio.
    turmas = aluno.turmas.all() 
    
    return render(request, 'academico/disciplinas_aluno.html', {'turmas': turmas})

@login_required
def matricular_aluno(request, turma_id):
    turma = get_object_or_404(Turma, pk=turma_id)
    aluno, created = Aluno.objects.get_or_create(user=request.user)
    aluno.turma = turma
    aluno.save()
    messages.success(request, f"Matrícula realizada na turma: {turma.nome}!")
    return redirect('ver_disciplinas_aluno')

@login_required
def matricular_aluno_manual(request, turma_id=None):
    # Se o ID veio pela URL (link do professor), usamos ele
    if turma_id:
        turma = get_object_or_404(Turma, id=turma_id)
        aluno, created = Aluno.objects.get_or_create(user=request.user)
        aluno.turmas.add(turma)
        messages.success(request, f"Matrícula realizada na turma: {turma.nome}")
        return redirect('ver_disciplinas_aluno')
    
    # Se veio pelo formulário manual (POST)
    if request.method == 'POST':
        codigo = request.POST.get('turma_codigo', '').strip().upper()
        turma = Turma.objects.filter(codigo_convite=codigo).first()
        if turma:
            aluno, created = Aluno.objects.get_or_create(user=request.user)
            aluno.turmas.add(turma)
            messages.success(request, f"Matrícula realizada na turma: {turma.nome}")
        else:
            messages.error(request, "Código de turma não encontrado.")
            
    return redirect('ver_disciplinas_aluno')

@login_required
@user_passes_test(eh_professor)
def remover_aluno_turma(request, turma_id, aluno_id):
    turma = get_object_or_404(Turma, pk=turma_id, instituicao__professor=request.user)
    aluno = get_object_or_404(Aluno, pk=aluno_id)
    
    # Remove a turma do aluno (ManyToMany)
    if aluno.turmas.filter(pk=turma.pk).exists():
        aluno.turmas.remove(turma)
        
    return redirect('listar_alunos_turma', turma_id=turma.pk)