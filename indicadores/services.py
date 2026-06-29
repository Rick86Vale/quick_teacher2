from django.db.models import Count
from academico.models import Turma, Disciplina, Aluno
from django.contrib.auth import get_user_model

User = get_user_model()

def get_dashboard_indicadores():
    # Filtra apenas os usuários que são PROFESSORES
    professores = User.objects.filter(tipo_usuario='PROFESSOR').annotate(
        num_disciplinas=Count('disciplina', distinct=True)
    )
    
    for prof in professores:
        total_turmas = Turma.objects.filter(instituicao__professor=prof).count()
        prof.total_turmas_impactadas = total_turmas
        
        total_alunos = Turma.objects.filter(instituicao__professor=prof).aggregate(
            total=Count('alunos_na_turma')
        )['total'] or 0
        prof.total_alunos_impactados = total_alunos

    return {
        'professores': professores,
        'total_professores_geral': User.objects.filter(tipo_usuario='PROFESSOR').count(), # Nova contagem
        'total_disciplinas_geral': Disciplina.objects.count(),
        'total_alunos_geral': Aluno.objects.count(),
        'total_turmas_geral': Turma.objects.count(),
    }


def get_dashboard_data():
    """Retorna um dicionário com todos os indicadores."""
    return {
        'total_disciplinas': Disciplina.objects.count(),
        'total_alunos': Aluno.objects.count(),
        # E aqui também usamos o related_name correto
        'turmas_com_alunos': Turma.objects.annotate(n_alunos=Count('alunos_na_turma')),
    }