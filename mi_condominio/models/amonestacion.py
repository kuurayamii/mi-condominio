"""
Modelo de Amonestacion.

Este módulo contiene el modelo Amonestacion que gestiona las sanciones
aplicadas a los residentes de los condominios.
"""

from django.db import models
from .usuario import Usuario


class Amonestacion(models.Model):
    """
    Amonestaciones aplicadas en los condominios.

    Este modelo gestiona las sanciones o amonestaciones aplicadas a los residentes
    que incumplen las normas del condominio. Incluye información sobre el tipo
    de amonestación, el motivo, la persona sancionada y, en caso de multas,
    las fechas límite de pago.
    """

    class TipoAmonestacion(models.TextChoices):
        VERBAL = 'VERBAL', 'Verbal'
        ESCRITA = 'ESCRITA', 'Escrita'
        MULTA = 'MULTA', 'Multa'
        SUSPENSION = 'SUSPENSION', 'Suspensión de servicios'

    class MotivoAmonestacion(models.TextChoices):
        RUIDOS_MOLESTOS = 'RUIDOS_MOLESTOS', 'Ruidos molestos'
        USO_INDEBIDO_ESTACIONAMIENTOS = 'USO_INDEBIDO_ESTACIONAMIENTOS', 'Uso indebido de estacionamientos'
        DANO_BIEN_COMUN = 'DANO_BIEN_COMUN', 'Daño a bien común'
        MAL_USO_AREA_COMUN = 'MAL_USO_AREA_COMUN', 'Mal uso de área común'
        INCUMPLIMIENTO_NORMAS_SANITARIAS = 'INCUMPLIMIENTO_NORMAS_SANITARIAS', 'Incumplimiento de normas sanitarias'
        TENENCIA_IRRESPONSABLE = 'TENENCIA_IRRESPONSABLE', 'Tenencia irresponsable'
        MAL_USO_DUCTOS_BASURA = 'MAL_USO_DUCTOS_BASURA', 'Mal uso de ductos de basura'
        ARRIENDO_ILEGAL = 'ARRIENDO_ILEGAL', 'Arriendo ilegal'
        INCUMPLIMIENTO_OBRAS_REMODELACIONES = 'INCUMPLIMIENTO_OBRAS_REMODELACIONES', 'Incumplimiento en obras y remodelaciones'
        IMPEDIMENTO_LABORES_ADMINISTRATIVAS = 'IMPEDIMENTO_LABORES_ADMINISTRATIVAS', 'Impedimento de labores administrativas'
        SEGURIDAD = 'SEGURIDAD', 'Seguridad'
        OTRO = 'OTRO', 'Otro motivo'

    tipo_amonestacion = models.CharField(
        max_length=15,
        choices=TipoAmonestacion.choices,
        help_text='Tipo de amonestación'
    )

    motivo = models.CharField(
        max_length=40,
        choices=MotivoAmonestacion.choices,
        help_text='Motivo principal de la amonestación'
    )

    motivo_detalle = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text='Detalle adicional del motivo o especificar si seleccionó "Otro"'
    )

    fecha_amonestacion = models.DateField(
        help_text='Fecha aplicada'
    )

    nombre_amonestado = models.CharField(
        max_length=150,
        help_text='Nombre del sancionado'
    )

    apellidos_amonestado = models.CharField(
        max_length=150,
        help_text='Apellidos del sancionado'
    )

    rut_amonestado = models.CharField(
        max_length=10,
        help_text='RUT del sancionado'
    )

    numero_departamento = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        help_text='Número de departamento'
    )

    fecha_limite_pago = models.DateField(
        blank=True,
        null=True,
        help_text='Fecha límite de pago'
    )

    usuario_reporta = models.ForeignKey(
        Usuario,
        on_delete=models.PROTECT,
        related_name='amonestaciones_reportadas',
        help_text='Usuario que reporta'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'amonestaciones'
        verbose_name = 'Amonestación'
        verbose_name_plural = 'Amonestaciones'
        ordering = ['-fecha_amonestacion']

    def __str__(self):
        return f"{self.nombre_amonestado} {self.apellidos_amonestado} - {self.motivo}"
