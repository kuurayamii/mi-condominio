"""
Modelo de Region.

Este módulo contiene el modelo Region que representa las regiones
administrativas de Chile.
"""

from django.db import models


class Region(models.Model):
    """
    Regiones administrativas de Chile.

    Este modelo almacena las 16 regiones de Chile para ser utilizadas
    en la gestión de ubicaciones de condominios y otras entidades.
    """

    codigo = models.CharField(
        max_length=5,
        unique=True,
        help_text='Código de la región (ej: RM, V, VIII)'
    )

    nombre = models.CharField(
        max_length=100,
        unique=True,
        help_text='Nombre completo de la región'
    )

    numero_romano = models.CharField(
        max_length=5,
        blank=True,
        null=True,
        help_text='Número romano de la región (ej: I, II, III)'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'regiones'
        verbose_name = 'Región'
        verbose_name_plural = 'Regiones'
        ordering = ['codigo']

    def __str__(self):
        return self.nombre
