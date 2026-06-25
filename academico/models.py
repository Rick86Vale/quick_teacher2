# Path: academico/models.py

import datetime
from django.db import models
from usuarios.models import CustomUser

# 1. Instituição: A raiz do sistema
class Instituicao(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Instituição")
    professor = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo_usuario': 'PROFESSOR'},
        verbose_name="Professor Responsável"
    )

    def __str__(self):
        return self.nome

# 2. Área de Conhecimento
class AreaConhecimento(models.Model):
    nome = models.CharField(max_length=100, unique=True, verbose_name="Área do Conhecimento")

    def __str__(self):
        return self.nome

# 3. Disciplina
class Disciplina(models.Model):
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
        if not self.codigo:
            ano = datetime.datetime.now().year
            palavras = self.nome.split()
            prefixo = "".join([p[0].upper() for p in palavras[:3]])
            ultimo = Disciplina.objects.filter(codigo__startswith=f"{prefixo}{ano}").last()
            sequencial = int(ultimo.codigo[-3:]) + 1 if ultimo else 1
            self.codigo = f"{prefixo}{ano}{sequencial:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

# 4. Turma: Vinculada à Instituição e possui M2M com Disciplina
class Turma(models.Model):
    instituicao = models.ForeignKey(
        Instituicao, 
        on_delete=models.CASCADE, 
        related_name='turmas',
        verbose_name="Instituição"
    )
    nome = models.CharField(max_length=100, verbose_name="Nome da Turma")
    ano = models.PositiveIntegerField(default=datetime.datetime.now().year)
    disciplinas = models.ManyToManyField(
        Disciplina, 
        related_name='turmas', 
        blank=True,
        verbose_name="Disciplinas vinculadas"
    )

    def __str__(self):
        return f"{self.nome} - {self.ano} ({self.instituicao.nome})"

# 5. Aula
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
    

# 6. Convite para criar conta professor
class Convite(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=[('PROFESSOR', 'Professor'), ('ALUNO', 'Aluno')])
    usado = models.BooleanField(default=False)