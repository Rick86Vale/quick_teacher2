# Path: academico/forms.py
from django import forms
from .models import (
    Turma, Instituicao, Disciplina, AreaConhecimento, Aula, 
    Video, PDF, LinkUtil, Tutorial, Evento  # Adicionei Evento aqui
)
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
            self.fields['disciplinas'].queryset = Disciplina.objects.filter(professor=user)
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
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['area'].queryset = AreaConhecimento.objects.filter(professor=user)

# --- 5. AULAS ---
class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['titulo', 'conteudo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'style': 'width: 100%; padding: 10px;'}),
            'conteudo': forms.Textarea(attrs={'class': 'form-control', 'style': 'width: 100%; height: 400px; font-family: monospace;', 'placeholder': 'Escreva o conteúdo da aula em Markdown...'}),
        }

# --- 6. EVENTOS (AGENDA) ---
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['titulo', 'data', 'descricao']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# --- FORMSETS ---
VideoFormSet = inlineformset_factory(Aula, Video, fields=('titulo', 'url', 'thumbnail_url'), extra=1, can_delete=True)
PDFFormSet = inlineformset_factory(Aula, PDF, fields=('titulo', 'link'), extra=1, can_delete=True)
LinkUtilFormSet = inlineformset_factory(Aula, LinkUtil, fields=('titulo', 'url'), extra=1, can_delete=True)

# --- TUTORIAIS ---
from django import forms
from .models import Tutorial, Turma

class TutorialForm(forms.ModelForm):
    class Meta:
        model = Tutorial
        fields = ['titulo', 'descricao', 'turmas', 'imagem', 'imagem_url', 'publicado']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'turmas': forms.CheckboxSelectMultiple(),  # Exibe em formato de caixas de seleção (checkboxes)
            'imagem_url': forms.URLInput(attrs={'class': 'form-control'}),
            'publicado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None) # Recebe o usuário logado opcionalmente
        super().__init__(*args, **kwargs)
        if user and not user.is_staff:
            # Filtra as turmas para que o professor selecione apenas as turmas associadas à instituição dele 
            # ou às disciplinas lecionadas por ele (ajuste conforme a regra de turmas do seu projeto)
            self.fields['turmas'].queryset = Turma.objects.filter(instituicao__professor=user).distinct()