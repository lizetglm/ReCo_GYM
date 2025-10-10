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

class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pago
        fields = '__all__'