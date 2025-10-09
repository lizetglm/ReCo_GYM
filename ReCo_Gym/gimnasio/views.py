from django.shortcuts import render

from django.shortcuts import render, get_object_or_404
from .models import Clase

def home(request):
    return render(request, 'gimnasio/home.html')


def lista_clases(request):
    clases = Clase.objects.all()
    entrenador_id = request.GET.get('entrenador')
    if entrenador_id:
        clases = clases.filter(entrenador_id=entrenador_id)
    context = {'clases': clases}
    return render(request, 'gimnasio/lista_clases.html', context)