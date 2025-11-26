from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q
from django.utils.crypto import get_random_string
from datetime import date, timedelta
from .models import Clase, Entrenador, Socio, Suscripcion,InscripcionClase, Producto, Caja, VentaItem, CajaMovimiento
from decimal import Decimal, InvalidOperation
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from django.views.generic import TemplateView
from django.db.models import Sum
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .whatsapp import send_whatsapp_message
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from datetime import datetime
from django.conf import settings
from django.views.decorators.http import require_http_methods


@login_required
def dashboard(request):
    if not request.user.is_staff and not request.user.is_superuser:
        return redirect('perfil_socio')
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

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def reset_password_socio(request, pk):
    # Restringe el acceso solo a administradores
    if not request.user.is_staff:
        messages.error(request, "Acceso denegado.")
        return redirect('socios_list')

    if request.method == 'POST':
        socio = get_object_or_404(Socio, pk=pk)

        if socio.user:
            # Generar nueva contraseña y establecerla en el objeto User
            nueva_contraseña = get_random_string(length=8)
            socio.user.set_password(nueva_contraseña)
            socio.user.save()

            messages.success(request, 
                f"La contraseña de **{socio.nombre}** ha sido restablecida. La nueva contraseña temporal es: **{nueva_contraseña}**. (¡Anotar y comunicar al socio!)")
        else:
            messages.warning(request, "Este socio no tiene una cuenta de usuario de acceso vinculada.")

    return redirect('socios_list')

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def eliminar_socio(request, pk):
    socio = get_object_or_404(Socio, pk=pk)
    
    if request.method == 'POST':
        
        nombre_completo = f"{socio.nombre} {socio.apellido}"
        user_eliminado = False
        username_a_eliminar = socio.id_socio 
        try:
            usuario_django = User.objects.get(username=username_a_eliminar)
            
            usuario_django.delete() 
            user_eliminado = True
            
            print(f"DEBUG: Usuario de Django {username_a_eliminar} eliminado por username.")
            
        except User.DoesNotExist:
            print(f"DEBUG: Usuario {username_a_eliminar} no encontrado en la tabla de Django.")
            pass
            
        except Exception as e:
            messages.warning(request, f"Advertencia: Error crítico al eliminar la cuenta de usuario de Django ({username_a_eliminar}): {e}")
            print(f"DEBUG: ERROR CRÍTICO AL BORRAR USUARIO {username_a_eliminar}: {e}")

        try:
            socio.delete()
            
        except Exception as e:
            messages.error(request, f"Error CRÍTICO al eliminar el socio {nombre_completo} de la base de datos: {e}")
            return redirect('socios_list')
        
        msg = f'Socio "{nombre_completo}" eliminado correctamente.'
        if user_eliminado:
            msg += " También se eliminó su cuenta de acceso."
            
        messages.success(request, msg)
        
        return redirect('socios_list')
    
    return redirect('socios_list')
# Lista de Clases con filtro por Entrenador
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
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
            
            if user.is_staff or user.is_superuser:
                return redirect('dashboard') 
            else:
                try:
                    Socio.objects.get(user=user)
                    return redirect('perfil_socio')
                except Socio.DoesNotExist:
                    messages.error(request, "Tu cuenta no está vinculada a un socio. Acceso denegado.")
                    logout(request)
                    return redirect('login_usuario')
        else:
            # Autenticación fallida (contraseña o usuario/id incorrecto)
            messages.error(request, "ID de Socio/Nombre de usuario o contraseña incorrectos. Inténtalo de nuevo.")
            
    return render(request, 'gimnasio/login.html')

