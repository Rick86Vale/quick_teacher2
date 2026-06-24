# Path: academico/models.py

from django.db import models

class AreaConhecimento(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Área do Conhecimento")

    def __str__(self):
        return self.nome

class Disciplina(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Disciplina")
    # blank=True e null=True tornam o campo opcional
    area = models.ForeignKey(
        AreaConhecimento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='disciplinas',
        verbose_name="Área do Conhecimento"
    )

    def __str__(self):
        return self.nome