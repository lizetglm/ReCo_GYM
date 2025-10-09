from django.contrib import admin
from .models import Entrenador, Clase, PerfilMiembro, Suscripcion, Pago

# Registramos cada modelo con opciones personalizadas
@admin.register(Entrenador)
class EntrenadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'especialidad', 'telefono')
    search_fields = ('nombre',)
    list_filter = ('especialidad',)

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_hora', 'entrenador', 'duracion_minutos')
    list_filter = ('entrenador', 'fecha_hora')
    filter_horizontal = ('participantes',)

@admin.register(PerfilMiembro)
class PerfilMiembroAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_registro', 'telefono')
    raw_id_fields = ('usuario',)

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('miembro', 'tipo', 'fecha_inicio', 'activa')
    list_filter = ('tipo', 'activa')

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('suscripcion', 'monto', 'fecha_pago', 'metodo')
    list_filter = ('metodo',)