from django.urls import path, include
from rest_framework import routers

from .api_views import (
    EntrenadorViewSet,
    ClaseViewSet,
    SocioViewSet,
    SuscripcionViewSet,
    RegistrarVentaAPIView,
)

router = routers.DefaultRouter()
router.register(r'entrenadores', EntrenadorViewSet)
router.register(r'clases', ClaseViewSet)
router.register(r'socios', SocioViewSet)
router.register(r'suscripciones', SuscripcionViewSet)
registrar_venta_api = RegistrarVentaAPIView.as_view()

urlpatterns = [
    path('', include(router.urls)),
    path('registrar_venta/', registrar_venta_api, name='registrar_venta_api'),
]