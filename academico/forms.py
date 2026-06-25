# Path: academico/forms.py
from django import forms
from .models import Turma, Instituicao, Disciplina

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['instituicao', 'nome', 'ano', 'disciplinas']
        widgets = {'disciplinas': forms.CheckboxSelectMultiple()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['instituicao'].queryset = Instituicao.objects.filter(professor=user)

class InstituicaoForm(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = ['nome']

#  CRUD DE DISCIPLINAS
class DisciplinaForm(forms.ModelForm):
    class Meta:
        model = Disciplina
        # Removemos 'codigo' dos fields pois ele é gerado automaticamente
        fields = ['nome', 'area', 'descricao']