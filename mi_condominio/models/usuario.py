"""
Modelo de Usuario.

Este módulo contiene el modelo Usuario que representa a los usuarios
del sistema (administradores, supervisores, conserjes).
"""

from django.db import models
from django.contrib.auth.models import User
from .condominio import Condominio


class Usuario(models.Model):
    """
    Usuarios del sistema de gestión de condominios.

    Este modelo representa a los usuarios que interactúan con el sistema,
    que pueden ser administradores, supervisores o conserjes. Cada usuario
    está asociado a un condominio específico y tiene credenciales de acceso
    cifradas para garantizar la seguridad del sistema.
    """

    class Genero(models.TextChoices):
        MASCULINO = 'M', 'Masculino'
        FEMENINO = 'F', 'Femenino'
        OTRO = 'O', 'Otro'
        PREFIERO_NO_DECIR = 'N', 'Prefiero no decir'

    class TipoUsuario(models.TextChoices):
        ADMINISTRADOR = 'ADMIN', 'Administrador'
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        CONSERJE = 'CONSERJE', 'Conserje'

    class EstadoCuenta(models.TextChoices):
        ACTIVO = 'ACTIVO', 'Activo'
        INACTIVO = 'INACTIVO', 'Inactivo'

    # Vinculación con User de Django para autenticación
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='perfil_usuario',
        null=True,
        blank=True,
        help_text='Usuario de Django para autenticación'
    )

    condominio = models.ForeignKey(
        Condominio,
        on_delete=models.CASCADE,
        related_name='usuarios',
        help_text='Condominio asociado'
    )

    nombres = models.CharField(
        max_length=200,
        help_text='Nombres del usuario'
    )

    apellido = models.CharField(
        max_length=200,
        help_text='Apellidos del usuario'
    )

    genero = models.CharField(
        max_length=1,
        choices=Genero.choices,
        blank=True,
        null=True,
        help_text='Género del usuario'
    )

    rut = models.CharField(
        max_length=10,
        unique=True,
        help_text='RUT del usuario'
    )

    correo = models.EmailField(
        max_length=200,
        unique=True,
        help_text='Correo del usuario'
    )

    residencia = models.TextField(
        blank=True,
        null=True,
        help_text='Dirección de residencia'
    )

    tipo_usuario = models.CharField(
        max_length=10,
        choices=TipoUsuario.choices,
        help_text='Rol del usuario'
    )

    estado_cuenta = models.CharField(
        max_length=10,
        choices=EstadoCuenta.choices,
        default=EstadoCuenta.ACTIVO,
        help_text='Estado de la cuenta'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['apellido', 'nombres']

    def set_password(self, raw_password):
        """Establece la contraseña hasheada"""
        from django.contrib.auth.hashers import make_password
        self.contrasena_hash = make_password(raw_password)

    def check_password(self, raw_password):
        """Verifica la contraseña"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_password, self.contrasena_hash)

    def __str__(self):
        return f"{self.nombres} {self.apellido} ({self.tipo_usuario})"
