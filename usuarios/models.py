# Path: usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado estendendo AbstractUser.
    """
    # 1. Definimos as opções de papel (roles) do usuário
    TIPOS_USUARIO = (
        ('ALUNO', 'Aluno'),
        ('PROFESSOR', 'Professor'),
    )

    # 2. Adicionamos o campo para salvar essa escolha
    tipo_usuario = models.CharField(
        max_length=10, 
        choices=TIPOS_USUARIO, 
        default='ALUNO',
        verbose_name="Tipo de Usuário"
    )

    def __str__(self):
        return f"{self.username} ({self.tipo_usuario})"