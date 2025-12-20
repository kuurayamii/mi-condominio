"""
Modelo de Reunion.

Este módulo contiene el modelo Reunion que representa las reuniones
programadas para los condominios.
"""

from django.db import models
from .condominio import Condominio


class Reunion(models.Model):
    """
    Reuniones programadas para los condominios.

    Este modelo gestiona las reuniones que se realizan en cada condominio,
    almacenando información sobre la fecha, lugar, motivo y acta de cada reunión.
    Permite llevar un registro histórico de todas las reuniones realizadas.
    """

    class TipoReunion(models.TextChoices):
        ORDINARIA = 'ORDINARIA', 'Ordinaria'
        EXTRAORDINARIA = 'EXTRAORDINARIA', 'Extraordinaria'
        INFORMATIVA = 'INFORMATIVA', 'Informativa'

    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name='reuniones',
        help_text='Condominio asociado'
    )

    tipo_reunion = models.CharField(
        max_length=15,
        choices=TipoReunion.choices,
        help_text='Tipo de reunión'
    )

    nombre_reunion = models.CharField(
        max_length=20,
        help_text='Nombre de la reunión'
    )

    fecha_reunion = models.DateField(
        help_text='Fecha programada'
    )

    lugar_reunion = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        help_text='Lugar de realización'
    )

    motivo_reunion = models.TextField(
        blank=True,
        null=True,
        help_text='Motivo o temática'
    )

    acta_reunion_url = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text='URL del acta de la reunión'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reuniones'
        verbose_name = 'Reunión'
        verbose_name_plural = 'Reuniones'
        ordering = ['-fecha_reunion']

    def __str__(self):
        return f"{self.nombre_reunion} - {self.fecha_reunion}"
