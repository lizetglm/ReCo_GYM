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


def clase_form(request, pk=None):
    clase = None
    if pk:
        clase = get_object_or_404(Clase.objects.select_related('entrenador'), pk=pk)
        
    entrenadores = Entrenador.objects.all()

    if request.method == 'POST':
        # Campos de Clase
        id_clase = request.POST.get('id_clase', get_random_string(length=10)) # Generar un ID si no viene
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        duracion_minutos = request.POST.get('duracion_minutos', 60)
        entrenador_pk = request.POST.get('entrenador', '')
        max_participantes = request.POST.get('max_participantes', 20)
        precio = request.POST.get('precio', 0.00)

        # Validación básica de entrenador
        if not entrenador_pk:
            messages.error(request, "Debe seleccionar un entrenador.")
            context = {'clase': clase, 'entrenadores': entrenadores}
            return render(request, 'gimnasio/clase_form.html', context)
            
        entrenador = get_object_or_404(Entrenador, pk=entrenador_pk)

        # Crear o actualizar Clase
        if clase is None:
            # Asegurar que el id_clase es único, especialmente si se genera automáticamente
            if Clase.objects.filter(id_clase=id_clase).exists():
                 id_clase = get_random_string(length=10) # Regenerar si ya existe
                 
            clase = Clase(
                id_clase=id_clase, nombre=nombre, descripcion=descripcion, 
                fecha_hora=fecha_hora, duracion_minutos=duracion_minutos,
                entrenador=entrenador, max_participantes=max_participantes,
                precio=precio
            )
        else:
            clase.nombre = nombre
            clase.descripcion = descripcion
            clase.fecha_hora = fecha_hora
            clase.duracion_minutos = duracion_minutos
            clase.entrenador = entrenador
            clase.max_participantes = max_participantes
            clase.precio = precio
            
        clase.save()

        messages.success(request, f'Clase "{nombre}" guardada correctamente.')
        return redirect('lista_clases')

    # Para GET
    context = {'clase': clase, 'entrenadores': entrenadores}
    return render(request, 'gimnasio/clase_form.html', context)

def eliminar_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == 'POST':
        nombre_clase = clase.nombre
        clase.delete()
        messages.success(request, f'Clase "{nombre_clase}" eliminada correctamente.')
    return redirect('lista_clases')

# Función para Inscribir un Socio a una Clase
def inscribir_clase(request, clase_pk):
    """Maneja la inscripción de un socio en una clase por parte del administrador."""
    if request.method == 'POST':
        clase = get_object_or_404(Clase, pk=clase_pk)
        socio_id_input = request.POST.get('socio_id') # ID_SOCIO (ej: S001)

        if not socio_id_input:
            messages.error(request, 'Debes ingresar el ID del socio.')
            return redirect('lista_clases')
            
        try:
            # Buscar el Socio usando el campo id_socio
            # NOTA: Asegúrate de que 'id_socio' es el campo único que usa el admin
            socio = Socio.objects.get(id_socio=socio_id_input)
            
            # 1. Verificar si ya está inscrito
            if clase.participantes.filter(pk=socio.pk).exists():
                messages.warning(request, f'El socio {socio.nombre} ya está inscrito en {clase.nombre}.')
                return redirect('lista_clases')

            # 2. Verificar capacidad máxima
            if clase.participantes_actuales >= clase.max_participantes:
                messages.error(request, f'La clase {clase.nombre} está llena. ¡Máximo {clase.max_participantes} participantes!')
                return redirect('lista_clases')
                
            # 3. Realizar la inscripción
            clase.participantes.add(socio)
            
            messages.success(request, f'¡Inscripción exitosa! {socio.nombre} inscrito a la clase de {clase.nombre}.')
            
        except Socio.DoesNotExist:
            messages.error(request, f'Error: No se encontró ningún socio con el ID "{socio_id_input}".')
        except Exception as e:
            messages.error(request, f'Error al inscribir: {e}')
            
    return redirect('lista_clases') 


