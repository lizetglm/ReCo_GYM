from django.db import models

# Create your models here.
class Actividades(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descripcion = models.TextField(blank=True)
    capacidad = models.PositiveIntegerField(null=True, blank=True)
    precio = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    schedule_file = models.FileField(upload_to="activities/schedules/", null=True, blank=True)  # pdf, etc.
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre