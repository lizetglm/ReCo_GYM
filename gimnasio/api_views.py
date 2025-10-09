from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from .models import Entrenador, Clase, PerfilMiembro, Suscripcion, Pago
from .serializers import (
    EntrenadorSerializer,
    ClaseSerializer,
    PerfilMiembroSerializer,
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


class PerfilMiembroViewSet(BaseGymViewSet):
    queryset = PerfilMiembro.objects.select_related('usuario')
    serializer_class = PerfilMiembroSerializer


class SuscripcionViewSet(BaseGymViewSet):
    queryset = Suscripcion.objects.select_related('miembro__usuario')
    serializer_class = SuscripcionSerializer


class PagoViewSet(BaseGymViewSet):
    queryset = Pago.objects.select_related('suscripcion__miembro__usuario')
    serializer_class = PagoSerializer
