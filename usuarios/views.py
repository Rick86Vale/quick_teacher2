# Path: usuarios/views.py

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.views.generic.base import TemplateView
from .forms import AlunoRegistrationForm
from .models import CustomUser
from academico.models import AreaConhecimento, Disciplina

# 1. View de Registro
class AlunoRegisterView(CreateView):
    form_class = AlunoRegistrationForm
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('registro_sucesso')

    def form_valid(self, form):
        self.request.session['novo_aluno_id'] = form.save().id
        return super().form_valid(form)

# 2. View de Sucesso
class RegistroSucessoView(TemplateView):
    template_name = 'usuarios/registro_sucesso.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        aluno_id = self.request.session.get('novo_aluno_id')
        context['aluno'] = CustomUser.objects.get(id=aluno_id)
        return context

# 3. View de Login Customizada (Redirecionamento Inteligente)
class CustomLoginView(LoginView):
    template_name = 'usuarios/login.html'

    def get_success_url(self):
        if self.request.user.tipo_usuario == 'PROFESSOR':
            return reverse_lazy('dashboard_professor')
        return reverse_lazy('dashboard')

# 4. Verificadores de Perfil
def eh_aluno(user):
    return user.is_authenticated and user.tipo_usuario == 'ALUNO'

def eh_professor(user):
    return user.is_authenticated and user.tipo_usuario == 'PROFESSOR'

# 5. Dashboards
@user_passes_test(eh_aluno, login_url='login')
def dashboard_aluno(request):
    areas = AreaConhecimento.objects.all()
    orfas = Disciplina.objects.filter(area__isnull=True)
    return render(request, 'usuarios/dashboard.html', {'areas': areas, 'orfas': orfas})

@user_passes_test(eh_professor, login_url='login')
def dashboard_professor(request):
    return render(request, 'usuarios/dashboard_professor.html')