# indicadores/views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .services import get_dashboard_indicadores

@staff_member_required
def dashboard_indicadores(request):
    context = get_dashboard_indicadores()
    return render(request, 'indicadores/dashboard.html', context)