# Path: usuarios/context_processors.py

def user_role(request):
    """
    Adiciona variáveis de contexto para identificar o papel do usuário.
    """
    if request.user.is_authenticated:
        return {
            'is_admin': request.user.is_superuser or request.user.tipo_usuario == 'ADMIN',
            'is_professor': request.user.tipo_usuario == 'PROFESSOR',
            'is_aluno': request.user.tipo_usuario == 'ALUNO',
        }
    return {
        'is_admin': False, 
        'is_professor': False, 
        'is_aluno': False
    }