@login_required
def logout_usuario(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect('login_usuario')

@login_required
def registro_usuario(request):
    return render(request, 'gimnasio/registro.html')
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
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
            socio.suscripcion_activa = socio.suscripciones.filter(activa=True).first() or socio.suscripciones.order_by('-fecha_inicio').first()
        else:
            socio.suscripcion_activa = None

    temp_password_data = request.session.pop('temp_password_data', None)
    
    context = {
        'socios': socios,
        'temp_password_data': temp_password_data,
    }
    return render(request, 'gimnasio/socios_list.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def socio_form(request, pk=None):
    socio = None
    suscripcion = None
    if pk:
        socio = get_object_or_404(Socio, pk=pk)
        if socio.tipo_socio == 'interno':
            suscripcion = socio.suscripciones.filter(activa=True).first() or socio.suscripciones.first()

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Datos del POST
                nombre = request.POST.get('nombre', '').strip()
                apellido = request.POST.get('apellido', '').strip()
                telefono = request.POST.get('telefono', '').strip()
                domicilio = request.POST.get('domicilio', '').strip()
                tipo_socio = request.POST.get('tipo_socio')
                tipo_suscripcion = request.POST.get('tipo_suscripcion') if tipo_socio == 'interno' else None
                fecha_inicio_str = request.POST.get('fecha_inicio') if tipo_socio == 'interno' else None

                if not all([nombre, apellido, telefono, domicilio, tipo_socio]):
                    raise ValueError("Todos los campos obligatorios deben llenarse.")

                # Generar id_socio único (solo para nuevo)
                if not socio:
                    contador = Socio.objects.count() + 1
                    id_socio_propuesto = f"S{contador:03d}"
                    while Socio.objects.filter(id_socio=id_socio_propuesto).exists():
                        contador += 1
                        id_socio_propuesto = f"S{contador:03d}"
                    id_socio = id_socio_propuesto
                else:
                    id_socio = socio.id_socio

                # Crear/actualizar socio
                if socio:  # Edición
                    socio.nombre = nombre
                    socio.apellido = apellido
                    socio.telefono = telefono
                    socio.domicilio = domicilio
                    socio.tipo_socio = tipo_socio
                    socio.save()
                    messages.success(request, f'Socio {nombre} {apellido} actualizado correctamente.')
                    if tipo_socio == 'externo':
                        socio.suscripciones.all().delete()  # Limpia si cambia a externo
                else:  # Creación nueva
                    socio = Socio.objects.create(
                        id_socio=id_socio,
                        nombre=nombre,
                        apellido=apellido,
                        telefono=telefono,
                        domicilio=domicilio,
                        tipo_socio=tipo_socio,
                        estado='activo'
                    )
                    messages.success(request, f'Socio {nombre} {apellido} creado correctamente.')

                # Suscripción para internos
                if tipo_socio == 'interno' and tipo_suscripcion and fecha_inicio_str:
                    fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
                    if suscripcion:  # Actualizar existente
                        suscripcion.tipo = tipo_suscripcion
                        suscripcion.fecha_inicio = fecha_inicio
                        suscripcion.save()  # Recalcula fin/monto
                    else:  # Crear nueva
                        contador_sus = Suscripcion.objects.count() + 1
                        id_sus_propuesto = f"SUB{contador_sus:03d}"
                        while Suscripcion.objects.filter(id_suscripcion=id_sus_propuesto).exists():
                            contador_sus += 1
                            id_sus_propuesto = f"SUB{contador_sus:03d}"
                        Suscripcion.objects.create(
                            id_suscripcion=id_sus_propuesto,
                            socio=socio,
                            tipo=tipo_suscripcion,
                            fecha_inicio=fecha_inicio
                        )

                # Crear User y password SOLO para creación nueva
                if not pk:  # Nueva
                    password = get_random_string(length=8)
                    user, created = User.objects.get_or_create(
                        username=id_socio,
                        defaults={'password': '', 'is_staff': False}
                    )
                    if created or not user.password:
                        user.set_password(password)
                        user.first_name = nombre
                        user.last_name = apellido
                        user.save()
                        socio.user = user
                        socio.save()

                    temp_data = {
                        'id_socio': id_socio,
                        'password': password,
                        'whatsapp_sent': False,
                        'error': None
                    }
                    request.session['temp_password_data'] = temp_data
    
                    # Para AJAX: Retorna JSON
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'id_socio': id_socio,
                            'password': password,
                            'message': f'Socio {nombre} {apellido} creado exitosamente.',
                            'socio_pk': socio.pk
                        })

            if not pk:
                temp_data = {
                    'id_socio': id_socio,
                    'password': password,
                    'whatsapp_sent': False,
                    'error': None
                }
                request.session['temp_password_data'] = temp_data

            return redirect('socios_list')

        except ValueError as ve:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(ve)
                }, status=400)
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=400)

    post_data = {k: v for k, v in request.POST.items()} if request.method == 'POST' else {}
    
    nombre_value = post_data.get('nombre', socio.nombre if socio else '')
    apellido_value = post_data.get('apellido', socio.apellido if socio else '')
    telefono_value = post_data.get('telefono', socio.telefono if socio else '')
    domicilio_value = post_data.get('domicilio', socio.domicilio if socio else '')
    tipo_socio_value = post_data.get('tipo_socio', socio.tipo_socio if socio else '')
    
    suscripcion_tipo = suscripcion.tipo if suscripcion else None
    suscripcion_fecha_inicio = suscripcion.fecha_inicio.strftime('%Y-%m-%d') if suscripcion and suscripcion.fecha_inicio else None

    context = {
        'socio': socio,
        'post_data': post_data,
        'nombre_value': nombre_value,
        'apellido_value': apellido_value,
        'telefono_value': telefono_value,
        'domicilio_value': domicilio_value,
        'tipo_socio_value': tipo_socio_value,
        'suscripcion_tipo': suscripcion_tipo,
        'suscripcion_fecha_inicio': suscripcion_fecha_inicio or '',
        'twilio_configured': bool(getattr(settings, 'TWILIO_ACCOUNT_SID', '') and getattr(settings, 'TWILIO_AUTH_TOKEN', '') and getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '')),
    }
    return render(request, 'gimnasio/socio_form.html', context)

