"""
Modelos de Incidencia y CategoriaIncidencia.

Este módulo contiene los modelos relacionados con las incidencias
reportadas en los condominios y sus categorías.
"""

from django.db import models
from .condominio import Condominio
from .usuario import Usuario


class CategoriaIncidencia(models.Model):
    """
    Catálogo de categorías de incidencias.

    Este modelo clasifica las diferentes tipos de incidencias que pueden ocurrir
    en un condominio (mantenimiento, seguridad, limpieza, ruidos, etc.).
    """

    nombre_categoria_incidencia = models.CharField(
        max_length=30,
        unique=True,
        help_text='Nombre de la categoría'
    )

    class Meta:
        db_table = 'categoria_incidencias'
        verbose_name = 'Categoría de Incidencia'
        verbose_name_plural = 'Categorías de Incidencias'
        ordering = ['nombre_categoria_incidencia']

    def __str__(self):
        return self.nombre_categoria_incidencia


class Incidencia(models.Model):
    """
    Incidencias reportadas en los condominios.

    Este modelo gestiona todas las incidencias o problemas reportados dentro
    de un condominio. Incluye información sobre el tipo de incidencia, su estado,
    prioridad, ubicación geográfica y seguimiento completo desde el reporte
    hasta su cierre. Permite a los administradores dar seguimiento a los problemas
    y mantener un historial de resolución.
    """

    class Estado(models.TextChoices):
        PENDIENTE = 'PENDIENTE', 'Pendiente'
        EN_PROCESO = 'EN_PROCESO', 'En Proceso'
        RESUELTA = 'RESUELTA', 'Resuelta'
        CERRADA = 'CERRADA', 'Cerrada'
        CANCELADA = 'CANCELADA', 'Cancelada'

    class Prioridad(models.TextChoices):
        BAJA = 'BAJA', 'Baja'
        MEDIA = 'MEDIA', 'Media'
        ALTA = 'ALTA', 'Alta'
        URGENTE = 'URGENTE', 'Urgente'

    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name='incidencias',
        help_text='Condominio asociado'
    )

    tipo_incidencia = models.ForeignKey(
        CategoriaIncidencia,
        on_delete=models.PROTECT,
        related_name='incidencias',
        help_text='Categoría de la incidencia'
    )

    titulo = models.CharField(
        max_length=160,
        help_text='Título de la incidencia'
    )

    descripcion = models.TextField(
        blank=True,
        null=True,
        help_text='Descripción detallada'
    )

    estado = models.CharField(
        max_length=15,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
        help_text='Estado de la incidencia'
    )

    ubicacion_latitud_reporte = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Latitud del reporte'
    )

    ubicacion_longitud_reporte = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text='Longitud del reporte'
    )

    direccion_condominio_incidencia = models.CharField(
        max_length=180,
        blank=True,
        null=True,
        help_text='Dirección asociada'
    )

    usuario_reporta = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='incidencias_reportadas',
        help_text='Usuario que reporta'
    )

    fecha_reporte = models.DateField(
        auto_now_add=True,
        help_text='Fecha del reporte'
    )

    fecha_cierre = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha de cierre'
    )

    prioridad = models.CharField(
        max_length=10,
        choices=Prioridad.choices,
        default=Prioridad.MEDIA,
        help_text='Prioridad asignada'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'incidencias'
        verbose_name = 'Incidencia'
        verbose_name_plural = 'Incidencias'
        ordering = ['-fecha_reporte', '-prioridad']

    def __str__(self):
        return f"{self.titulo} - {self.estado}"
