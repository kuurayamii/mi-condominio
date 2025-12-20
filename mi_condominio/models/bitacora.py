"""
Modelo de Bitacora.

Este módulo contiene el modelo Bitacora que registra el seguimiento
de las incidencias.
"""

from django.db import models
from .incidencia import Incidencia


class Bitacora(models.Model):
    """
    Bitácoras de seguimiento de incidencias.

    Este modelo registra cada acción o actualización realizada sobre una incidencia,
    creando un historial detallado de seguimiento. Permite rastrear quién hizo qué
    y cuándo durante el proceso de resolución de una incidencia.
    """

    incidencia = models.ForeignKey(
        Incidencia,
        on_delete=models.CASCADE,
        related_name='bitacoras',
        help_text='Incidencia asociada'
    )

    detalle = models.TextField(
        blank=True,
        null=True,
        help_text='Detalle del registro'
    )

    accion = models.TextField(
        blank=True,
        null=True,
        help_text='Acción ejecutada'
    )

    fecha_bitacora = models.DateField(
        auto_now_add=True,
        help_text='Fecha del registro'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bitacoras'
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'
        ordering = ['-fecha_bitacora']

    def __str__(self):
        return f"Bitácora {self.id} - {self.incidencia.titulo}"
