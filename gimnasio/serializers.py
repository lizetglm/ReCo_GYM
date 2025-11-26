from rest_framework import serializers
from .models import Entrenador, Clase, Socio, Suscripcion
from .security import sanitize_text_input, validate_email, validate_phone, validate_socio_id

class EntrenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrenador
        fields = '__all__'
    
    def validate_nombre(self, value):
        """Sanitiza y valida el nombre del entrenador."""
        value = sanitize_text_input(value)
        if not value or len(value) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return value
    
    def validate_especialidad(self, value):
        """Sanitiza y valida la especialidad."""
        value = sanitize_text_input(value)
        if not value:
            raise serializers.ValidationError("La especialidad no puede estar vacía.")
        return value
    
    def validate_telefono(self, value):
        """Valida el formato del teléfono."""
        if not validate_phone(value):
            raise serializers.ValidationError("El teléfono no tiene un formato válido.")
        return value

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

    class Meta:
        model = Clase
        fields = '__all__'

    def validate_nombre(self, value):
        """Sanitiza y valida el nombre de la clase."""
        value = sanitize_text_input(value)
        if not value or len(value) < 2:
            raise serializers.ValidationError("El nombre de la clase debe tener al menos 2 caracteres.")
        return value
    
    def validate_descripcion(self, value):
        """Sanitiza la descripción."""
        if value:
            value = sanitize_text_input(value)
        return value
    
    def validate_precio(self, value):
        """Valida que el precio sea positivo."""
        if value < 0:
            raise serializers.ValidationError("El precio no puede ser negativo.")
        return value
    
    def validate_max_participantes(self, value):
        """Valida que el máximo de participantes sea positivo."""
        if value <= 0:
            raise serializers.ValidationError("El máximo de participantes debe ser mayor a 0.")
        return value

    def get_participantes(self, obj):
        return SocioSerializer(obj.participantes.all(), many=True).data

class SocioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Socio
        fields = '__all__'
    
    def validate_id_socio(self, value):
        """Valida el formato del ID de socio."""
        if not validate_socio_id(value):
            raise serializers.ValidationError("El ID de socio debe tener formato válido (ej: S001).")
        return value.upper()
    
    def validate_nombre(self, value):
        """Sanitiza y valida el nombre."""
        value = sanitize_text_input(value)
        if not value or len(value) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return value
    
    def validate_apellido(self, value):
        """Sanitiza y valida el apellido."""
        value = sanitize_text_input(value)
        if not value or len(value) < 2:
            raise serializers.ValidationError("El apellido debe tener al menos 2 caracteres.")
        return value
    
    def validate_telefono(self, value):
        """Valida el formato del teléfono."""
        if not validate_phone(value):
            raise serializers.ValidationError("El teléfono no tiene un formato válido.")
        return value
    
    def validate_domicilio(self, value):
        """Sanitiza el domicilio."""
        value = sanitize_text_input(value)
        if not value:
            raise serializers.ValidationError("El domicilio no puede estar vacío.")
        return value

class SuscripcionSerializer(serializers.ModelSerializer):
    # lectura: objeto completo; escritura: enviar socio_id
    socio = SocioSerializer(read_only=True)
    socio_id = serializers.PrimaryKeyRelatedField(
        source='socio', queryset=Socio.objects.all(), write_only=True, required=False
    )

    class Meta:
        model = Suscripcion
        fields = '__all__'
    
    def validate_tipo(self, value):
        """Valida que el tipo de suscripción sea válido."""
        valid_types = ['mensual', 'trimestral', 'anual']
        if value not in valid_types:
            raise serializers.ValidationError(f"El tipo debe ser uno de: {', '.join(valid_types)}")
        return value


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
