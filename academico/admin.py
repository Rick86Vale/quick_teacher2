# Path: academico/admin.py

from django.contrib import admin
from .models import AreaConhecimento, Disciplina

admin.site.register(AreaConhecimento)
admin.site.register(Disciplina)