@login_required(login_url='login')  # Solo usuarios autenticados
@require_http_methods(["POST"])      # Solo acepta POST

def enviar_whatsapp_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido. Usa POST.'}, status=405)
    
    try:
        telefono = request.POST.get('telefono', '').strip()
        id_socio = request.POST.get('id_socio', '').strip()
        password = request.POST.get('password', '').strip()
        nombre = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()

        if not all([telefono, id_socio, password, nombre, apellido]):
            return JsonResponse({
                'sent': False, 
                'error': 'Datos incompletos: faltan teléfono, ID socio, password, nombre o apellido.'
            }, status=400)

        whatsapp_sent, error_msg = send_whatsapp_message(telefono, id_socio, password, nombre, apellido)

        if whatsapp_sent:
            print(f"WhatsApp enviado exitosamente a {telefono} para socio {id_socio}")
            return JsonResponse({
                'sent': True, 
                'message': 'WhatsApp enviado correctamente al socio.'
            }, status=200)
        else:
            print(f"Error en WhatsApp para {telefono}: {error_msg}") 
            return JsonResponse({
                'sent': False, 
                'error': error_msg or 'Error desconocido al enviar WhatsApp.',
                'credenciales': f'Usuario: {id_socio}, Contraseña temporal: {password}' 
            }, status=200)

    except Exception as e:
        print(f"Error crítico en enviar_whatsapp_api: {str(e)}")
        return JsonResponse({
            'sent': False, 
            'error': f'Error interno del servidor: {str(e)}'
        }, status=500)

@login_required
def perfil_socio(request):
    try:
        socio = Socio.objects.get(user=request.user)
    except Socio.DoesNotExist:
        messages.error(request, "Error: Tu cuenta no está asociada a ningún socio.")
        logout(request)
        return redirect('login_usuario')

    suscripcion = socio.suscripciones.filter(activa=True).order_by('-fecha_inicio').first()
    
    clases_inscritas = InscripcionClase.objects.filter(socio=socio).select_related('clase')

    context = {
        'socio': socio,
        'suscripcion': suscripcion,
        'clases_inscritas': clases_inscritas,
        'clases_activas': Clase.objects.all(), 
    }
    return render(request, 'gimnasio/perfil_socio.html', context)

@login_required
def perfil_lista_clases(request):
    clases = Clase.objects.select_related('entrenador').all()
    query = request.GET.get('q', '')
    if query:
        clases = clases.filter(
            Q(nombre__icontains=query) |
            Q(entrenador__nombre__icontains=query) |
            Q(descripcion__icontains=query)
        )
    return render(request, 'gimnasio/perfil_lista_clases.html', {'clases': clases, 'query': query})

