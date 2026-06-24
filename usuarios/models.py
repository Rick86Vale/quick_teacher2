# Path: usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado.
    """
    TIPO_USUARIO_CHOICES = (
        ('ADMIN', 'Administrador'),      # Para quem cuida do sistema
        ('PROFESSOR', 'Professor'),      # Para quem cria aulas/conteúdo
        ('ALUNO', 'Aluno'),              # Para quem consome aulas
    )

    tipo_usuario = models.CharField(
        max_length=20, 
        choices=TIPO_USUARIO_CHOICES, 
        default='ALUNO',
        verbose_name="Tipo de Usuário"
    )

    def __str__(self):
        return f"{self.username} - {self.get_tipo_usuario_display()}"