from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Entrenador, Clase, PerfilMiembro, Suscripcion, Pago


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class EntrenadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Entrenador
        fields = '__all__'


class ClaseSerializer(serializers.ModelSerializer):
    entrenador = serializers.PrimaryKeyRelatedField(queryset=Entrenador.objects.all())
    participantes = serializers.PrimaryKeyRelatedField(
        queryset=get_user_model().objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Clase
        fields = '__all__'


class PerfilMiembroSerializer(serializers.ModelSerializer):
    usuario_detalle = UsuarioSerializer(source='usuario', read_only=True)

    class Meta:
        model = PerfilMiembro
        fields = (
            'id',
            'usuario',
            'usuario_detalle',
            'fecha_registro',
            'peso',
            'telefono',
        )
        read_only_fields = ('fecha_registro',)


class SuscripcionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suscripcion
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'
