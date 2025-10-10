from django.contrib import admin
from .models import Entrenador, Socio, Suscripcion, Pago, Clase, InscripcionClase

@admin.register(Entrenador)
class EntrenadorAdmin(admin.ModelAdmin):
    list_display = ('id_entrenador', 'nombre', 'especialidad', 'telefono', 'salario')
    search_fields = ('nombre', 'id_entrenador')
    list_filter = ('especialidad', 'fecha_contratacion')

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('id_socio', 'nombre', 'apellido', 'telefono', 'tipo_socio', 'estado', 'get_activo_display')
    search_fields = ('nombre', 'apellido', 'id_socio')
    list_filter = ('tipo_socio', 'estado', 'fecha_registro')
    readonly_fields = ('fecha_registro',)

    def get_activo_display(self, obj):
        return obj.activo

@admin.register(Suscripcion)
class SuscripcionAdmin(admin.ModelAdmin):
    list_display = ('id_suscripcion', 'socio', 'tipo', 'fecha_inicio', 'fecha_fin', 'activa', 'monto_total')
    list_filter = ('tipo', 'activa')
    raw_id_fields = ('socio',)

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'socio', 'tipo_pago', 'monto', 'fecha_pago', 'get_metodo_display')  # Changed: Use method for metodo
    list_filter = ('tipo_pago', 'metodo')
    raw_id_fields = ('socio', 'suscripcion', 'clase')

    def get_metodo_display(self, obj):
        """Custom method to safely display 'metodo' (handles null/blank)"""
        return obj.metodo or 'N/A'

@admin.register(Clase)
class ClaseAdmin(admin.ModelAdmin):
    list_display = ('id_clase', 'nombre', 'fecha_hora', 'entrenador', 'precio', 'participantes_actuales')
    list_filter = ('entrenador', 'fecha_hora')
    filter_horizontal = ('participantes',)
    readonly_fields = ('participantes_actuales',)
    raw_id_fields = ('entrenador',)

@admin.register(InscripcionClase)
class InscripcionClaseAdmin(admin.ModelAdmin):
    list_display = ('id_inscripcion', 'socio', 'clase', 'fecha_inscripcion', 'pago_asociado')
    list_filter = ('fecha_inscripcion',)
    raw_id_fields = ('socio', 'clase', 'pago_asociado')