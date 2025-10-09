from django.db import models
from django.contrib.auth.models import User

# Modelo para Entrenador: Uno puede dar muchas clases
class Entrenador(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=50)  # e.g., 'Cardio', 'Pesas'
    telefono = models.CharField(max_length=15)
    fecha_contratacion = models.DateField()

    def __str__(self):
        return self.nombre

# Modelo para Clase: Relacionada a un entrenador, y miembros pueden inscribirse
class Clase(models.Model):
    nombre = models.CharField(max_length=100)  # e.g., 'Yoga Matutino'
    descripcion = models.TextField()
    fecha_hora = models.DateTimeField()
    duracion_minutos = models.IntegerField(default=60)
    entrenador = models.ForeignKey(Entrenador, on_delete=models.CASCADE)  # Si borras entrenador, borra clases
    max_participantes = models.IntegerField(default=20)
    participantes = models.ManyToManyField(User, blank=True)  # Miembros inscritos (usuarios auth)

    def __str__(self):
        return f"{self.nombre} - {self.fecha_hora}"

class PerfilMiembro(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)  # Relación 1:1 con User
    fecha_registro = models.DateField(auto_now_add=True)
    peso = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Para tracking fitness
    telefono = models.CharField(max_length=15)

    def __str__(self):
        return self.usuario.username

# Modelo para Suscripción: Relacionada a un miembro
class Suscripcion(models.Model):
    TIPOS_SUSCRIPCION = [
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
    ]
    miembro = models.ForeignKey(PerfilMiembro, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPOS_SUSCRIPCION)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Suscripción {self.tipo} para {self.miembro}"

# Modelo para Pago: Relacionado a una suscripción
class Pago(models.Model):
    suscripcion = models.ForeignKey(Suscripcion, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(auto_now_add=True)
    metodo = models.CharField(max_length=20, default='Tarjeta')  # e.g., 'Efectivo', 'Tarjeta'

    def __str__(self):
        return f"Pago de ${self.monto} para {self.suscripcion}"