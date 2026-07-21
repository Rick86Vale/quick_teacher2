# Path: views/aulas.py

import json, os, io
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.db import transaction
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from academico.utils.gerador_slides import criar_apresentacao

# Seus modelos e formulários
from academico.models import Disciplina, Aula, Video, PDF, LinkUtil, Aluno, AulaLida

from ..forms import AulaForm, VideoFormSet, PDFFormSet, LinkUtilFormSet
from ..models import Disciplina, Aula, Video, PDF, LinkUtil, Aluno, AulaLida, ComentarioContextual

# Configuração de Logger
logger = logging.getLogger(__name__)

# --- GESTÃO DE AULAS
# 1. Listagem de Aulas
@login_required
def gerenciar_aulas(request, disciplina_id):
    # Fluxo estrito do PROFESSOR
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    # A lógica aqui pode ser focada apenas em EDITAR/CRIAR
    aulas = Aula.objects.filter(disciplina=disciplina).order_by('ordem')
    return render(request, 'academico/aulas/gerenciar_aulas.html', {'disciplina': disciplina, 'aulas': aulas})


# 2. Criação de Aula
@login_required
def criar_aula(request, disciplina_id):
    disciplina = get_object_or_404(Disciplina, pk=disciplina_id)
    if not (request.user == disciplina.professor or request.user.is_staff):
        raise PermissionDenied("Acesso negado.")
    
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            aula = form.save(commit=False)
            aula.disciplina = disciplina
            aula.ordem = Aula.objects.filter(disciplina=disciplina).count() + 1
            aula.save()
            # Em criar_aula, após salvar a aula:
            return redirect('menu_recursos', aula_id=aula.pk)
    else:
        form = AulaForm()
    return render(request, 'academico/aulas/criar_aula.html', {'form': form, 'disciplina': disciplina})

# 3. Excluir Aula
@login_required
def excluir_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    # Opcional: checar se o usuário é o professor da disciplina
    disciplina_id = aula.disciplina.id
    aula.delete()
    return redirect('gerenciar_aulas', disciplina_id=disciplina_id)