@login_required
def perfil_instructores_list(request):
    entrenadores = Entrenador.objects.all()
    query = request.GET.get('q', '')
    if query:
        entrenadores = entrenadores.filter(
            Q(nombre__icontains=query) |
            Q(especialidad__icontains=query) |
            Q(telefono__icontains=query)
        )
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def inscribir_a_clase(request, socio_id, clase_id):
    socio = get_object_or_404(Socio, pk=socio_id)
    clase = get_object_or_404(Clase, pk=clase_id)
    
    if request.method == 'POST':
        movimiento = CajaMovimiento.objects.create(
            tipo='clase',
            descripcion=f"Pago Clase {clase.nombre} - Socio {socio.id_socio}",
            metodo_pago=request.POST.get('metodo', 'efectivo'),
            monto=clase.precio,
            socio=socio,
        )
        inscripcion = InscripcionClase.objects.create(
            id_inscripcion=f"INS{date.today().strftime('%Y%m%d')}-{socio.id_socio}-{clase.id_clase}",
            socio=socio,
            clase=clase,
            movimiento_caja=movimiento
        )
        
        movimiento.inscripcion_clase = inscripcion
        movimiento.save()
        
        clase.participantes.add(socio)
        
        messages.success(request, f'{socio.nombre} inscrito a {clase.nombre} por ${clase.precio}.')
        return redirect('lista_clases')
    
    context = {'socio': socio, 'clase': clase}
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def clase_form(request, pk=None):
    clase = None
    if pk:
        clase = get_object_or_404(Clase.objects.select_related('entrenador'), pk=pk)
        
    entrenadores = Entrenador.objects.all()

    if request.method == 'POST':
        # Campos de Clase
        id_clase = request.POST.get('id_clase', get_random_string(length=10))
        nombre = request.POST.get('nombre', '')
        descripcion = request.POST.get('descripcion', '')
        fecha_hora = request.POST.get('fecha_hora', '')
        duracion_minutos = request.POST.get('duracion_minutos', 60)
        entrenador_pk = request.POST.get('entrenador', '')
        max_participantes = request.POST.get('max_participantes', 20)
        precio = request.POST.get('precio', 0.00)

        if not entrenador_pk:
            messages.error(request, "Debe seleccionar un entrenador.")
            context = {'clase': clase, 'entrenadores': entrenadores}
            return render(request, 'gimnasio/clase_form.html', context)
            
        entrenador = get_object_or_404(Entrenador, pk=entrenador_pk)

        # Crear o actualizar Clase
        if clase is None:
            if Clase.objects.filter(id_clase=id_clase).exists():
                id_clase = get_random_string(length=10)
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
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def eliminar_clase(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    if request.method == 'POST':
        nombre_clase = clase.nombre
        clase.delete()
# Función para Inscribir un Socio a una Clase
# Función para Inscribir un Socio a una Clase
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def inscribir_clase(request, clase_pk):
    if request.method == 'POST':
        clase = get_object_or_404(Clase, pk=clase_pk)
        socio_id_input = request.POST.get('socio_id') 

        if not socio_id_input:
            messages.error(request, 'Debes ingresar el ID del socio.')
            return redirect('lista_clases')
            
        try:
            socio = Socio.objects.get(id_socio=socio_id_input)
            
            if clase.participantes.filter(pk=socio.pk).exists():
                messages.warning(request, f'El socio {socio.nombre} ya está inscrito en {clase.nombre}.')
                return redirect('lista_clases')

            #Verificar capacidad máxima
            if clase.participantes_actuales >= clase.max_participantes:
                messages.error(request, f'La clase {clase.nombre} está llena. ¡Máximo {clase.max_participantes} participantes!')
                return redirect('lista_clases')
                
            #Realizar la inscripción
            clase.participantes.add(socio)
            
            messages.success(request, f'¡Inscripción exitosa! {socio.nombre} inscrito a la clase de {clase.nombre}.')
            
        except Socio.DoesNotExist:
            messages.error(request, f'Error: No se encontró ningún socio con el ID "{socio_id_input}".')
        except Exception as e:
            messages.error(request, f'Error al inscribir: {e}')
            
@login_required
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def inscripcion_clase_detalle(request, pk):
    clase = get_object_or_404(Clase, pk=pk)
    
    if request.method == 'POST':
        socio_id_input = request.POST.get('socio_id')

        if not socio_id_input:
            messages.error(request, 'Debes ingresar el ID del socio para inscribirlo.')
            return redirect('inscripcion_clase_detalle', pk=pk)
            
        try:
            socio = Socio.objects.get(id_socio=socio_id_input)
            
            if clase.participantes.filter(pk=socio.pk).exists():
                messages.warning(request, f'El socio {socio.nombre} ya está inscrito en {clase.nombre}.')
                return redirect('inscripcion_clase_detalle', pk=pk)

            if clase.participantes_actuales >= clase.max_participantes:
                messages.error(request, f'La clase {clase.nombre} está llena. ¡Máximo {clase.max_participantes} participantes!')
                return redirect('inscripcion_clase_detalle', pk=pk)
                
            clase.participantes.add(socio)
    
            inscripcion = InscripcionClase.objects.create(
                id_inscripcion=f"INS{date.today().strftime('%Y%m%d')}-{socio.id_socio}-{clase.id_clase}",
                socio=socio,
                clase=clase,
            )
            
            movimiento = CajaMovimiento.objects.create(
                tipo='clase',
                descripcion=f"Pago Clase {clase.nombre} - Socio {socio.id_socio}",
                metodo_pago=request.POST.get('metodo', 'efectivo'), # Debe venir del formulario
                monto=clase.precio,
                socio=socio,
                inscripcion_clase=inscripcion
            )

            inscripcion.movimiento_caja = movimiento
            inscripcion.save()
            
            
            messages.success(request, f'¡Inscripción exitosa! {socio.nombre} inscrito a la clase de {clase.nombre} por ${clase.precio}.')
            
        except Socio.DoesNotExist:
            messages.error(request, f'Error: No se encontró ningún socio con el ID "{socio_id_input}".')
        except Exception as e:
            messages.error(request, f'Error al inscribir: {e}')
            
        return redirect('inscripcion_clase_detalle', pk=pk)

    context = {
        'clase': clase,
    }
    return render(request, 'gimnasio/inscripcion_clase_detalle.html', context)

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def eliminar_inscripcion_clase(request, clase_pk, socio_pk):
    clase = get_object_or_404(Clase, pk=clase_pk)
    socio = get_object_or_404(Socio, pk=socio_pk)
    
    if request.method == 'POST':
        if clase.participantes.filter(pk=socio.pk).exists():
            clase.participantes.remove(socio)
            
            try:
                inscripcion = InscripcionClase.objects.get(socio=socio, clase=clase)
                
                if inscripcion.movimiento_caja:
                    pago_id = inscripcion.movimiento_caja.pk
                    inscripcion.movimiento_caja.delete() # Elimina el pago
                    messages.info(request, f'Pago asociado ({pago_id}) eliminado.')
                
                inscripcion.delete()
                
                messages.success(request, f'Inscripción de {socio.nombre} a {clase.nombre} eliminada correctamente.')
                
            except InscripcionClase.DoesNotExist:
                messages.warning(request, f'Advertencia: No se encontró un registro formal de InscripcionClase. Se eliminó de la lista de participantes.')
            
        else:
            messages.error(request, f'El socio {socio.nombre} no estaba inscrito en {clase.nombre}.')
            
# Listado de Instructores
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
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
        'query': query
    }
    return render(request, 'gimnasio/instructores_list.html', context) 

