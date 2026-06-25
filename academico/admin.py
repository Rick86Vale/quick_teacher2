# Path: academico/admin.py

from django.contrib import admin
from .models import AreaConhecimento, Disciplina, Aula

class AulaInline(admin.TabularInline):
    model = Aula
    extra = 1

@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    # 'codigo' adicionado e colocado como readonly para ninguém alterar manualmente
    list_display = ('codigo', 'nome', 'professor', 'area')
    readonly_fields = ('codigo',) 
    search_fields = ('codigo', 'nome')
    inlines = [AulaInline]

@admin.register(AreaConhecimento)
class AreaConhecimentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)

@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'disciplina', 'ordem')
    list_filter = ('disciplina',)