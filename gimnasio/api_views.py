from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from .models import Entrenador, Clase, Socio, Suscripcion, Pago  # Cambiado: Import Socio en lugar de PerfilMiembro
from .serializers import (  # Asume que tienes serializers actualizados
    EntrenadorSerializer,
    ClaseSerializer,
    SocioSerializer,
    SuscripcionSerializer,
    PagoSerializer,
)

class BaseGymViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)


class EntrenadorViewSet(BaseGymViewSet):
    queryset = Entrenador.objects.all()
    serializer_class = EntrenadorSerializer


class ClaseViewSet(BaseGymViewSet):
    queryset = Clase.objects.select_related('entrenador').prefetch_related('participantes')
    serializer_class = ClaseSerializer


class SocioViewSet(BaseGymViewSet):  
    queryset = Socio.objects.all()  


class SuscripcionViewSet(BaseGymViewSet):
    queryset = Suscripcion.objects.select_related('socio')  # Cambiado: 'socio' en lugar de 'miembro__usuario'
    serializer_class = SuscripcionSerializer


class PagoViewSet(BaseGymViewSet):
    queryset = Pago.objects.select_related('suscripcion__socio', 'clase')  # Cambiado: 'suscripcion__socio' en lugar de 'suscripcion__miembro__usuario'
    serializer_class = PagoSerializer