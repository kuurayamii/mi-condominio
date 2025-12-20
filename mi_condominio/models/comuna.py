"""
Modelo de Comuna.

Este módulo contiene el modelo Comuna que representa las comunas
de Chile, asociadas a sus respectivas regiones.
"""

from django.db import models
from .region import Region


class Comuna(models.Model):
    """
    Comunas de Chile.

    Este modelo almacena todas las comunas del país, cada una asociada
    a una región específica mediante una relación ForeignKey.
    Relación: 1 Región puede tener N Comunas.
    """

    region = models.ForeignKey(
        Region,
        on_delete=models.PROTECT,
        related_name='comunas',
        help_text='Región a la que pertenece la comuna'
    )

    nombre = models.CharField(
        max_length=100,
        help_text='Nombre de la comuna'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comunas'
        verbose_name = 'Comuna'
        verbose_name_plural = 'Comunas'
        ordering = ['region', 'nombre']
        unique_together = [['region', 'nombre']]  # Una comuna no puede repetirse en la misma región

    def __str__(self):
        return self.nombre
