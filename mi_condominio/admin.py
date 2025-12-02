from django.contrib import admin
from .models import (
    Condominio,
    CategoriaIncidencia,
    Reunion,
    Usuario,
    Incidencia,
    Bitacora,
    EvidenciaIncidencia,
    Amonestacion
)


@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'comuna', 'region', 'mail_contacto']
    search_fields = ['nombre', 'rut', 'comuna']
    list_filter = ['region', 'comuna']
    ordering = ['nombre']


@admin.register(CategoriaIncidencia)
class CategoriaIncidenciaAdmin(admin.ModelAdmin):
    list_display = ['nombre_categoria_incidencia']
    search_fields = ['nombre_categoria_incidencia']
    ordering = ['nombre_categoria_incidencia']


@admin.register(Reunion)
class ReunionAdmin(admin.ModelAdmin):
    list_display = ['nombre_reunion', 'condominio', 'tipo_reunion', 'fecha_reunion', 'lugar_reunion']
    search_fields = ['nombre_reunion', 'condominio__nombre']
    list_filter = ['tipo_reunion', 'fecha_reunion', 'condominio']
    date_hierarchy = 'fecha_reunion'
    ordering = ['-fecha_reunion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('condominio', 'tipo_reunion', 'nombre_reunion')
        }),
        ('Detalles de la Reunión', {
            'fields': ('fecha_reunion', 'lugar_reunion', 'motivo_reunion')
        }),
        ('Documentación', {
            'fields': ('acta_reunion_url',)
        }),
    )


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['nombres', 'apellido', 'rut', 'correo', 'tipo_usuario', 'estado_cuenta', 'condominio']
    search_fields = ['nombres', 'apellido', 'rut', 'correo']
    list_filter = ['tipo_usuario', 'estado_cuenta', 'genero', 'condominio']
    ordering = ['apellido', 'nombres']

    fieldsets = (
        ('Información Personal', {
            'fields': ('nombres', 'apellido', 'rut', 'genero', 'residencia')
        }),
        ('Información de Contacto', {
            'fields': ('correo',)
        }),
        ('Información del Sistema', {
            'fields': ('condominio', 'tipo_usuario', 'estado_cuenta')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']


@admin.register(Incidencia)
class IncidenciaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'condominio', 'tipo_incidencia', 'estado', 'prioridad', 'fecha_reporte', 'usuario_reporta']
    search_fields = ['titulo', 'descripcion', 'condominio__nombre']
    list_filter = ['estado', 'prioridad', 'tipo_incidencia', 'condominio', 'fecha_reporte']
    date_hierarchy = 'fecha_reporte'
    ordering = ['-fecha_reporte', '-prioridad']

    fieldsets = (
        ('Información Básica', {
            'fields': ('condominio', 'tipo_incidencia', 'titulo', 'descripcion')
        }),
        ('Estado y Prioridad', {
            'fields': ('estado', 'prioridad')
        }),
        ('Ubicación', {
            'fields': ('direccion_condominio_incidencia', 'ubicacion_latitud_reporte', 'ubicacion_longitud_reporte'),
            'classes': ('collapse',)
        }),
        ('Seguimiento', {
            'fields': ('usuario_reporta', 'fecha_cierre')
        }),
    )

    readonly_fields = ['fecha_reporte', 'created_at', 'updated_at']


@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ['incidencia', 'accion', 'fecha_bitacora']
    search_fields = ['detalle', 'accion', 'incidencia__titulo']
    list_filter = ['fecha_bitacora', 'incidencia']
    date_hierarchy = 'fecha_bitacora'
    ordering = ['-fecha_bitacora']

    fieldsets = (
        ('Incidencia', {
            'fields': ('incidencia',)
        }),
        ('Detalles', {
            'fields': ('accion', 'detalle')
        }),
    )

    readonly_fields = ['fecha_bitacora', 'created_at']


@admin.register(EvidenciaIncidencia)
class EvidenciaIncidenciaAdmin(admin.ModelAdmin):
    list_display = ['incidencia', 'tipo_archivo_evidencia', 'url_archivo_evidencia', 'created_at']
    search_fields = ['incidencia__titulo', 'url_archivo_evidencia']
    list_filter = ['tipo_archivo_evidencia', 'incidencia']
    ordering = ['-created_at']

    fieldsets = (
        ('Incidencia', {
            'fields': ('incidencia',)
        }),
        ('Evidencia', {
            'fields': ('tipo_archivo_evidencia', 'url_archivo_evidencia')
        }),
    )

    readonly_fields = ['created_at']


@admin.register(Amonestacion)
class AmonestacionAdmin(admin.ModelAdmin):
    list_display = ['nombre_amonestado', 'apellidos_amonestado', 'rut_amonestado', 'tipo_amonestacion', 'motivo', 'fecha_amonestacion', 'usuario_reporta']
    search_fields = ['nombre_amonestado', 'apellidos_amonestado', 'rut_amonestado', 'motivo_detalle']
    list_filter = ['tipo_amonestacion', 'motivo', 'fecha_amonestacion']
    date_hierarchy = 'fecha_amonestacion'
    ordering = ['-fecha_amonestacion']

    fieldsets = (
        ('Datos del Amonestado', {
            'fields': ('nombre_amonestado', 'apellidos_amonestado', 'rut_amonestado', 'numero_departamento')
        }),
        ('Tipo y Motivo', {
            'fields': ('tipo_amonestacion', 'motivo', 'motivo_detalle')
        }),
        ('Fechas', {
            'fields': ('fecha_amonestacion', 'fecha_limite_pago')
        }),
        ('Usuario que Reporta', {
            'fields': ('usuario_reporta',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']
