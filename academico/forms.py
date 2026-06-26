# Path: academico/forms.py
from django import forms
from .models import Turma, Instituicao, Disciplina, AreaConhecimento, Aula
from django.forms import inlineformset_factory

# --- 1. TURMAS ---
class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['instituicao', 'nome', 'ano', 'disciplinas']
        widgets = {
            'disciplinas': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtra apenas as disciplinas que o professor logado criou
            self.fields['disciplinas'].queryset = Disciplina.objects.filter(professor=user)
            # Filtra também as instituições do professor
            self.fields['instituicao'].queryset = Instituicao.objects.filter(professor=user)

# --- 2. INSTITUIÇÕES ---
class InstituicaoForm(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = ['nome']

# --- 3. ÁREAS DO CONHECIMENTO ---
class AreaConhecimentoForm(forms.ModelForm):
    class Meta:
        model = AreaConhecimento
        fields = ['nome']

# --- 4. DISCIPLINAS ---
class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        fields = ['nome', 'area', 'descricao']

    def __init__(self, *args, **kwargs):
        # Capturamos o usuário para filtrar as áreas disponíveis
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Garante que o professor veja apenas as áreas que ele criou
            self.fields['area'].queryset = AreaConhecimento.objects.filter(professor=user)

# --- 5. AULAS ---
class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['titulo', 'conteudo'] # Ordem removida daqui
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 10px;'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 100%; height: 400px; font-family: monospace;', 'placeholder': 'Escreva o conteúdo da aula em Markdown...'}),
        }