# 4. Edição de Aula
@login_required
def editar_aula(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    
    # Validação de permissão
    if not (request.user == aula.disciplina.professor or request.user.is_staff):
        raise PermissionDenied("Sem permissão.")

    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        
        # DEBUG: O print abaixo mostrará no terminal se o Django está recebendo o conteúdo
        # print(f"Dados recebidos no POST: {request.POST.get('conteudo')}")
        
        if form.is_valid():
            form.save()
            return redirect('visualizar_aula', aula_id=aula.pk)
        else:
            # DEBUG: Se houver erro de validação, ele aparecerá no seu terminal
            print(f"Erros no formulário: {form.errors}")
            # Você pode enviar os erros para o template para depurar
            return render(request, 'academico/aulas/editar_aula.html', {
                'form': form, 
                'aula': aula,
                'erros': form.errors # Adicione isso no template para ver o erro na tela
            })
    else:
        form = AulaForm(instance=aula)
    
    return render(request, 'academico/aulas/editar_aula.html', {'form': form, 'aula': aula})


#4.1 - Inserir imagem na aula
@csrf_exempt # Necessário se o form estiver fora do contexto padrão
def upload_imagem_ajax(request):
    if request.method == 'POST' and request.FILES.get('image'):
        file = request.FILES['image']
        # Salva o arquivo no caminho media/aulas/nome_do_arquivo
        save_path = default_storage.save(os.path.join('aulas', file.name), file)
        # Retorna a URL pública da imagem
        image_url = default_storage.url(save_path)
        return JsonResponse({'url': image_url})
    return JsonResponse({'error': 'Falha no upload'}, status=400)

# 5. Visualizar Aula
def visualizar_aula(request, aula_id):
    # Busca a aula pelo ID
    aula = get_object_or_404(Aula, pk=aula_id)
    
    # Define se o usuário tem permissão de autor ou staff
    e_autor = (request.user == aula.disciplina.professor or request.user.is_staff)
    
    # Verifica a permissão de visualização (se não publicado e não for autor)
    if not aula.publicado and not e_autor:
        raise PermissionDenied("Esta aula ainda não foi publicada.")
    
    
    return render(request, 'academico/aulas/visualizar_aula.html', {
        'aula': aula, 
        'disciplina': aula.disciplina, 
        'conteudo_html': aula.conteudo, 
        'e_autor': e_autor
    })

# 5.1 Edição de Slides da aula
@login_required
def editar_conteudo_slide(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if request.method == 'POST':
        # CAPTURA O CONTEÚDO EDITADO PELO USUÁRIO NO TEMPLATE
        conteudo_editado = request.POST.get('conteudo_slide')
        
        from academico.utils.gerador_slides import criar_apresentacao
        import io
        
        # PASSA O CONTEÚDO EDITADO, E NÃO O DA AULA ORIGINAL
        prs = criar_apresentacao(aula.titulo, conteudo_editado)
        
        buffer = io.BytesIO()
        prs.save(buffer)
        buffer.seek(0)
        
        response = HttpResponse(
            buffer.read(), 
            content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        response['Content-Disposition'] = f'attachment; filename={aula.titulo}_slides.pptx'
        return response

    return render(request, 'academico/aulas/editar_conteudo_slide.html', {'aula': aula})

# 6. Alternar Publicação
@login_required
@require_POST
def alternar_publicacao(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    if request.user == aula.disciplina.professor or request.user.is_staff:
        aula.publicado = not aula.publicado
        aula.save()
    return redirect('gerenciar_aulas', disciplina_id=aula.disciplina.id)

# 7. Seletor de Disciplina
@login_required
def selecionar_disciplina_para_aula(request):
    disciplinas = Disciplina.objects.filter(professor=request.user)
    if request.method == 'POST':
        return redirect('criar_aula', disciplina_id=request.POST.get('disciplina_id'))
    return render(request, 'academico/disciplinas/selecionar_disciplina.html', {'disciplinas': disciplinas})

# 7. Recursos
# -- 7.1 Menu de Recursos
@login_required
def menu_recursos(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    return render(request, 'academico/recursos/menu_recursos.html', {'aula': aula})

# -- 7.1.1 Videos
@login_required
def gerenciar_videos(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if request.method == 'POST':
        formset = VideoFormSet(request.POST, instance=aula)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Vídeos atualizados com sucesso!")
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        formset = VideoFormSet(instance=aula)
        
    return render(request, 'academico/recursos/gerenciar_videos.html', {
        'aula': aula,
        'formset': formset
    })

# -- 7.1.2 PDF
@login_required
def gerenciar_pdfs(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if request.method == 'POST':
        formset = PDFFormSet(request.POST, instance=aula)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Links de PDF atualizados!")
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        formset = PDFFormSet(instance=aula)
        
    return render(request, 'academico/recursos/gerenciar_pdfs.html', {
        'aula': aula,
        'formset': formset
    })

# -- 7.1.3 Links Úteis
@login_required
def gerenciar_links(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    
    if request.method == 'POST':
        formset = LinkUtilFormSet(request.POST, instance=aula)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Links úteis atualizados!")
            return redirect('visualizar_aula', aula_id=aula.pk)
    else:
        formset = LinkUtilFormSet(instance=aula)
        
    return render(request, 'academico/recursos/gerenciar_links.html', {
        'aula': aula,
        'formset': formset
    })

# --- Reordenação de Aulas ---

@login_required
def reordenar_aulas_template(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    aulas = disciplina.aulas.all().order_by('ordem')
    return render(request, 'academico/aulas/reordenar_aulas.html', {'disciplina': disciplina, 'aulas': aulas})

from django.db import transaction, models  # Adicione o ', models' aqui

@login_required
def reordenar_aulas_salvar(request, pk):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            with transaction.atomic():
                # Deslocamento para evitar conflito de UNIQUE constraint
                Aula.objects.filter(disciplina_id=pk).update(ordem=models.F('ordem') + 10000)
                
                # Aplicar nova ordem
                for item in data['ordem']:
                    Aula.objects.filter(pk=item['id']).update(ordem=item['nova_ordem'])
            
            return JsonResponse({
                'status': 'success', 
                'redirect_url': reverse('reordenar_confirmacao', args=[pk])
            })
        except Exception as e:
            logger.error(f"Erro ao salvar reordenação: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Método inválido'}, status=400)

@login_required
def reordenar_confirmacao(request, pk):
    disciplina = get_object_or_404(Disciplina, pk=pk)
    return render(request, 'academico/aulas/confirmar_reordenacao.html', {'disciplina': disciplina})


@login_required
def marcar_aula_lida(request, aula_id):
    aula = get_object_or_404(Aula, pk=aula_id)
    aluno = get_object_or_404(Aluno, user=request.user)
    
    # Validação de tempo (ex: 30 segundos)
    # Se você quiser uma regra de negócio, pode checar data_criacao ou similar
    
    AulaLida.objects.get_or_create(aluno=aluno, aula=aula)
    return JsonResponse({'status': 'success'})


def baixar_slides(request, aula_id):
    aula = Aula.objects.get(pk=aula_id)
    prs = criar_apresentacao(aula.titulo, aula.conteudo)
    
    # Salva na memória em vez de disco
    buffer = io.BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    
    response = HttpResponse(buffer.read(), content_type='application/vnd.openxmlformats-officedocument.presentationml.presentation')
    response['Content-Disposition'] = f'attachment; filename={aula.titulo}.pptx'
    return response


@login_required
def adicionar_comentario_contextual(request, aula_pk):
    aula = get_object_or_404(Aula, pk=aula_pk)
    
    if request.method == 'POST' and aula.disciplina.professor == request.user:
        comentario_id = request.POST.get('comentario_id')
        identificador = request.POST.get('identificador_ancora')
        texto = request.POST.get('texto')
        
        if identificador and texto:
            if comentario_id:
                # Atualizar (Update) se veio ID
                comentario = get_object_or_404(ComentarioContextual, pk=comentario_id, professor=request.user)
                comentario.identificador_ancora = identificador
                comentario.texto = texto
                comentario.save()
                messages.success(request, "Nota atualizada com sucesso!")
            else:
                # Criar (Create) se não veio ID
                ComentarioContextual.objects.create(
                    aula=aula,
                    professor=request.user,
                    identificador_ancora=identificador,
                    texto=texto
                )
                messages.success(request, "Nota adicionada com sucesso!")
        else:
            messages.error(request, "Preencha todos os campos da nota.")
            
    return redirect('visualizar_aula', aula_id=aula.pk)

@login_required
def excluir_comentario_contextual(request, comentario_pk):
    comentario = get_object_or_404(ComentarioContextual, pk=comentario_pk)
    
    # Valida se o usuário logado é o dono do comentário/professor
    if comentario.professor == request.user:
        aula_pk = comentario.aula.pk
        comentario.delete()
        messages.success(request, "Nota excluída com sucesso!")
        return redirect('visualizar_aula', aula_id=aula_pk)
    
    raise PermissionDenied("Acesso negado.")