"""
Comando de Django para cargar categorías iniciales de incidencias.

Uso:
    python manage.py cargar_categorias
"""

from django.core.management.base import BaseCommand
from mi_condominio.models import CategoriaIncidencia


class Command(BaseCommand):
    help = 'Carga las categorías iniciales de incidencias más comunes en condominios'

    def handle(self, *args, **options):
        """
        Método principal que ejecuta el comando.
        """
        categorias_iniciales = [
            'Mantenimiento',
            'Seguridad',
            'Limpieza',
            'Ruidos Molestos',
            'Estacionamientos',
            'Áreas Comunes',
            'Mascotas',
            'Basura',
            'Iluminación',
            'Agua',
            'Electricidad',
            'Ascensores',
            'Portones y Accesos',
            'Jardines',
            'Piscina',
            'Quincho',
            'Gimnasio',
            'Convivencia',
            'Normativa',
            'Otros',
        ]

        self.stdout.write(self.style.SUCCESS('=== Cargando categorías iniciales ===\n'))

        categorias_creadas = 0
        categorias_existentes = 0

        for nombre in categorias_iniciales:
            categoria, created = CategoriaIncidencia.objects.get_or_create(
                nombre_categoria_incidencia=nombre
            )

            if created:
                categorias_creadas += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Creada: {nombre}')
                )
            else:
                categorias_existentes += 1
                self.stdout.write(
                    self.style.WARNING(f'- Ya existe: {nombre}')
                )

        # Resumen
        self.stdout.write('\n' + '=' * 50)
        self.stdout.write(self.style.SUCCESS(f'\nResumen:'))
        self.stdout.write(f'  • Categorías creadas: {categorias_creadas}')
        self.stdout.write(f'  • Categorías existentes: {categorias_existentes}')
        self.stdout.write(f'  • Total de categorías: {CategoriaIncidencia.objects.count()}')
        self.stdout.write('\n' + self.style.SUCCESS('✓ Proceso completado exitosamente'))
