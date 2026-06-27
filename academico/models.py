# Path: academico/models.py
import datetime
import random
import string
from django.db import models
from django.contrib.auth import get_user_model


# Obtém o modelo de usuário configurado no projeto
User = get_user_model()

# 1. Área de Conhecimento
class AreaConhecimento(models.Model):
    nome = models.CharField(max_length=100)
    professor = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.nome

# 2. Instituição: A raiz do sistema
class Instituicao(models.Model):
    nome = models.CharField(max_length=200, verbose_name="Nome da Instituição")
    professor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo_usuario': 'PROFESSOR'},
        verbose_name="Professor Responsável"
    )

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
    descricao = models.TextField(verbose_name="Descrição", blank=True, null=True)
    
    area = models.ForeignKey(
        AreaConhecimento, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='disciplinas',
        verbose_name="Área do Conhecimento"
    )
    
    professor = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        limit_choices_to={'tipo_usuario': 'PROFESSOR'},
        verbose_name="Professor Responsável"
    )

    def save(self, *args, **kwargs):
        if not self.codigo:
            ano = datetime.datetime.now().year
            palavras = self.nome.split()
            # Gera prefixo de 3 letras com base no nome, preenche com 'X' se necessário
            prefixo = "".join([p[0].upper() for p in palavras])[:3].ljust(3, 'X')
            
            # Busca o último registro para incrementar o sequencial
            ultimo = Disciplina.objects.filter(codigo__startswith=f"{prefixo}{ano}").order_by('codigo').last()
            
            sequencial = 1
            if ultimo:
                try:
                    sequencial = int(ultimo.codigo[-3:]) + 1
                except (ValueError, IndexError):
                    sequencial = 1
            
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

    codigo_convite = models.CharField(max_length=3, unique=True, editable=False, blank=True)

    def save(self, *args, **kwargs):
        if not self.codigo_convite:
            # Gera 3 caracteres (letras maiúsculas ou números)
            while True:
                novo_codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
                if not Turma.objects.filter(codigo_convite=novo_codigo).exists():
                    self.codigo_convite = novo_codigo
                    break
        super().save(*args, **kwargs)

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
        unique_together = ['disciplina', 'ordem']
    
    publicado = models.BooleanField(default=False, verbose_name="Publicado")

    def __str__(self):
        return f"{self.titulo} ({'Público' if self.publicado else 'Rascunho'})"
    
# 5.1 Recursos (Vídeos)
class Video(models.Model):
    aula = models.ForeignKey('Aula', related_name='videos', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True, help_text="Opcional: link da imagem da capa")

    def get_thumbnail(self):
        if self.thumbnail_url:
            return self.thumbnail_url
        # Lógica automática mantida
        video_id = self.url.split('v=')[-1].split('&')[0] if 'v=' in self.url else None
        return f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg" if video_id else ""
    
# 5.2 Recursos (PDF)
class PDF(models.Model):
    aula = models.ForeignKey('Aula', related_name='pdfs', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    link = models.URLField(help_text="Cole o link do PDF hospedado (Google Drive, Dropbox, etc.)")

    def __str__(self):
        return self.titulo

# 5.3 Recursos (Links Úteis)
class LinkUtil(models.Model):
    aula = models.ForeignKey('Aula', related_name='links_uteis', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    url = models.URLField()

    def __str__(self):
        return self.titulo
    

# 6. Convite
class Convite(models.Model):
    email = models.EmailField(unique=True)
    token = models.CharField(max_length=64, unique=True)
    tipo_usuario = models.CharField(max_length=20, choices=[('PROFESSOR', 'Professor'), ('ALUNO', 'Aluno')])
    usado = models.BooleanField(default=False)

# 7. Aluno
class Aluno(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    turma = models.ForeignKey(
        Turma, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='alunos'
    )

    def __str__(self):
        return self.user.username
    
