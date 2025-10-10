from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.utils.crypto import get_random_string
from datetime import date, timedelta
from .models import Clase, Entrenador, Socio, Suscripcion, Pago, InscripcionClase

def dashboard(request):
    # Estadísticas básicas (ya las tenías)
    total_socios = Socio.objects.count()
    total_clases = Clase.objects.count()
    total_entrenadores = Entrenador.objects.count()

    socios = Socio.objects.all()
    query = request.GET.get('q', '')
    if query:
        socios = socios.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(id_socio__icontains=query)
        )
    today = date.today()
    for socio in socios:
        if socio.tipo_socio == 'interno':
            socio.suscripcion_activa = socio.suscripciones.filter(activa=True).first() or socio.suscripciones.order_by('-fecha_inicio').first()
        else:
            socio.suscripcion_activa = None
            
    context = {
        'total_socios': total_socios,
        'total_clases': total_clases,
        'total_entrenadores': total_entrenadores,
        'socios': socios,
        'query': query,
        'today': today,
    }
    return render(request, 'gimnasio/dashboard.html', context)

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
    socios = Socio.objects.all()
    query = request.GET.get('q', '')
    if query:
        socios = socios.filter(
            Q(nombre__icontains=query) |
            Q(apellido__icontains=query) |
            Q(id_socio__icontains=query)
        )
        
    for socio in socios:
        if socio.tipo_socio == 'interno':
            socio.suscripcion_activa = socio.suscripciones.filter(activa=True).first()
        else:
            socio.suscripcion_activa = None

    context = {'socios': socios, 'query': query}
    return render(request, 'gimnasio/socios_list.html', context)

def socio_form(request, pk=None):
    socio = None
    if pk:
        socio = get_object_or_404(Socio, pk=pk)

    if request.method == 'POST':
        # Campos comunes
        id_socio = request.POST.get('id_socio', '')  # ID único
        nombre = request.POST.get('nombre', '')
        apellido = request.POST.get('apellido', '')
        telefono = request.POST.get('telefono', '')
        domicilio = request.POST.get('domicilio', '')
        tipo_socio = request.POST.get('tipo_socio', 'externo')

        # Crear o actualizar Socio
        if socio is None:
            socio = Socio(id_socio=id_socio, nombre=nombre, apellido=apellido,
                        telefono=telefono, domicilio=domicilio, tipo_socio=tipo_socio)
        else:
            socio.nombre = nombre
            socio.apellido = apellido
            socio.telefono = telefono
            socio.domicilio = domicilio
            socio.tipo_socio = tipo_socio
        socio.save()

        # Si es interno, crear Suscripción inicial y Pago
        if tipo_socio == 'interno':
            tipo_sus = request.POST.get('tipo_suscripcion', 'mensual')
            fecha_inicio = date.today()
            suscripcion = Suscripcion.objects.create(
                id_suscripcion=f"SUS{date.today().strftime('%Y%m%d')}-{id_socio}",  # Ejemplo ID
                socio=socio,
                tipo=tipo_sus,
                fecha_inicio=fecha_inicio
            )
            # Crear Pago para la suscripción
            Pago.objects.create(
                id_pago=f"PAG{date.today().strftime('%Y%m%d')}-{id_socio}-SUS",
                socio=socio,
                tipo_pago='gimnasio',
                suscripcion=suscripcion
            )

        messages.success(request, f'Socio {nombre} {apellido} guardado correctamente.')
        return redirect('socios_list')

    context = {'socio': socio}
    return render(request, 'gimnasio/socio_form.html', context)

def eliminar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    if request.method == 'POST':
        socio.delete()
        messages.success(request, 'Socio eliminado correctamente.')
    return redirect('socios_list')

def inscribir_a_clase(request, socio_id, clase_id):
    socio = get_object_or_404(Socio, pk=socio_id)
    clase = get_object_or_404(Clase, pk=clase_id)
    
    if request.method == 'POST':
        # Crear pago por clase
        pago = Pago.objects.create(
            id_pago=f"PAG{date.today().strftime('%Y%m%d')}-{socio.id_socio}-CLA{clase.id_clase}",
            socio=socio,
            tipo_pago='clase',
            clase=clase,
            metodo=request.POST.get('metodo', '')  # Opcional
        )
        # Crear inscripción
        InscripcionClase.objects.create(
            id_inscripcion=f"INS{date.today().strftime('%Y%m%d')}-{socio.id_socio}-{clase.id_clase}",
            socio=socio,
            clase=clase,
            pago_asociado=pago
        )
        clase.participantes.add(socio)
        
        messages.success(request, f'{socio.nombre} inscrito a {clase.nombre} por ${clase.precio}.')
        return redirect('lista_clases')
    
    context = {'socio': socio, 'clase': clase}
    return render(request, 'gimnasio/inscripcion_form.html', context)