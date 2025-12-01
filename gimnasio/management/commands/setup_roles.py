from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from gimnasio.models import Socio, Clase, Entrenador, InscripcionClase, CajaMovimiento, Producto

class Command(BaseCommand):
    help = 'Configura los grupos de usuarios y asigna permisos iniciales'

    def handle(self, *args, **options):
        self.stdout.write('Configurando roles y permisos...')

        # 1. Crear Grupos
        grupo_admins, created_admin = Group.objects.get_or_create(name='Administradores')
        grupo_socios, created_socio = Group.objects.get_or_create(name='Socios')

        if created_admin:
            self.stdout.write(self.style.SUCCESS('Grupo "Administradores" creado.'))
        if created_socio:
            self.stdout.write(self.style.SUCCESS('Grupo "Socios" creado.'))

        # 2. Obtener Permisos de la app 'gimnasio'
        # Lista de modelos que gestionan los administradores
        modelos_admin = [Socio, Clase, Entrenador, InscripcionClase, CajaMovimiento, Producto]
        
        permisos_admin = []
        for modelo in modelos_admin:
            content_type = ContentType.objects.get_for_model(modelo)
            perms = Permission.objects.filter(content_type=content_type)
            permisos_admin.extend(perms)

        # 3. Asignar permisos al grupo Administradores
        grupo_admins.permissions.set(permisos_admin)
        self.stdout.write(self.style.SUCCESS(f'Se asignaron {len(permisos_admin)} permisos al grupo "Administradores".'))

        # 4. Asignar permisos al grupo Socios (Opcional: Lectura básica si fuera necesario)
        # Por ahora, los socios solo necesitan estar autenticados, pero dejamos el grupo listo.
        # Ejemplo: Si quisieras que vieran clases pero no editaran:
        # ct_clase = ContentType.objects.get_for_model(Clase)
        # perm_view_clase = Permission.objects.get(content_type=ct_clase, codename='view_clase')
        # grupo_socios.permissions.add(perm_view_clase)
        
        # 5. Asignar usuarios existentes a los grupos
        users = User.objects.all()
        count_admins = 0
        count_socios = 0

        for user in users:
            if user.is_superuser:
                # Los superusuarios no necesitan grupo, pero pueden estar si se desea.
                pass
            elif user.is_staff:
                grupo_admins.user_set.add(user)
                count_admins += 1
            else:
                # Asumimos que si no es staff, es socio
                grupo_socios.user_set.add(user)
                count_socios += 1
        
        self.stdout.write(self.style.SUCCESS(f'Usuarios existentes asignados: {count_admins} a Administradores, {count_socios} a Socios.'))
        self.stdout.write(self.style.SUCCESS('¡Configuración de roles completada con éxito!'))
