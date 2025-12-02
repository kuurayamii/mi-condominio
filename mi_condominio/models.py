from django.db import models

from django.core.validators import RegexValidator


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
        #validators=[rut_validator],
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

    contrasena_hash = models.CharField(
        max_length=255,
        help_text='Contraseña cifrada'
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


class EvidenciaIncidencia(models.Model):
    """
    Evidencias asociadas a incidencias.

    Este modelo almacena las evidencias multimedia (imágenes, videos, documentos, etc.)
    que respaldan una incidencia reportada. Permite a los usuarios adjuntar pruebas
    visuales o documentales para facilitar la resolución del problema.
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

    url_archivo_evidencia = models.URLField(
        max_length=500,
        help_text='URL del archivo'
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