# Detalle de Clase e Inscripción
def inscripcion_clase_detalle(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    
    if request.method == 'POST':
        socio_id_input = request.POST.get('socio_id') # ID_SOCIO (ej: S001)

        if not socio_id_input:
            messages.error(request, 'Debes ingresar el ID del socio para inscribirlo.')
            # Redirige de vuelta a la misma página
            return redirect('inscripcion_clase_detalle', pk=pk)
            
        try:
            # Buscar el Socio usando el campo id_socio
            socio = Socio.objects.get(id_socio=socio_id_input)
            
            # 1. Verificar si ya está inscrito
            if clase.participantes.filter(pk=socio.pk).exists():
                messages.warning(request, f'El socio {socio.nombre} ya está inscrito en {clase.nombre}.')
                return redirect('inscripcion_clase_detalle', pk=pk)

            # 2. Verificar capacidad máxima
            if clase.participantes_actuales >= clase.max_participantes:
                messages.error(request, f'La clase {clase.nombre} está llena. ¡Máximo {clase.max_participantes} participantes!')
                return redirect('inscripcion_clase_detalle', pk=pk)
                
            # 3. Realizar la inscripción 
            clase.participantes.add(socio)
            
            # Crear registro en InscripcionClase y Pago para tener el historial formal
            pago = Pago.objects.create(
                id_pago=f"PAG{date.today().strftime('%Y%m%d')}-{socio.id_socio}-CLA{clase.id_clase}-{get_random_string(length=4)}",
                socio=socio,
                monto=clase.precio,
                tipo_pago='clase',
                clase=clase,
            )
            InscripcionClase.objects.create(
                id_inscripcion=f"INS{date.today().strftime('%Y%m%d')}-{socio.id_socio}-{clase.id_clase}-{get_random_string(length=4)}",
                socio=socio,
                clase=clase,
                pago_asociado=pago
            )
            
            messages.success(request, f'¡Inscripción exitosa! {socio.nombre} inscrito a la clase de {clase.nombre} por ${clase.precio}.')
            
        except Socio.DoesNotExist:
            messages.error(request, f'Error: No se encontró ningún socio con el ID "{socio_id_input}".')
        except Exception as e:
            messages.error(request, f'Error al inscribir: {e}')
            
        return redirect('inscripcion_clase_detalle', pk=pk)

    context = {
        'clase': clase,
        'participantes': clase.participantes.all().order_by('nombre'),
    }
    return render(request, 'gimnasio/inscripcion_clase_detalle.html', context)

# En tu archivo views.py, añade esta función:
def eliminar_inscripcion_clase(request, clase_pk, socio_pk):
    clase = get_object_or_404(Clase, pk=clase_pk)
    socio = get_object_or_404(Socio, pk=socio_pk)
    
    if request.method == 'POST':
        # 1. Eliminar la relación ManyToMany (participantes)
        if clase.participantes.filter(pk=socio.pk).exists():
            clase.participantes.remove(socio)
            
            try:
                # 2. Buscar y eliminar el registro formal de InscripcionClase
                # Esto es crucial para la integridad de los datos
                inscripcion = InscripcionClase.objects.get(socio=socio, clase=clase)
                
                # 3. Opcional: Eliminar el pago asociado si se registró solo para esta clase
                if inscripcion.pago_asociado:
                    pago_id = inscripcion.pago_asociado.id_pago
                    inscripcion.pago_asociado.delete() # Elimina el pago
                    messages.info(request, f'Pago asociado ({pago_id}) eliminado.')
                
                inscripcion.delete() # Elimina la inscripción formal
                
                messages.success(request, f'Inscripción de {socio.nombre} a {clase.nombre} eliminada correctamente.')
                
            except InscripcionClase.DoesNotExist:
                messages.warning(request, f'Advertencia: No se encontró un registro formal de InscripcionClase. Se eliminó de la lista de participantes.')
            
        else:
            messages.error(request, f'El socio {socio.nombre} no estaba inscrito en {clase.nombre}.')
            
        # Redirigir de vuelta a la página de detalle de la clase
        return redirect('inscripcion_clase_detalle', pk=clase_pk)
        
    return redirect('inscripcion_clase_detalle', pk=clase_pk)

# Listado de Instructores
def instructores_list(request): 
    query = request.GET.get('q')
    entrenadores = Entrenador.objects.all().order_by('nombre')
    
    if query:
        entrenadores = entrenadores.filter(
            Q(nombre__icontains=query) |
            Q(especialidad__icontains=query) |
            Q(id_entrenador__icontains=query)
        ).distinct()
        
    context = {
        'entrenadores': entrenadores, 
        'query': query,
    }
    return render(request, 'gimnasio/instructores_list.html', context) 

# Formulario de Instructor
def instructor_form(request, pk=None): 
    if pk:
        entrenador = get_object_or_404(Entrenador, pk=pk)
    else:
        entrenador = None

    if request.method == 'POST':
        try:
            id_entrenador = request.POST.get('id_entrenador')
            nombre = request.POST.get('nombre')
            especialidad = request.POST.get('especialidad')
            telefono = request.POST.get('telefono')
            fecha_contratacion = request.POST.get('fecha_contratacion')
            salario = request.POST.get('salario')

            if entrenador:
                # Entrenador existente
                entrenador.nombre = nombre
                entrenador.especialidad = especialidad
                entrenador.telefono = telefono
                entrenador.fecha_contratacion = fecha_contratacion
                entrenador.salario = salario
                entrenador.save()
                messages.success(request, f'Instructor {nombre} actualizado con éxito.')
            else:
                # Nuevo Entrenador
                Entrenador.objects.create(
                    id_entrenador=id_entrenador,
                    nombre=nombre,
                    especialidad=especialidad,
                    telefono=telefono,
                    fecha_contratacion=fecha_contratacion,
                    salario=salario
                )
                messages.success(request, f'Instructor {nombre} agregado con éxito.')

            return redirect('instructores_list') 
        
        except Exception as e:
            messages.error(request, f'Error al guardar el instructor: {e}')
            return redirect('instructor_form', pk=pk) 

    context = {
        'entrenador': entrenador,
    }
    return render(request, 'gimnasio/instructor_form.html', context) 

# Eliminar Instructor
def eliminar_instructor(request, pk): 
    entrenador = get_object_or_404(Entrenador, pk=pk)
    if request.method == 'POST':
        try:
            nombre = entrenador.nombre
            entrenador.delete()
            messages.success(request, f'Instructor {nombre} eliminado con éxito.')
            return redirect('instructores_list')
        except Exception as e:
            messages.error(request, f'Error al eliminar el instructor: {e}')
            return redirect('instructores_list')
    return redirect('instructores_list') 