# Formulario de Instructor
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def instructor_form(request, pk=None): 
    if pk:
        entrenador = get_object_or_404(Entrenador, pk=pk)
    else:
        entrenador = None

    if request.method == 'POST':
        try:
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
                contador = Entrenador.objects.count() + 1
                id_entrenador =str(contador).zfill(3)
                while Entrenador.objects.filter(id_entrenador=id_entrenador).exists():
                    contador += 1
                    id_entrenador =str(contador).zfill(3)
                    
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

    context = {'entrenador': entrenador}
    return render(request, 'gimnasio/instructor_form.html', context) 

# Eliminar Instructor
@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
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

class CajaView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "gimnasio/caja.html"

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        return redirect('perfil_socio')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        movimientos = CajaMovimiento.objects.select_related(
            'venta', 
            'suscripcion',            
        ).order_by('-fecha')[:200]
        total_hoy = CajaMovimiento.objects.filter(fecha__date=date.today()).aggregate(total=Sum('monto'))['total'] or 0
        ctx.update({
            'movimientos': movimientos,
            'total_hoy': total_hoy,
        })
        return ctx

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def pago_productos(request):
    """Pantalla para registrar ventas de productos en la tienda del gym."""
    productos = Producto.objects.all().order_by("nombre")

    if request.method == "POST":
        pass 
    return render(request, "gimnasio/pago_productos.html", {"productos": productos})

