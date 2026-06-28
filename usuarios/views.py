# Path: usuarios/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from .forms import AlunoRegistrationForm, ProfessorRegistrationForm # Importando os dois
from .models import CustomUser
from academico.models import AreaConhecimento, Disciplina, Instituicao
from django.db.models import Count, Q


@login_required
def perfil_usuario(request):
    return render(request, 'usuarios/perfil.html', {'user': request.user})

# 1. Registro de Aluno
class AlunoRegisterView(CreateView):
    form_class = AlunoRegistrationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('registro_sucesso')

    def form_valid(self, form):
        self.request.session['novo_aluno_id'] = form.save().id
        return super().form_valid(form)

# 2. Registro de Professor
class ProfessorRegisterView(CreateView):
    form_class = ProfessorRegistrationForm
    template_name = 'usuarios/registro_professor.html'
    success_url = reverse_lazy('login')

# 3. View de Sucesso
class RegistroSucessoView(TemplateView):
    template_name = 'usuarios/registro_sucesso.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno_id = self.request.session.get('novo_aluno_id')
        context['aluno'] = CustomUser.objects.get(id=aluno_id)
        return context

# 4. Login Customizado
class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'

    def get_success_url(self):
        if self.request.user.tipo_usuario == 'PROFESSOR':
            return reverse_lazy('dashboard_professor')
        return reverse_lazy('dashboard')

# 5. Dashboards e Segurança
def eh_aluno(user):
    return user.is_authenticated and user.tipo_usuario == 'ALUNO'

def eh_professor(user):
    return user.is_authenticated and user.tipo_usuario == 'PROFESSOR'

@user_passes_test(eh_aluno, login_url='login')
def dashboard_aluno(request):
    areas = AreaConhecimento.objects.all()
    orfas = Disciplina.objects.filter(area__isnull=True)
    return render(request, 'usuarios/dashboard.html', {'areas': areas, 'orfas': orfas})

@user_passes_test(eh_professor, login_url='login')
def dashboard_professor(request):
    return render(request, 'usuarios/dashboard_professor.html')


from django.db.models import Count, Q

@login_required
def dashboard_professor(request):
    instituicoes = Instituicao.objects.filter(professor=request.user).prefetch_related(
        'turmas__disciplinas__aulas',
        'turmas__turmas' # <--- Corrigido de 'turmas__alunos' para 'turmas__turmas'
    )
    return render(request, 'usuarios/dashboard_professor.html', {
        'instituicoes': instituicoes
    })


