from rest_framework import serializers
from .models import Entrenador, Clase, Socio, Suscripcion, Pago

class EntrenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrenador
        fields = '__all__'

class ClaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clase
        fields = '__all__' 

class SocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socio
        fields = '__all__' 

class SuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = '__all__' 

# class PagoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Pago
#         fields = '__all__'


# Serializer Anidado para Suscripción
class SuscripcionDetalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = ('tipo', 'fecha_inicio', 'fecha_fin', 'activa', 'monto_total',)

# serializer Anidado para Clase
class ClaseDetalleSerializer(serializers.ModelSerializer):
    entrenador_nombre = serializers.ReadOnlyField(source='entrenador.nombre')
    
    class Meta:
        model = Clase
        fields = ( 'nombre','fecha_hora','precio', 'entrenador_nombre')


class PagoSerializer(serializers.ModelSerializer):
    # Campo que se mantiene como StringRelatedField (Socio)
    socio_display = serializers.StringRelatedField(source='socio', read_only=True)
    
    #SuscripcionDetalleSerializer, pero con el alias 'suscripcion_display'
    suscripcion_display = SuscripcionDetalleSerializer(source='suscripcion', read_only=True)
    
    #ClaseDetalleSerializer, pero con el alias 'clase_display'
    clase_display = ClaseDetalleSerializer(source='clase', read_only=True)
    
    class Meta:
        model = Pago
        fields = ('id_pago', 'socio_display', 'suscripcion_display', 'clase_display', 
            'tipo_pago', 'fecha_pago', 'monto', 'metodo'
        )