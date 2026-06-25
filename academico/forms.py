# Path: academico/forms.py
from django import forms
from .models import Turma, Instituicao

class TurmaForm(forms.ModelForm):
    class Meta:
        model = Turma
        fields = ['instituicao', 'nome', 'ano', 'disciplinas']
        widgets = {'disciplinas': forms.CheckboxSelectMultiple()}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Filtra apenas as instituições do professor logado
            self.fields['instituicao'].queryset = Instituicao.objects.filter(professor=user)


class InstituicaoForm(forms.ModelForm):
    class Meta:
        model = Instituicao
        fields = ['nome']