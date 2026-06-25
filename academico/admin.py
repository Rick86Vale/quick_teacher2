# Path: academico/admin.py

from django.contrib import admin
from .models import AreaConhecimento, Disciplina, Aula, Turma, Instituicao

# 1. Registro da Instituição
@admin.register(Instituicao)
class InstituicaoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'professor')
    search_fields = ('nome',)

# 2. Inlines para facilitar a edição hierárquica
class AulaInline(admin.TabularInline):
    model = Aula
    extra = 1

# 3. Disciplina
@admin.register(Disciplina)
class DisciplinaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'professor', 'area')
    readonly_fields = ('codigo',) 
    search_fields = ('codigo', 'nome')
    inlines = [AulaInline]

# 4. Área de Conhecimento
@admin.register(AreaConhecimento)
class AreaConhecimentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)

# 5. Aula
@admin.register(Aula)
class AulaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'disciplina', 'ordem')
    list_filter = ('disciplina',)

# 6. Turma
@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ano', 'get_professor', 'instituicao')
    list_filter = ('instituicao', 'ano') # Filtro lateral útil
    filter_horizontal = ('disciplinas',)

    # Método para exibir o professor da instituição na listagem da turma
    def get_professor(self, obj):
        return obj.instituicao.professor
    
    get_professor.short_description = 'Professor'