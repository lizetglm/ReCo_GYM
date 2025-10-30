from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Producto, Caja, VentaItem, CajaMovimiento

from .models import Entrenador, Clase, Socio, Suscripcion # Cambiado: Import Socio en lugar de PerfilMiembro
from .serializers import (  # Asume que tienes serializers actualizados
    EntrenadorSerializer,
    ClaseSerializer,
    SocioSerializer,
    SuscripcionSerializer,
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
    serializer_class = SocioSerializer


class SuscripcionViewSet(BaseGymViewSet):
    queryset = Suscripcion.objects.select_related('socio').order_by('id')
    serializer_class = SuscripcionSerializer

# Importa las clases necesarias
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
# Importa tus modelos y utilidades...
import json
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404
# from .models import Producto, Caja, VentaItem, CajaMovimiento, etc.

class RegistrarVentaAPIView(APIView):

    def post(self, request, *args, **kwargs):
        try:
            data = request.data
        except (json.JSONDecodeError, AttributeError):
                return Response({'error': 'Cuerpo de petición JSON inválido.'}, status=status.HTTP_400_BAD_REQUEST)
        
        metodo = data.get("metodo_pago", "efectivo")
        cliente = data.get("cliente", "")
        obs = data.get("observacion", "")
        items_data = data.get("items", [])
        
        items = []
        total = Decimal("0.00")

        try:
            with transaction.atomic():
                # 2. Validar y calcular el total
                for item_data in items_data:
                    pid = item_data.get("producto_id")
                    cant = int(item_data.get("cantidad", 0))
                    punit = Decimal(item_data.get("precio_unitario", "0"))

                    if not pid or cant <= 0 or punit < 0:
                        continue
                    
                    producto = get_object_or_404(Producto, pk=pid)
                    subtotal = punit * cant
                    total += subtotal
                    items.append((producto, cant, punit, subtotal))

                if not items:
                    return Response({"error": "Agrega al menos un producto válido."}, status=status.HTTP_400_BAD_REQUEST)

                # CREAR LA VENTA (Caja) - MANTENER IGUAL
                venta = Caja.objects.create(
                    total=total, 
                    metodo_pago=metodo, 
                    cliente=cliente, 
                    observacion=obs
                )

                # CREAR LOS ITEMS de VENTA (VentaItem) - MANTENER IGUAL
                for producto, cant, punit, subtotal in items:
                    VentaItem.objects.create(
                        venta=venta, 
                        producto=producto, 
                        cantidad=cant, 
                        precio_unitario=punit, 
                        subtotal=subtotal
                    )

                # REGISTRAR MOVIMIENTO en CajaMovimiento - MANTENER IGUAL
                CajaMovimiento.objects.create(
                    tipo='producto',
                    descripcion=f'Venta #{venta.id} - {len(items)} item(s)',
                    metodo_pago=metodo,
                    monto=total,
                    venta=venta,
                )

            # Responder con el ID de la venta
            return Response({'success': True, 'venta_id': venta.id}, status=status.HTTP_201_CREATED)

        except (InvalidOperation, ValueError) as e:
            return Response({'error': f'Datos de entrada inválidos: {e}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f'Error interno del servidor: {e}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)