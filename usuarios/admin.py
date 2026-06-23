# Path: usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# 1. Registro no Painel Administrativo
admin.site.register(CustomUser, UserAdmin)