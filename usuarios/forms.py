# Path: usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import random
import datetime

# --- Formulário do Aluno (Mantém a lógica da matrícula automática) ---
class AlunoRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Nome")
    last_name = forms.CharField(max_length=150, required=True, label="Sobrenome")

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_usuario = 'ALUNO'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        while True:
            nome_completo = (user.first_name + user.last_name).upper()
            letras = "".join([c for c in nome_completo if c.isalpha()])[:3]
            ano = str(datetime.date.today().year)
            aleatorio = str(random.randint(100, 999))
            nova_matricula = f"{letras}{ano}{aleatorio}"
            
            if not CustomUser.objects.filter(username=nova_matricula).exists():
                user.username = nova_matricula
                break
        if commit:
            user.save()
        return user

# --- Novo Formulário do Professor (Username escolhido pelo usuário) ---
class ProfessorRegistrationForm(UserCreationForm):
    username = forms.CharField(label="Nome de Usuário (Login)")
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Nome")
    last_name = forms.CharField(max_length=150, required=True, label="Sobrenome")

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.tipo_usuario = 'PROFESSOR'
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.username = self.cleaned_data['username'] # Usa o que ele escolheu
        
        if commit:
            user.save()
        return user

