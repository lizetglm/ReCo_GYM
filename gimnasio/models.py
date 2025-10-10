from django.db import models
from datetime import date, timedelta

# Tabla Entrenador
class Entrenador(models.Model):
    id_entrenador = models.CharField(max_length=10, unique=True, primary_key=False)
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=50)
    telefono = models.CharField(max_length=15)
    fecha_contratacion = models.DateField()
    salario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.id_entrenador} - {self.nombre}"

# Tabla Socio
class Socio(models.Model):
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
            pago_reciente = self.pagos.filter(fecha_pago__gte=date.today() - timedelta(days=30)).exists()
            return pago_reciente
    activo = property(is_activo)

# Tabla Suscripcion Intenos
class Suscripcion(models.Model):
    id_suscripcion = models.CharField(max_length=10, unique=True, primary_key=False)
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

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.tipo == 'mensual':
                self.monto_total = 500
                self.fecha_fin = self.fecha_inicio + timedelta(days=30)
            elif self.tipo == 'trimestral':
                self.monto_total = 1500
                self.fecha_fin = self.fecha_inicio + timedelta(days=90)
            else:  # anual
                self.monto_total = 6000
                self.fecha_fin = self.fecha_inicio + timedelta(days=365)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_suscripcion} - Suscripción {self.get_tipo_display()} para {self.socio}"

# Tabla Pago
class Pago(models.Model):
    TIPOS_PAGO = [
        ('gimnasio', 'Suscripción Gimnasio'),
        ('clase', 'Pago por Clase'),
    ]
    
    id_pago = models.CharField(max_length=10, unique=True, primary_key=False)
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE, related_name='pagos')
    tipo_pago = models.CharField(max_length=10, choices=TIPOS_PAGO)
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.SET_NULL, null=True, blank=True)
    clase = models.ForeignKey('Clase', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_pago = models.DateField(auto_now_add=True)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    metodo = models.CharField(max_length=20, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.tipo_pago == 'gimnasio' and self.suscripcion:
            self.monto = self.suscripcion.monto_total
        elif self.tipo_pago == 'clase' and self.clase:
            self.monto = self.clase.precio
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_pago} - Pago de ${self.monto} por {self.tipo_pago} - {self.socio}"

# Modelo para Clase
class Clase(models.Model):
    id_clase = models.CharField(max_length=10, unique=True, primary_key=False)
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
    id_inscripcion = models.CharField(max_length=10, unique=True, primary_key=False)
    socio = models.ForeignKey(Socio, on_delete=models.CASCADE)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    pago_asociado = models.ForeignKey(Pago, on_delete=models.SET_NULL, null=True, blank=True)  # Obligatorio

    class Meta:
        unique_together = ('socio', 'clase')

    def __str__(self):
        return f"{self.id_inscripcion} - Inscripción de {self.socio} a {self.clase.nombre}"

    def save(self, *args, **kwargs):
        if not self.pago_asociado:
            raise ValueError("Todos los socios deben tener un pago asociado para inscribirse a clases.")
        if self.socio.tipo_socio == 'interno' and not self.socio.activo:
            raise ValueError("Los socios internos deben tener suscripción activa para acceder al gym.")
        super().save(*args, **kwargs)