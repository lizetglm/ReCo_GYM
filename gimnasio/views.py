from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Clase

def dashboard(request):
    return render(request, 'gimnasio/dashboard.html')

def lista_clases(request):
    clases = Clase.objects.all()
    entrenador_id = request.GET.get('entrenador')
    if entrenador_id:
        clases = clases.filter(entrenador_id=entrenador_id)
    context = {'clases': clases}
    return render(request, 'gimnasio/lista_clases.html', context)

def login_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard') 
        else:
            messages.error(request, "Nombre de usuario o contraseña incorrectos. Inténtalo de nuevo.")
            
    return render(request, 'gimnasio/login.html')

def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login_usuario')

def registro_usuario(request):
    return render(request, 'gimnasio/registro.html')

def socios_list(request):
    socios = []
    query = request.GET.get('q', '')
    if query:
        pass
    context = {'socios': socios, 'query': query}
    return render(request, 'gimnasio/socios_list.html', context)

def socio_form(request):
    context = {}
    if request.method == 'POST':
        pass
    return render(request, 'gimnasio/socio_form.html', context)