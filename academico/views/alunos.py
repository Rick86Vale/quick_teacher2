from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from academico.models import Aluno, Turma
from usuarios.views import eh_professor

def eh_professor_ou_admin(user):
    return user.is_authenticated and (user.is_staff or eh_professor(user))

@login_required
@user_passes_test(eh_professor_ou_admin)
def listar_alunos_professor(request):
    user = request.user
    
    if user.is_staff or getattr(user, 'tipo_usuario', None) == 'ADMIN':
        # Admin vê todos os alunos do sistema
        alunos = Aluno.objects.all().distinct().order_by('user__first_name', 'user__username')
    else:
        # Professor vê apenas os alunos matriculados nas turmas cuja instituição ou disciplina ele gerencia,
        # ou se a turma estiver vinculada diretamente a ele (ajuste conforme seu modelo Turma/Instituição).
        # Considerando que a Turma está ligada à Instituição e a Instituição tem um professor:
        turmas_do_professor = Turma.objects.filter(instituicao__professor=user)
        
        # Busca todos os alunos dessas turmas sem duplicar registros
        alunos = Aluno.objects.filter(turmas__in=turmas_do_professor).distinct().order_by('user__first_name', 'user__username')

    return render(request, 'academico/alunos/listar_alunos.html', {'alunos': alunos})