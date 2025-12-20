"""
Modelo de Condominio.

Este módulo contiene el modelo Condominio que representa las propiedades
administradas en el sistema.
"""

from django.db import models


class Condominio(models.Model):
    """
    Modelo que almacena los condominios que tiene bajo su poder el administrador
    para así saber desde qué parte vienen las incidencias e incluso las amonestaciones
    hacia los usuarios.
    """

    # Validador para RUT chileno (formato: XX.XXX.XXX-X)
    # rut_validator = RegexValidator(
    #     regex=r'^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$',
    #     message='El RUT debe tener el formato XX.XXX.XXX-X'
    # )

    rut = models.CharField(
        max_length=10,
        # validators=[rut_validator],
        unique=True,
        help_text='RUT del condominio (formato: XX.XXX.XXX-X)'
    )

    nombre = models.CharField(
        max_length=140,
        help_text='Nombre del condominio'
    )

    direccion = models.CharField(
        max_length=255,
        help_text='Dirección completa'
    )

    region = models.CharField(
        max_length=50,
        help_text='Región donde se ubica'
    )

    comuna = models.CharField(
        max_length=50,
        help_text='Comuna del condominio'
    )

    mail_contacto = models.EmailField(
        max_length=255,
        help_text='Correo de contacto'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'condominios'
        verbose_name = 'Condominio'
        verbose_name_plural = 'Condominios'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} - {self.comuna}"