@login_required
@user_passes_test(lambda u: u.is_staff, login_url='perfil_socio')
def ticket_venta_pdf(request, venta_id: int):
    """Genera un PDF tipo ticket para una venta de productos."""
    venta = get_object_or_404(Caja.objects.prefetch_related("items__producto"), pk=venta_id)

    ancho = 80 * mm
    alto_base = 110 * mm
    alto_por_item = 6 * mm
    num_items = venta.items.count()
    alto = alto_base + num_items * alto_por_item
    pagesize = (ancho, alto)

    # Respuesta PDF
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"inline; filename=ticket_venta_{venta.id}.pdf"

    c = canvas.Canvas(response, pagesize=pagesize)
    y = alto - 8 * mm

    def center(text, y_pos, size=11):
        c.setFont("Helvetica-Bold", size)
        c.drawCentredString(ancho / 2, y_pos, text)

    def left(text, y_pos, size=10):
        c.setFont("Helvetica", size)
        c.drawString(6 * mm, y_pos, text)

    # Encabezado
    center("Control Gym", y, 12); y -= 6 * mm
    center("Ticket de Venta", y, 11); y -= 8 * mm

    left(f"N°: {venta.id}", y); y -= 5 * mm
    left(venta.fecha.strftime("Fecha: %d/%m/%Y %H:%M"), y); y -= 5 * mm
    left(f"Método: {venta.get_metodo_pago_display()}", y); y -= 5 * mm
    if venta.cliente:
        left(f"Cliente: {venta.cliente}", y); y -= 5 * mm

    # Separador
    c.line(6 * mm, y, ancho - 6 * mm, y); y -= 5 * mm
    left("Producto", y); c.drawRightString(ancho - 6 * mm, y, "Subtotal"); y -= 4 * mm
    c.line(6 * mm, y, ancho - 6 * mm, y); y -= 4 * mm

    # Items
    for it in venta.items.all():
        nombre = f"{it.producto.nombre} x{it.cantidad}"
        left(nombre[:30], y)
        c.drawRightString(ancho - 6 * mm, y, f"${it.subtotal:.2f}")
        y -= 5 * mm

    # Total
    c.line(6 * mm, y, ancho - 6 * mm, y); y -= 6 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(6 * mm, y, "TOTAL:")
    c.drawRightString(ancho - 6 * mm, y, f"${venta.total:.2f}")
    y -= 8 * mm

    # Observación
    if venta.observacion:
        left("Obs:", y); y -= 5 * mm
        c.setFont("Helvetica", 9)
        for line in str(venta.observacion).splitlines():
            left(line[:40], y); y -= 4 * mm
        y -= 2 * mm

    # Footer
    c.line(6 * mm, y, ancho - 6 * mm, y); y -= 6 * mm
    center("¡Gracias por su compra!", y, 10)

    c.showPage()
    c.save()
    return response


@require_GET
@login_required
def productos_por_categoria_api(request, tipo):
    try:
        clase = Clase.objects.select_related('entrenador').get(nombre__iexact=tipo)
        
        data = {
            'clase': clase.nombre,
            'entrenador': {
                'id': clase.entrenador.pk,
                'nombre': clase.entrenador.nombre,
                'especialidad': clase.entrenador.especialidad,
            }
        }
        return JsonResponse(data, status=200)
    except Clase.DoesNotExist:
        return JsonResponse({'error': 'Clase no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)