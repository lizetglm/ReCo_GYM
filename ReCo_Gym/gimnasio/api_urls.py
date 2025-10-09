from rest_framework import routers

from .api_views import (
    EntrenadorViewSet,
    ClaseViewSet,
    PerfilMiembroViewSet,
    SuscripcionViewSet,
    PagoViewSet,
)

router = routers.DefaultRouter()
router.register(r'entrenadores', EntrenadorViewSet)
router.register(r'clases', ClaseViewSet)
router.register(r'perfiles', PerfilMiembroViewSet)
router.register(r'suscripciones', SuscripcionViewSet)
router.register(r'pagos', PagoViewSet)

urlpatterns = router.urls
