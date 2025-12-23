"""
Management command para limpiar datos de prueba del sistema.
Elimina todos los registros creados por cargar_datos_prueba.py, excepto Regiones, Comunas y Categorías.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from mi_condominio.models import (
    Condominio, Usuario, Reunion, Incidencia, Bitacora,
    EvidenciaIncidencia, Amonestacion, ChatSession, ChatMessage
)


class Command(BaseCommand):
    help = 'Elimina todos los datos de prueba del sistema (excepto Regiones, Comunas y Categorías)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirmar',
            action='store_true',
            help='Confirma la eliminación de datos (requerido para ejecutar)',
        )

    def handle(self, *args, **options):
        if not options['confirmar']:
            self.stdout.write(self.style.WARNING(
                '\n⚠️  ADVERTENCIA: Este comando eliminará TODOS los datos de prueba.\n'
                'Para ejecutar, usa: python manage.py limpiar_datos_prueba --confirmar\n'
            ))
            return

        self.stdout.write(self.style.WARNING('\n🗑️  Iniciando eliminación de datos de prueba...\n'))

        # Contar registros antes de eliminar
        stats_antes = {
            'Condominios': Condominio.objects.count(),
            'Usuarios': Usuario.objects.count(),
            'Reuniones': Reunion.objects.count(),
            'Incidencias': Incidencia.objects.count(),
            'Bitácoras': Bitacora.objects.count(),
            'Evidencias': EvidenciaIncidencia.objects.count(),
            'Amonestaciones': Amonestacion.objects.count(),
            'Sesiones Chat': ChatSession.objects.count(),
            'Mensajes Chat': ChatMessage.objects.count(),
        }

        self.stdout.write('Registros antes de limpiar:')
        for modelo, count in stats_antes.items():
            self.stdout.write(f'  - {modelo}: {count}')

        # Eliminar en orden correcto (respetando dependencias)
        try:
            # 1. Chat (sin dependencias externas)
            ChatMessage.objects.all().delete()
            ChatSession.objects.all().delete()

            # 2. Evidencias (depende de Incidencias)
            EvidenciaIncidencia.objects.all().delete()

            # 3. Bitácoras (depende de Incidencias)
            Bitacora.objects.all().delete()

            # 4. Amonestaciones (depende de Usuarios)
            Amonestacion.objects.all().delete()

            # 5. Incidencias (depende de Usuarios y Condominios)
            Incidencia.objects.all().delete()

            # 6. Reuniones (depende de Condominios)
            Reunion.objects.all().delete()

            # 7. Usuarios (depende de Condominios)
            # Eliminar usuarios Django asociados
            usuarios = Usuario.objects.filter(user__isnull=False)
            django_users_ids = list(usuarios.values_list('user_id', flat=True))
            Usuario.objects.all().delete()
            User.objects.filter(id__in=django_users_ids).delete()

            # 8. Condominios (sin dependencias)
            Condominio.objects.all().delete()

            self.stdout.write(self.style.SUCCESS('\n✅ Datos eliminados exitosamente!\n'))

            # Mostrar estadísticas finales
            stats_despues = {
                'Condominios': Condominio.objects.count(),
                'Usuarios': Usuario.objects.count(),
                'Reuniones': Reunion.objects.count(),
                'Incidencias': Incidencia.objects.count(),
                'Bitácoras': Bitacora.objects.count(),
                'Evidencias': EvidenciaIncidencia.objects.count(),
                'Amonestaciones': Amonestacion.objects.count(),
                'Sesiones Chat': ChatSession.objects.count(),
                'Mensajes Chat': ChatMessage.objects.count(),
            }

            self.stdout.write('Registros después de limpiar:')
            for modelo, count in stats_despues.items():
                self.stdout.write(f'  - {modelo}: {count}')

            # Mostrar lo que NO se eliminó
            self.stdout.write(self.style.SUCCESS(
                '\n📌 Datos preservados:'
                '\n  - Regiones'
                '\n  - Comunas'
                '\n  - Categorías de Incidencias'
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error al eliminar datos: {str(e)}\n'))
