from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout # <-- Importaciones Clave
from django.contrib import messages
from .models import Clase

<<<<<<< HEAD
# VISTAS EXISTENTES

def home(request):
    """Muestra la página de inicio."""
    return render(request, 'gimnasio/home.html')
=======
def dashboard(request):
    return render(request, 'gimnasio/dashboard.html')
>>>>>>> 1d4a44e (Avance API)


def lista_clases(request):
    """Muestra la lista de clases, con opción a filtrar por entrenador."""
    clases = Clase.objects.all()
    entrenador_id = request.GET.get('entrenador')
    if entrenador_id:
        clases = clases.filter(entrenador_id=entrenador_id)
    context = {'clases': clases}
    return render(request, 'gimnasio/lista_clases.html', context)


# NUEVA VISTA PARA INICIAR SESIÓN

def login_usuario(request):
    """
    Gestiona la visualización del formulario de login (GET)
    y el procesamiento de la autenticación (POST).
    """
    if request.method == 'POST':
        # 1. Obtener datos del formulario de login.html
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 2. Intentar autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 3. Si es válido, iniciar la sesión
            login(request, user)
            messages.success(request, f"Bienvenido de nuevo, {username}!")
            # Redirigir al usuario al home o a su dashboard
            return redirect('home') 
        else:
            # 4. Si es inválido, mostrar un mensaje de error
            messages.error(request, "Nombre de usuario o contraseña incorrectos. Inténtalo de nuevo.")
            
    # Mostrar el formulario de login si el método es GET o si falló el login
    return render(request, 'gimnasio/login.html')


# VISTA PARA CERRAR SESIÓN

def logout_usuario(request):
    """Cierra la sesión del usuario actual."""
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    # Redirigir al usuario a la página de inicio
    return redirect('home')

def registro_usuario(request):
    """Placeholder para la vista de registro."""
    # Por ahora, solo devuelve una plantilla vacía o un mensaje
    # ¡Debes crear el archivo registro.html para que esto funcione!
    return render(request, 'gimnasio/registro.html')