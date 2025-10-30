from rest_framework import serializers
from .models import Entrenador, Clase, Socio, Suscripcion

class EntrenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrenador
        fields = '__all__'

class ClaseSerializer(serializers.ModelSerializer):
    participantes = serializers.SerializerMethodField(read_only=True)
    participantes_ids = serializers.PrimaryKeyRelatedField(
        source='participantes', many=True, queryset=Socio.objects.all(), write_only=True, required=False
    )
    
    entrenador = EntrenadorSerializer(read_only=True)
    entrenador_id = serializers.PrimaryKeyRelatedField(
        source='entrenador', queryset=Entrenador.objects.all(),
        write_only=True, required=False
    )
    entrenador_nombre = serializers.ReadOnlyField(source='entrenador.nombre')
    entrenador_nombre = serializers.ReadOnlyField(source='entrenador.nombre')

    class Meta:
        model = Clase
        fields = '__all__'

    def get_participantes(self, obj):
        return SocioSerializer(obj.participantes.all(), many=True).data

class SocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socio
        fields = '__all__' 

class SuscripcionSerializer(serializers.ModelSerializer):
    # lectura: objeto completo; escritura: enviar socio_id
    socio = SocioSerializer(read_only=True)
    socio_id = serializers.PrimaryKeyRelatedField(
        source='socio', queryset=Socio.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Suscripcion
        fields = '__all__'


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

