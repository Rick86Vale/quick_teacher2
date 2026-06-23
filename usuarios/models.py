# Path: usuarios/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

# 1. Definição do Modelo Customizado
class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado que estende o AbstractUser do Django.
    """
    # Você pode adicionar campos extras aqui futuramente, ex:
    # telefone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.username