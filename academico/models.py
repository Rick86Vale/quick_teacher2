# Path: academico/models.py

import datetime
from django.db import models
from usuarios.models import CustomUser

# 1. Área de Conhecimento: Define grandes temas para categorizar disciplinas
class AreaConhecimento(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Área do Conhecimento")

    def __str__(self):
        return self.nome

# 2. Disciplina: Contém o conteúdo e está vinculada a uma área e a um professor responsável
class Disciplina(models.Model):
    # O campo 'codigo' agora é gerado automaticamente e opcional na edição manual
    codigo = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        verbose_name="Código da Disciplina",
        help_text="Gerado automaticamente (ex: LOG2026001)"
    )
    nome = models.CharField(max_length=200, verbose_name="Disciplina")
    area = models.ForeignKey(
        AreaConhecimento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='disciplinas',
        verbose_name="Área do Conhecimento"
    )
    professor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo_usuario': 'PROFESSOR'},
        verbose_name="Professor Responsável"
    )

    def save(self, *args, **kwargs):
        # Gera o código automaticamente se ainda não existir
        if not self.codigo:
            ano = datetime.datetime.now().year
            # Pega as primeiras letras de cada palavra (até 3 palavras)
            palavras = self.nome.split()
            prefixo = "".join([p[0].upper() for p in palavras[:3]])
            
            # Busca a última disciplina que começa com esse prefixo no ano atual
            ultimo = Disciplina.objects.filter(codigo__startswith=f"{prefixo}{ano}").last()
            
            if ultimo:
                # Extrai os 3 últimos dígitos e incrementa
                sequencial = int(ultimo.codigo[-3:]) + 1
            else:
                sequencial = 1
            
            # Formata: ABC2026001
            self.codigo = f"{prefixo}{ano}{sequencial:03d}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

# 3. Aula: A unidade fundamental de conteúdo vinculada a uma disciplina específica
class Aula(models.Model):
    disciplina = models.ForeignKey(
        Disciplina, 
        on_delete=models.CASCADE, 
        related_name='aulas',
        verbose_name="Disciplina"
    )
    titulo = models.CharField(max_length=200, verbose_name="Título da Aula")
    conteudo = models.TextField(verbose_name="Conteúdo da Aula")
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    ordem = models.PositiveIntegerField(default=1, verbose_name="Ordem da Aula")

    class Meta:
        ordering = ['ordem']

    def __str__(self):
        return f"{self.ordem} - {self.titulo} ({self.disciplina.nome})"