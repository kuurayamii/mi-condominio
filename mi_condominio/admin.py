from django.contrib import admin
from .models import (
    Region,
    Comuna,
    Condominio,
    CategoriaIncidencia,
    Reunion,
    Usuario,
    Incidencia,
    Bitacora,
    EvidenciaIncidencia,
    Amonestacion,
    ChatSession,
    ChatMessage
)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'numero_romano']
    search_fields = ['codigo', 'nombre']
    ordering = ['codigo']


@admin.register(Comuna)
class ComunaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'region']
    search_fields = ['nombre', 'region__nombre']
    list_filter = ['region']
    ordering = ['region', 'nombre']


@admin.register(Condominio)
class CondominioAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'rut', 'get_comuna', 'get_region', 'mail_contacto']
    search_fields = ['nombre', 'rut', 'comuna__nombre', 'region__nombre']
    list_filter = ['region', 'comuna__region']
    ordering = ['nombre']

    def get_region(self, obj):
        return obj.region.nombre if obj.region else '-'
    get_region.short_description = 'Región'
    get_region.admin_order_field = 'region__nombre'

    def get_comuna(self, obj):
        return obj.comuna.nombre if obj.comuna else '-'
    get_comuna.short_description = 'Comuna'
    get_comuna.admin_order_field = 'comuna__nombre'


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
    list_display = ['incidencia', 'tipo_archivo_evidencia', 'archivo_evidencia', 'created_at']
    search_fields = ['incidencia__titulo', 'archivo_evidencia']
    list_filter = ['tipo_archivo_evidencia', 'incidencia']
    ordering = ['-created_at']

    fieldsets = (
        ('Incidencia', {
            'fields': ('incidencia',)
        }),
        ('Evidencia', {
            'fields': ('tipo_archivo_evidencia', 'archivo_evidencia')
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


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'usuario', 'titulo', 'activa', 'created_at', 'updated_at']
    search_fields = ['titulo', 'usuario__nombres', 'usuario__apellido']
    list_filter = ['activa', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-updated_at']

    readonly_fields = ['created_at', 'updated_at']


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    fields = ['role', 'contenido', 'tokens_usados', 'created_at']
    readonly_fields = ['created_at']
    extra = 0
    can_delete = False


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sesion', 'role', 'preview_contenido', 'tokens_usados', 'created_at']
    search_fields = ['contenido', 'sesion__usuario__nombres']
    list_filter = ['role', 'created_at']
    ordering = ['-created_at']

    readonly_fields = ['created_at']

    def preview_contenido(self, obj):
        return obj.contenido[:100] + "..." if len(obj.contenido) > 100 else obj.contenido
    preview_contenido.short_description = 'Contenido'
