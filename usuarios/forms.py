# Path: usuarios/forms.py

from django.core.exceptions import ValidationError
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
import random
import datetime

class AlunoRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True, label="Nome")
    last_name = forms.CharField(max_length=150, required=True, label="Sobrenome")

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        # Lógica de geração com verificação de unicidade
        while True:
            nome_completo = (user.first_name + user.last_name).upper()
            letras = "".join([c for c in nome_completo if c.isalpha()])[:3]
            ano = str(datetime.date.today().year)
            aleatorio = str(random.randint(100, 999))
            nova_matricula = f"{letras}{ano}{aleatorio}"
            
            # Verifica se já existe alguém com essa matrícula no banco
            if not CustomUser.objects.filter(username=nova_matricula).exists():
                user.username = nova_matricula
                break
            # Se já existir, o loop "while" gera um novo número e tenta novamente

        if commit:
            user.save()
        return user