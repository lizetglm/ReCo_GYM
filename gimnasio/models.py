from django.db import models
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User #///////////////////////
from django.conf import settings
from datetime import timedelta, datetime

# Tabla Entrenador
class Entrenador(models.Model):
    id_entrenador = models.CharField(max_length=100, unique=True, primary_key=False)
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    fecha_contratacion = models.DateField()
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.id_entrenador} - {self.nombre}"

# Tabla Socio ////////////////////////////////////////////
class Socio(models.Model):
    user = models.OneToOneField(
            settings.AUTH_USER_MODEL,  # O User, si lo importas directamente
            on_delete=models.CASCADE, 
            null=True,                 
            blank=True
        )    
    id_socio = models.CharField(max_length=10, unique=True, primary_key=False) 
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15)
    domicilio = models.CharField(max_length=200)
    fecha_registro = models.DateField(auto_now_add=True)
    TIPOS_SOCIO = [
        ('interno', 'Interno (Suscripción Gimnasio)'),
        ('externo', 'Externo (Pago por Clase)'),
    ]
    tipo_socio = models.CharField(max_length=10, choices=TIPOS_SOCIO, default='externo')
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo/Vencido'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')  # Puede calcularse dinamicamente

    def __str__(self):
        return f"{self.id_socio} - {self.nombre} {self.apellido} ({self.get_tipo_socio_display()})"

    def is_activo(self):
        if self.tipo_socio == 'interno':
            suscripcion_activa = self.suscripciones.filter(activa=True).first()
            return suscripcion_activa and suscripcion_activa.fecha_fin >= date.today()
        else:
            # Los socios externos no tienen 'pagos', tienen 'inscripcion_clase' y se asumen activos para poder registrar su próximo pago por clase.
            return True
    activo = property(is_activo)

# Tabla Suscripcion Intenos
class Suscripcion(models.Model):
    id_suscripcion = models.CharField(max_length=100, unique=True, primary_key=False)
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, limit_choices_to={'tipo_socio': 'interno'}, related_name='suscripciones')
    tipo = models.CharField(max_length=10, choices=[
        ('mensual', 'Mensual ($500)'),
        ('trimestral', 'Trimestral ($1500)'),
        ('anual', 'Anual ($6000)'),
    ])
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    movimiento_caja = models.OneToOneField(
        'CajaMovimiento', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='suscripcion_asociada'
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            if isinstance(self.fecha_inicio, str):
                try:
                    fecha_obj = datetime.strptime(self.fecha_inicio, '%Y-%m-%d').date()
                except ValueError:
                    raise ValueError("Formato de fecha inválido. Usa YYYY-MM-DD.")
            else:
                fecha_obj = self.fecha_inicio

            # === ASIGNAR MONTO Y FECHA FIN ===
            if self.tipo == 'mensual':
                self.monto_total = 500
                self.fecha_fin = fecha_obj + timedelta(days=30)
            elif self.tipo == 'trimestral':
                self.monto_total = 1500
                self.fecha_fin = fecha_obj + timedelta(days=90)
            elif self.tipo == 'anual':
                self.monto_total = 6000
                self.fecha_fin = fecha_obj + timedelta(days=365)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_suscripcion} - Suscripción {self.get_tipo_display()} para {self.socio}"



# Modelo para Clase
class Clase(models.Model):
    id_clase = models.CharField(max_length=100, unique=True, primary_key=False)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.IntegerField(default=60)
    entrenador = models.ForeignKey(Entrenador, on_delete=models.CASCADE)
    max_participantes = models.IntegerField(default=20)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    participantes = models.ManyToManyField(Socio, blank=True, related_name='clases_inscritas')

    def __str__(self):
        return f"{self.id_clase} - {self.nombre} - {self.fecha_hora} ({self.entrenador.nombre}) - ${self.precio}"

    @property
    def participantes_actuales(self):
        return self.participantes.count()

# Modelo para InscripcionClase
class InscripcionClase(models.Model):
    id_inscripcion = models.CharField(max_length=100, unique=True, primary_key=False)
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    movimiento_caja = models.OneToOneField( 
        'CajaMovimiento', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='inscripcion_clase_asociada'
    )

    class Meta:
        unique_together = ('socio', 'clase')

    def __str__(self):
        return f"{self.id_inscripcion} - Inscripción de {self.socio} a {self.clase.nombre}"

    def save(self, *args, **kwargs):
        if self.socio.tipo_socio == 'interno' and not self.socio.activo:
            raise ValueError("Los socios internos deben tener suscripción activa para acceder al gym.")
        super().save(*args, **kwargs)

class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


class Caja(models.Model):
    METODOS = (
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
    )
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    metodo_pago = models.CharField(max_length=20, choices=METODOS, default="efectivo")
    cliente = models.CharField(max_length=120, blank=True)
    observacion = models.TextField(blank=True)

    def __str__(self):
        return f"Caja #{self.pk} - {self.fecha:%d/%m/%Y %H:%M} - ${self.total}"


class VentaItem(models.Model):
    venta = models.ForeignKey(Caja, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x{self.cantidad}"


class CajaMovimiento(models.Model):
    METODOS = [
        ("efectivo", "Efectivo"),
        ("tarjeta", "Tarjeta"),
        ("transferencia", "Transferencia"),
    ]
    TIPOS = [
        ("producto", "Venta de productos"),
        ("mensualidad", "Mensualidad"),
        ("clase", "Clase"),
        ("otro", "Otro"),
    ]

    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=20, choices=TIPOS, default="producto")
    descripcion = models.CharField(max_length=200, blank=True, default="")
    metodo_pago = models.CharField(max_length=20, choices=METODOS, default="efectivo")
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Referencia a venta de productos (Ticket)
    venta = models.ForeignKey('Caja', null=True, blank=True, on_delete=models.SET_NULL, related_name="mov_caja")
    
    # Referencias a la fuente de pago (para registrar quién paga y qué paga)
    socio = models.ForeignKey('Socio', null=True, blank=True, on_delete=models.SET_NULL, related_name='mov_caja_socio')
    
    # Referencia a la Suscripción (si es pago de mensualidad)
    suscripcion = models.OneToOneField(Suscripcion, null=True, blank=True, on_delete=models.SET_NULL, related_name='pago_suscripcion')
    
    # Referencia a la InscripciónClase (si es pago por clase)
    inscripcion_clase = models.OneToOneField(InscripcionClase, null=True, blank=True, on_delete=models.SET_NULL, related_name='pago_clase')


    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Movimiento de caja'
        verbose_name_plural = 'Movimientos de caja'

    def __str__(self):
        return f"{self.get_tipo_display()} - ${self.monto:.2f} ({self.get_metodo_pago_display()})"