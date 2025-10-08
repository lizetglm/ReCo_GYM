from django.db import models

# Create your models here.
class Membresias(models.Model):
    socio = models.ForeignKey("socios.Socios", on_delete=models.CASCADE, related_name="memberships")
    actividad = models.ForeignKey("actividades.Actividades", on_delete=models.CASCADE, related_name="memberships")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("socio", "actividad", "fecha_inicio")

    def __str__(self):
        return f"{self.socio} -> {self.actividad} ({self.fecha_inicio})"

class Asistencias(models.Model):
    socio = models.ForeignKey("socios.Socios", on_delete=models.CASCADE)
    actividad = models.ForeignKey("actividades.Actividades", on_delete=models.CASCADE)
    fecha = models.DateField()
    presente = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
