"""
Modelo de Evidencia.

Este módulo contiene el modelo EvidenciaIncidencia y la función
evidencia_upload_path para gestionar archivos de evidencia.
"""

import os
from datetime import datetime
from django.db import models
from django.utils.text import slugify
from .incidencia import Incidencia


def evidencia_upload_path(instance, filename):
    """
    Genera la ruta de upload para archivos de evidencia.

    Estructura: evidencias/incidencia_{id}_{titulo_sanitizado}/{timestamp}_{filename}

    Ejemplo: evidencias/incidencia_15_fuga-de-agua/20231219_143025_foto.jpg
    """
    # Sanitizar el título de la incidencia (eliminar caracteres especiales, espacios, etc.)
    titulo_sanitizado = slugify(instance.incidencia.titulo)[:50]  # Limitar a 50 caracteres

    # ID de la incidencia
    incidencia_id = instance.incidencia.id

    # Timestamp para evitar colisiones de nombres
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Nombre del archivo original
    nombre_original = os.path.basename(filename)

    # Construir la ruta: evidencias/incidencia_{id}_{titulo}/{timestamp}_{filename}
    return f'evidencias/incidencia_{incidencia_id}_{titulo_sanitizado}/{timestamp}_{nombre_original}'


class EvidenciaIncidencia(models.Model):
    """
    Evidencias asociadas a incidencias.

    Este modelo almacena las evidencias multimedia (imágenes, videos, documentos, etc.)
    que respaldan una incidencia reportada. Permite a los usuarios adjuntar pruebas
    visuales o documentales para facilitar la resolución del problema.

    Los archivos se almacenan localmente en media/evidencias/ con estructura:
    evidencias/incidencia_{id}_{titulo}/{timestamp}_{nombre_archivo}

    Ejemplo: evidencias/incidencia_15_fuga-de-agua/20231219_143025_foto.jpg

    Preparado para migración futura a S3.
    """

    class TipoArchivo(models.TextChoices):
        IMAGEN = 'IMAGEN', 'Imagen'
        VIDEO = 'VIDEO', 'Video'
        DOCUMENTO = 'DOCUMENTO', 'Documento'
        AUDIO = 'AUDIO', 'Audio'
        OTRO = 'OTRO', 'Otro'

    incidencia = models.ForeignKey(
        Incidencia,
        on_delete=models.CASCADE,
        related_name='evidencias',
        help_text='Incidencia asociada'
    )

    archivo_evidencia = models.FileField(
        upload_to=evidencia_upload_path,
        max_length=500,
        blank=True,
        null=True,
        help_text='Archivo de evidencia (imagen, video, documento, etc.)'
    )

    tipo_archivo_evidencia = models.CharField(
        max_length=15,
        choices=TipoArchivo.choices,
        help_text='Tipo de evidencia'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'evidencias_incidencia'
        verbose_name = 'Evidencia de Incidencia'
        verbose_name_plural = 'Evidencias de Incidencias'
        ordering = ['-created_at']

    def __str__(self):
        return f"Evidencia {self.tipo_archivo_evidencia} - {self.incidencia.titulo}"

    @property
    def extension(self):
        """Retorna la extensión del archivo en minúsculas."""
        return os.path.splitext(self.archivo_evidencia.name)[1].lower()

    @property
    def es_imagen(self):
        """Verifica si el archivo es una imagen."""
        extensiones_imagen = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp']
        return self.extension in extensiones_imagen

    @property
    def es_video(self):
        """Verifica si el archivo es un video."""
        extensiones_video = ['.mp4', '.avi', '.mov', '.wmv', '.webm', '.mkv']
        return self.extension in extensiones_video

    @property
    def nombre_archivo(self):
        """Retorna solo el nombre del archivo sin la ruta."""
        return os.path.basename(self.archivo_evidencia.name)
