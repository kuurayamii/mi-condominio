"""
Herramientas MCP para el asistente de IA.
Estas funciones permiten al asistente interactuar con la base de datos.
"""

from datetime import datetime, timedelta
from django.db.models import Q, Count, Avg
from .models import (
    Condominio,
    Usuario,
    Incidencia,
    Bitacora,
    EvidenciaIncidencia,
    Amonestacion,
    Reunion,
    CategoriaIncidencia
)


# ==================== HERRAMIENTAS DE CONSULTA ====================

def get_incidencias_abiertas(condominio_id=None):
    """
    Obtiene todas las incidencias abiertas o en proceso.

    Args:
        condominio_id: ID opcional del condominio para filtrar

    Returns:
        dict con información de las incidencias abiertas
    """
    query = Incidencia.objects.exclude(estado__in=['CERRADA', 'CANCELADA'])

    if condominio_id:
        query = query.filter(condominio_id=condominio_id)

    incidencias = query.select_related('condominio', 'tipo_incidencia', 'usuario_reporta').order_by('-fecha_reporte')

    result = {
        'total': incidencias.count(),
        'incidencias': []
    }

    for inc in incidencias[:20]:  # Limit to first 20
        result['incidencias'].append({
            'id': inc.id,
            'titulo': inc.titulo,
            'descripcion': inc.descripcion,
            'estado': inc.get_estado_display(),
            'prioridad': inc.get_prioridad_display(),
            'categoria': inc.tipo_incidencia.nombre_categoria_incidencia if inc.tipo_incidencia else None,
            'condominio': inc.condominio.nombre if inc.condominio else None,
            'usuario_reporta': f"{inc.usuario_reporta.nombres} {inc.usuario_reporta.apellido}" if inc.usuario_reporta else None,
            'fecha_reporte': inc.fecha_reporte.strftime('%d/%m/%Y %H:%M') if inc.fecha_reporte else None,
            'direccion': inc.direccion_condominio_incidencia,
        })

    return result


def get_estadisticas_dashboard(condominio_id=None):
    """
    Obtiene las estadísticas principales del dashboard.

    Args:
        condominio_id: ID opcional del condominio para filtrar

    Returns:
        dict con estadísticas del sistema
    """
    condominios_query = Condominio.objects.all()
    usuarios_query = Usuario.objects.all()
    incidencias_query = Incidencia.objects.all()
    reuniones_query = Reunion.objects.all()

    if condominio_id:
        condominios_query = condominios_query.filter(id=condominio_id)
        usuarios_query = usuarios_query.filter(condominio_id=condominio_id)
        incidencias_query = incidencias_query.filter(condominio_id=condominio_id)
        reuniones_query = reuniones_query.filter(condominio_id=condominio_id)

    # Calcular estadísticas
    incidencias_abiertas = incidencias_query.exclude(estado__in=['CERRADA', 'CANCELADA']).count()

    stats = {
        'total_condominios': condominios_query.count(),
        'total_usuarios': usuarios_query.count(),
        'total_incidencias': incidencias_query.count(),
        'incidencias_abiertas': incidencias_abiertas,
        'total_reuniones': reuniones_query.count(),
        'incidencias_por_estado': {},
        'incidencias_por_prioridad': {},
        'categorias_mas_comunes': []
    }

    # Incidencias por estado
    for estado_code, estado_name in Incidencia.Estado.choices:
        count = incidencias_query.filter(estado=estado_code).count()
        stats['incidencias_por_estado'][estado_name] = count

    # Incidencias por prioridad
    for prioridad_code, prioridad_name in Incidencia.Prioridad.choices:
        count = incidencias_query.filter(prioridad=prioridad_code).count()
        stats['incidencias_por_prioridad'][prioridad_name] = count

    # Categorías más comunes (top 5)
    categorias = incidencias_query.values('tipo_incidencia__nombre_categoria_incidencia').annotate(
        total=Count('id')
    ).order_by('-total')[:5]

    stats['categorias_mas_comunes'] = [
        {'categoria': cat['tipo_incidencia__nombre_categoria_incidencia'], 'total': cat['total']}
        for cat in categorias
    ]

    return stats


def get_amonestaciones_recientes(dias=30, condominio_id=None):
    """
    Obtiene las amonestaciones de los últimos N días.

    Args:
        dias: Número de días hacia atrás (default: 30)
        condominio_id: ID opcional del condominio para filtrar

    Returns:
        dict con información de amonestaciones recientes
    """
    fecha_limite = datetime.now().date() - timedelta(days=dias)

    query = Amonestacion.objects.filter(fecha_amonestacion__gte=fecha_limite)

    if condominio_id:
        query = query.filter(usuario_reporta__condominio_id=condominio_id)

    amonestaciones = query.select_related('usuario_reporta').order_by('-fecha_amonestacion')

    result = {
        'total': amonestaciones.count(),
        'periodo_dias': dias,
        'amonestaciones': []
    }

    for amon in amonestaciones[:15]:  # Limit to first 15
        result['amonestaciones'].append({
            'id': amon.id,
            'nombre_amonestado': f"{amon.nombre_amonestado} {amon.apellidos_amonestado}",
            'rut': amon.rut_amonestado,
            'departamento': amon.numero_departamento,
            'tipo': amon.get_tipo_amonestacion_display(),
            'motivo': amon.get_motivo_display(),
            'detalle': amon.motivo_detalle,
            'fecha': amon.fecha_amonestacion.strftime('%d/%m/%Y'),
            'reportado_por': f"{amon.usuario_reporta.nombres} {amon.usuario_reporta.apellido}" if amon.usuario_reporta else None,
        })

    return result


def buscar_incidencias(termino_busqueda, condominio_id=None):
    """
    Busca incidencias por título o descripción.

    Args:
        termino_busqueda: Término a buscar
        condominio_id: ID opcional del condominio para filtrar

    Returns:
        dict con incidencias que coinciden con la búsqueda
    """
    query = Incidencia.objects.filter(
        Q(titulo__icontains=termino_busqueda) |
        Q(descripcion__icontains=termino_busqueda)
    )

    if condominio_id:
        query = query.filter(condominio_id=condominio_id)

    incidencias = query.select_related('condominio', 'tipo_incidencia', 'usuario_reporta').order_by('-fecha_reporte')[:10]

    return {
        'total_encontradas': query.count(),
        'incidencias': [
            {
                'id': inc.id,
                'titulo': inc.titulo,
                'descripcion': inc.descripcion,
                'estado': inc.get_estado_display(),
                'prioridad': inc.get_prioridad_display(),
                'fecha_reporte': inc.fecha_reporte.strftime('%d/%m/%Y') if inc.fecha_reporte else None,
            }
            for inc in incidencias
        ]
    }


def analizar_tendencias_incidencias(dias=90, condominio_id=None):
    """
    Analiza tendencias de incidencias en un período.

    Args:
        dias: Número de días a analizar (default: 90)
        condominio_id: ID opcional del condominio para filtrar

    Returns:
        dict con análisis de tendencias
    """
    fecha_limite = datetime.now().date() - timedelta(days=dias)

    query = Incidencia.objects.filter(fecha_reporte__gte=fecha_limite)

    if condominio_id:
        query = query.filter(condominio_id=condominio_id)

    # Categorías más frecuentes
    categorias_freq = query.values('tipo_incidencia__nombre_categoria_incidencia').annotate(
        total=Count('id')
    ).order_by('-total')[:10]

    # Incidencias por prioridad
    prioridades = {}
    for prioridad_code, prioridad_name in Incidencia.Prioridad.choices:
        prioridades[prioridad_name] = query.filter(prioridad=prioridad_code).count()

    # Tasa de resolución
    total_cerradas = query.filter(estado='CERRADA').count()
    total_incidencias = query.count()
    tasa_resolucion = (total_cerradas / total_incidencias * 100) if total_incidencias > 0 else 0

    return {
        'periodo_dias': dias,
        'total_incidencias': total_incidencias,
        'categorias_frecuentes': [
            {'categoria': cat['tipo_incidencia__nombre_categoria_incidencia'], 'total': cat['total']}
            for cat in categorias_freq
        ],
        'distribucion_prioridades': prioridades,
        'tasa_resolucion_porcentaje': round(tasa_resolucion, 2),
        'total_cerradas': total_cerradas,
        'total_abiertas': total_incidencias - total_cerradas,
    }


# ==================== FUNCIONES AUXILIARES DE BÚSQUEDA ====================

def buscar_condominio_por_nombre(nombre):
    """
    Busca un condominio por nombre (búsqueda flexible).

    Args:
        nombre: Nombre del condominio (puede ser parcial)

    Returns:
        dict con condominios encontrados
    """
    condominios = Condominio.objects.filter(nombre__icontains=nombre)

    return {
        'total_encontrados': condominios.count(),
        'condominios': [
            {
                'id': c.id,
                'nombre': c.nombre,
                'rut': c.rut,
                'direccion': c.direccion,
                'comuna': c.comuna.nombre if c.comuna else None,
                'region': c.region.nombre if c.region else None
            }
            for c in condominios[:10]
        ]
    }


def buscar_usuario_por_nombre(nombre=None, apellido=None, condominio_nombre=None):
    """
    Busca usuarios por nombre, apellido o condominio.

    Args:
        nombre: Nombre del usuario (opcional)
        apellido: Apellido del usuario (opcional)
        condominio_nombre: Nombre del condominio (opcional)

    Returns:
        dict con usuarios encontrados
    """
    query = Usuario.objects.all()

    if nombre:
        query = query.filter(nombres__icontains=nombre)
    if apellido:
        query = query.filter(apellido__icontains=apellido)
    if condominio_nombre:
        query = query.filter(condominio__nombre__icontains=condominio_nombre)

    usuarios = query.select_related('condominio')

    return {
        'total_encontrados': usuarios.count(),
        'usuarios': [
            {
                'id': u.id,
                'nombres': u.nombres,
                'apellido': u.apellido,
                'rut': u.rut,
                'tipo_usuario': u.get_tipo_usuario_display(),
                'condominio_id': u.condominio.id if u.condominio else None,
                'condominio_nombre': u.condominio.nombre if u.condominio else None
            }
            for u in usuarios[:10]
        ]
    }


def buscar_categoria_por_nombre(nombre):
    """
    Busca categorías de incidencia por nombre.

    Args:
        nombre: Nombre de la categoría (puede ser parcial)

    Returns:
        dict con categorías encontradas
    """
    categorias = CategoriaIncidencia.objects.filter(nombre_categoria_incidencia__icontains=nombre)

    return {
        'total_encontradas': categorias.count(),
        'categorias': [
            {
                'id': c.id,
                'nombre': c.nombre_categoria_incidencia
            }
            for c in categorias
        ]
    }


def listar_todos_condominios():
    """
    Lista todos los condominios del sistema.

    Returns:
        dict con todos los condominios
    """
    condominios = Condominio.objects.all().select_related('comuna', 'region')

    return {
        'total': condominios.count(),
        'condominios': [
            {
                'id': c.id,
                'nombre': c.nombre,
                'rut': c.rut,
                'comuna': c.comuna.nombre if c.comuna else None,
                'region': c.region.nombre if c.region else None
            }
            for c in condominios
        ]
    }


def listar_todas_categorias():
    """
    Lista todas las categorías de incidencias disponibles.

    Returns:
        dict con todas las categorías
    """
    categorias = CategoriaIncidencia.objects.all().order_by('nombre_categoria_incidencia')

    return {
        'total': categorias.count(),
        'categorias': [
            {
                'id': c.id,
                'nombre': c.nombre_categoria_incidencia
            }
            for c in categorias
        ]
    }


def listar_condominios_por_region(region_nombre=None):
    """
    Lista condominios filtrados por región (opcional).
    Si no se especifica región, lista todos los condominios agrupados por región.

    Args:
        region_nombre: Nombre de la región (opcional, búsqueda flexible)

    Returns:
        dict con condominios filtrados por región
    """
    if region_nombre:
        # Búsqueda flexible por región
        condominios = Condominio.objects.filter(
            region__nombre__icontains=region_nombre
        ).select_related('comuna', 'region')

        if not condominios.exists():
            # Listar regiones disponibles
            from .models import Region
            regiones = Region.objects.all().order_by('nombre')
            lista_regiones = ', '.join([r.nombre for r in regiones])
            return {
                'total': 0,
                'region_buscada': region_nombre,
                'condominios': [],
                'error': f'No se encontraron condominios en la región "{region_nombre}". Regiones disponibles: {lista_regiones}'
            }

        region = condominios.first().region
        return {
            'total': condominios.count(),
            'region': region.nombre,
            'condominios': [
                {
                    'id': c.id,
                    'nombre': c.nombre,
                    'rut': c.rut,
                    'direccion': c.direccion,
                    'comuna': c.comuna.nombre if c.comuna else None
                }
                for c in condominios
            ]
        }
    else:
        # Listar todos los condominios agrupados por región
        from .models import Region
        regiones = Region.objects.all().order_by('nombre')
        resultado = {
            'total_regiones': regiones.count(),
            'regiones': []
        }

        for region in regiones:
            condominios = Condominio.objects.filter(
                region=region
            ).select_related('comuna')

            resultado['regiones'].append({
                'nombre': region.nombre,
                'total_condominios': condominios.count(),
                'condominios': [
                    {
                        'id': c.id,
                        'nombre': c.nombre,
                        'rut': c.rut,
                        'comuna': c.comuna.nombre if c.comuna else None
                    }
                    for c in condominios[:5]  # Limitar a 5 por región para no sobrecargar
                ]
            })

        return resultado


def listar_incidencias_detalladas(condominio_nombre=None, estado=None, prioridad=None, limite=10):
    """
    Lista incidencias con detalles completos (título, descripción, fecha, etc.).

    Args:
        condominio_nombre: Nombre del condominio para filtrar (opcional)
        estado: Estado de las incidencias (PENDIENTE, EN_PROCESO, RESUELTA, CERRADA, CANCELADA)
        prioridad: Prioridad de las incidencias (BAJA, MEDIA, ALTA, URGENTE)
        limite: Número máximo de incidencias a retornar (default: 10)

    Returns:
        dict con lista de incidencias detalladas
    """
    incidencias = Incidencia.objects.all().select_related(
        'condominio', 'tipo_incidencia', 'usuario_reporta'
    ).order_by('-fecha_reporte')

    # Filtrar por condominio si se especifica
    if condominio_nombre:
        incidencias = incidencias.filter(condominio__nombre__icontains=condominio_nombre)

    # Filtrar por estado si se especifica
    if estado:
        incidencias = incidencias.filter(estado=estado.upper())

    # Filtrar por prioridad si se especifica
    if prioridad:
        incidencias = incidencias.filter(prioridad=prioridad.upper())

    # Limitar resultados
    incidencias = incidencias[:limite]

    if not incidencias.exists():
        filtros_aplicados = []
        if condominio_nombre:
            filtros_aplicados.append(f'condominio "{condominio_nombre}"')
        if estado:
            filtros_aplicados.append(f'estado "{estado}"')
        if prioridad:
            filtros_aplicados.append(f'prioridad "{prioridad}"')

        mensaje = 'No se encontraron incidencias'
        if filtros_aplicados:
            mensaje += f' con los filtros: {", ".join(filtros_aplicados)}'

        return {
            'total': 0,
            'incidencias': [],
            'mensaje': mensaje
        }

    return {
        'total': incidencias.count(),
        'incidencias': [
            {
                'id': inc.id,
                'titulo': inc.titulo,
                'descripcion': inc.descripcion,
                'condominio': inc.condominio.nombre,
                'categoria': inc.tipo_incidencia.nombre_categoria_incidencia,
                'estado': inc.get_estado_display(),
                'prioridad': inc.get_prioridad_display(),
                'usuario_reporta': f'{inc.usuario_reporta.nombres} {inc.usuario_reporta.apellido}',
                'fecha_reporte': inc.fecha_reporte.strftime('%d/%m/%Y'),
                'fecha_cierre': inc.fecha_cierre.strftime('%d/%m/%Y') if inc.fecha_cierre else None,
                'direccion': inc.direccion_condominio_incidencia
            }
            for inc in incidencias
        ]
    }


def obtener_estadisticas_incidencias_por_condominio(condominio_id=None, condominio_nombre=None):
    """
    Obtiene estadísticas de incidencias de uno o todos los condominios.

    Args:
        condominio_id: ID del condominio (opcional)
        condominio_nombre: Nombre del condominio (opcional, búsqueda flexible)

    Returns:
        dict con estadísticas de incidencias por condominio
    """
    if condominio_id:
        # Buscar por ID
        try:
            condominio = Condominio.objects.get(id=condominio_id)
        except Condominio.DoesNotExist:
            return {
                'error': f'No se encontró el condominio con ID {condominio_id}'
            }

        incidencias = Incidencia.objects.filter(condominio=condominio)

        # Estadísticas por estado
        estadisticas_estado = {}
        for estado, nombre in Incidencia.Estado.choices:
            count = incidencias.filter(estado=estado).count()
            if count > 0:
                estadisticas_estado[nombre] = count

        # Estadísticas por prioridad
        estadisticas_prioridad = {}
        for prioridad, nombre in Incidencia.Prioridad.choices:
            count = incidencias.filter(prioridad=prioridad).count()
            if count > 0:
                estadisticas_prioridad[nombre] = count

        # Estadísticas por categoría (top 5)
        categorias_count = incidencias.values('tipo_incidencia__nombre_categoria_incidencia').annotate(
            total=Count('id')
        ).order_by('-total')[:5]

        return {
            'condominio_id': condominio.id,
            'condominio_nombre': condominio.nombre,
            'total_incidencias': incidencias.count(),
            'incidencias_abiertas': incidencias.filter(estado__in=['PENDIENTE', 'EN_PROCESO']).count(),
            'incidencias_cerradas': incidencias.filter(estado__in=['RESUELTA', 'CERRADA']).count(),
            'por_estado': estadisticas_estado,
            'por_prioridad': estadisticas_prioridad,
            'top_categorias': [
                {
                    'categoria': cat['tipo_incidencia__nombre_categoria_incidencia'],
                    'total': cat['total']
                }
                for cat in categorias_count
            ]
        }

    elif condominio_nombre:
        # Buscar por nombre
        condominios = Condominio.objects.filter(nombre__icontains=condominio_nombre)

        if not condominios.exists():
            # Listar condominios disponibles
            todos_condominios = Condominio.objects.all()[:10]
            lista_condominios = ', '.join([c.nombre for c in todos_condominios])
            return {
                'error': f'No se encontró ningún condominio con nombre similar a "{condominio_nombre}". Condominios disponibles: {lista_condominios}'
            }

        if condominios.count() > 1:
            # Si hay múltiples coincidencias, mostrar opciones
            lista_opciones = ', '.join([f'{c.nombre} (ID: {c.id})' for c in condominios])
            return {
                'error': f'Se encontraron {condominios.count()} condominios con nombre similar. Por favor, sé más específico. Opciones: {lista_opciones}'
            }

        # Llamar recursivamente con el ID encontrado
        return obtener_estadisticas_incidencias_por_condominio(condominio_id=condominios.first().id)

    else:
        # Estadísticas de todos los condominios
        condominios = Condominio.objects.all().select_related('region', 'comuna')
        resultado = {
            'total_condominios': condominios.count(),
            'condominios': []
        }

        for condominio in condominios:
            incidencias = Incidencia.objects.filter(condominio=condominio)
            total = incidencias.count()

            if total > 0:  # Solo incluir condominios con incidencias
                resultado['condominios'].append({
                    'id': condominio.id,
                    'nombre': condominio.nombre,
                    'region': condominio.region.nombre if condominio.region else None,
                    'total_incidencias': total,
                    'abiertas': incidencias.filter(estado__in=['PENDIENTE', 'EN_PROCESO']).count(),
                    'cerradas': incidencias.filter(estado__in=['RESUELTA', 'CERRADA']).count()
                })

        # Ordenar por total de incidencias (descendente)
        resultado['condominios'].sort(key=lambda x: x['total_incidencias'], reverse=True)

        return resultado


# ==================== HERRAMIENTAS DE ESCRITURA (CON CONFIRMACIÓN) ====================

def proponer_crear_condominio(nombre, rut, direccion, comuna, region, mail_contacto):
    """
    PROPONE crear un nuevo condominio (requiere confirmación del usuario).

    Args:
        nombre: Nombre del condominio
        rut: RUT del condominio
        direccion: Dirección completa
        comuna: Comuna
        region: Región
        mail_contacto: Email de contacto

    Returns:
        dict con la propuesta para confirmación del usuario
    """
    return {
        'requiere_confirmacion': True,
        'accion': 'crear_condominio',
        'tipo_registro': 'Condominio',
        'datos': {
            'nombre': nombre,
            'rut': rut,
            'direccion': direccion,
            'comuna': comuna,
            'region': region,
            'mail_contacto': mail_contacto
        },
        'mensaje_confirmacion': f'¿Deseas crear el condominio "{nombre}" con RUT {rut}?'
    }


def proponer_crear_usuario(nombres, apellido, rut, email, telefono, tipo_usuario, condominio_id):
    """
    PROPONE crear un nuevo usuario (requiere confirmación del usuario).

    Args:
        nombres: Nombres del usuario
        apellido: Apellido del usuario
        rut: RUT del usuario
        email: Email del usuario
        telefono: Teléfono del usuario
        tipo_usuario: Tipo de usuario (PROPIETARIO, ARRENDATARIO, ADMINISTRADOR)
        condominio_id: ID del condominio al que pertenece

    Returns:
        dict con la propuesta para confirmación del usuario
    """
    # Validar que existe el condominio
    try:
        condominio = Condominio.objects.get(id=condominio_id)
    except Condominio.DoesNotExist:
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': f'No se encontró condominio con ID {condominio_id}'
        }

    return {
        'requiere_confirmacion': True,
        'accion': 'crear_usuario',
        'tipo_registro': 'Usuario',
        'datos': {
            'nombres': nombres,
            'apellido': apellido,
            'rut': rut,
            'email': email,
            'telefono': telefono,
            'tipo_usuario': tipo_usuario,
            'condominio_id': condominio_id,
            'condominio_nombre': condominio.nombre
        },
        'mensaje_confirmacion': f'¿Deseas crear el usuario "{nombres} {apellido}" ({tipo_usuario}) para el condominio "{condominio.nombre}"?'
    }


def proponer_crear_reunion(condominio_id, tema, fecha_reunion, hora_reunion, ubicacion, descripcion=None):
    """
    PROPONE crear una nueva reunión (requiere confirmación del usuario).

    Args:
        condominio_id: ID del condominio
        tema: Tema de la reunión
        fecha_reunion: Fecha de la reunión (YYYY-MM-DD)
        hora_reunion: Hora de la reunión (HH:MM)
        ubicacion: Ubicación de la reunión
        descripcion: Descripción opcional

    Returns:
        dict con la propuesta para confirmación del usuario
    """
    # Validar condominio
    try:
        condominio = Condominio.objects.get(id=condominio_id)
    except Condominio.DoesNotExist:
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': f'No se encontró condominio con ID {condominio_id}'
        }

    return {
        'requiere_confirmacion': True,
        'accion': 'crear_reunion',
        'tipo_registro': 'Reunión',
        'datos': {
            'condominio_id': condominio_id,
            'condominio_nombre': condominio.nombre,
            'tema': tema,
            'fecha_reunion': fecha_reunion,
            'hora_reunion': hora_reunion,
            'ubicacion': ubicacion,
            'descripcion': descripcion
        },
        'mensaje_confirmacion': f'¿Deseas crear una reunión sobre "{tema}" el {fecha_reunion} a las {hora_reunion} en {ubicacion}?'
    }


def proponer_crear_incidencia(condominio_nombre, categoria_nombre, titulo, descripcion,
                               prioridad='MEDIA', direccion=None, latitud=None, longitud=None, _usuario_actual=None):
    """
    PROPONE crear una nueva incidencia (requiere confirmación del usuario).
    Busca el condominio y la categoría por nombre. El usuario reportante se obtiene automáticamente de la sesión.

    Args:
        condominio_nombre: Nombre del condominio (búsqueda flexible, case-insensitive)
        categoria_nombre: Nombre de la categoría de incidencia (búsqueda flexible, case-insensitive)
        titulo: Título de la incidencia
        descripcion: Descripción detallada
        prioridad: Prioridad (BAJA, MEDIA, ALTA, URGENTE). Default: MEDIA
        direccion: Dirección opcional
        latitud: Latitud opcional
        longitud: Longitud opcional
        _usuario_actual: Usuario de la sesión (pasado automáticamente por el sistema)

    Returns:
        dict con la propuesta para confirmación del usuario
    """
    # Validar que tenemos el usuario actual
    if not _usuario_actual:
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': 'No se pudo identificar al usuario actual. Por favor, inicia sesión nuevamente.'
        }

    # Buscar condominio por nombre (case-insensitive, búsqueda flexible)
    condominios = Condominio.objects.filter(nombre__icontains=condominio_nombre)

    if not condominios.exists():
        # Listar condominios disponibles
        todos_condominios = Condominio.objects.all()[:10]
        lista_condominios = ', '.join([c.nombre for c in todos_condominios])
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': f'No se encontró ningún condominio con nombre similar a "{condominio_nombre}". Condominios disponibles: {lista_condominios}'
        }

    if condominios.count() > 1:
        # Si hay múltiples coincidencias, mostrar opciones
        lista_opciones = ', '.join([c.nombre for c in condominios])
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': f'Se encontraron {condominios.count()} condominios con nombre similar a "{condominio_nombre}". Por favor, sé más específico. Opciones: {lista_opciones}'
        }

    condominio = condominios.first()

    # Buscar categoría por nombre (case-insensitive, búsqueda flexible)
    categorias = CategoriaIncidencia.objects.filter(nombre_categoria_incidencia__icontains=categoria_nombre)

    if not categorias.exists():
        # Listar categorías disponibles
        todas_categorias = CategoriaIncidencia.objects.all()
        lista_categorias = ', '.join([c.nombre_categoria_incidencia for c in todas_categorias])
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': f'No se encontró ninguna categoría con nombre similar a "{categoria_nombre}". Categorías disponibles: {lista_categorias}'
        }

    if categorias.count() > 1:
        # Si hay múltiples coincidencias, mostrar opciones
        lista_opciones = ', '.join([c.nombre_categoria_incidencia for c in categorias])
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': f'Se encontraron {categorias.count()} categorías con nombre similar. Por favor, sé más específico. Opciones: {lista_opciones}'
        }

    categoria = categorias.first()

    return {
        'requiere_confirmacion': True,
        'accion': 'crear_incidencia',
        'tipo_registro': 'Incidencia',
        'datos': {
            'condominio_id': condominio.id,
            'condominio_nombre': condominio.nombre,
            'usuario_reporta_id': _usuario_actual.id,
            'usuario_reporta_nombre': f'{_usuario_actual.nombres} {_usuario_actual.apellido}',
            'tipo_incidencia_id': categoria.id,
            'categoria_nombre': categoria.nombre_categoria_incidencia,
            'titulo': titulo,
            'descripcion': descripcion,
            'prioridad': prioridad,
            'direccion_condominio_incidencia': direccion,
            'latitud': latitud,
            'longitud': longitud
        },
        'mensaje_confirmacion': f'¿Deseas crear la incidencia "{titulo}" con prioridad {prioridad} en el condominio "{condominio.nombre}"? (Reportado por: {_usuario_actual.nombres} {_usuario_actual.apellido})'
    }


def proponer_crear_categoria(nombre_categoria):
    """
    PROPONE crear una nueva categoría de incidencia (requiere confirmación del usuario).

    Args:
        nombre_categoria: Nombre de la categoría

    Returns:
        dict con la propuesta para confirmación del usuario
    """
    # Verificar si ya existe
    if CategoriaIncidencia.objects.filter(nombre_categoria_incidencia__iexact=nombre_categoria).exists():
        return {
            'requiere_confirmacion': False,
            'exito': False,
            'error': f'Ya existe una categoría con el nombre "{nombre_categoria}"'
        }

    return {
        'requiere_confirmacion': True,
        'accion': 'crear_categoria',
        'tipo_registro': 'Categoría de Incidencia',
        'datos': {
            'nombre_categoria_incidencia': nombre_categoria
        },
        'mensaje_confirmacion': f'¿Deseas crear la categoría "{nombre_categoria}"?'
    }


def proponer_crear_amonestacion(condominio_id, usuario_reporta_id, nombre_amonestado, apellidos_amonestado,
                                 rut_amonestado, tipo_amonestacion, motivo, fecha_amonestacion,
                                 numero_departamento=None, motivo_detalle=None, fecha_limite_pago=None):
    """
    PROPONE crear una nueva amonestación (requiere confirmación del usuario).

    Args:
        condominio_id: ID del condominio
        usuario_reporta_id: ID del usuario que reporta
        nombre_amonestado: Nombre del amonestado
        apellidos_amonestado: Apellidos del amonestado
        rut_amonestado: RUT del amonestado
        tipo_amonestacion: Tipo (VERBAL, ESCRITA, MULTA, SUSPENSION)
        motivo: Motivo de la amonestación
        fecha_amonestacion: Fecha de la amonestación (YYYY-MM-DD)
        numero_departamento: Número de departamento opcional
        motivo_detalle: Detalle del motivo opcional
        fecha_limite_pago: Fecha límite de pago (solo para MULTA)

    Returns:
        dict con la propuesta para confirmación del usuario
    """
    # Validar relaciones
    try:
        condominio = Condominio.objects.get(id=condominio_id)
        usuario = Usuario.objects.get(id=usuario_reporta_id)
    except Condominio.DoesNotExist:
        return {'requiere_confirmacion': False, 'exito': False, 'error': f'No se encontró condominio con ID {condominio_id}'}
    except Usuario.DoesNotExist:
        return {'requiere_confirmacion': False, 'exito': False, 'error': f'No se encontró usuario con ID {usuario_reporta_id}'}

    return {
        'requiere_confirmacion': True,
        'accion': 'crear_amonestacion',
        'tipo_registro': 'Amonestación',
        'datos': {
            'condominio_id': condominio_id,
            'condominio_nombre': condominio.nombre,
            'usuario_reporta_id': usuario_reporta_id,
            'usuario_reporta_nombre': f'{usuario.nombres} {usuario.apellido}',
            'nombre_amonestado': nombre_amonestado,
            'apellidos_amonestado': apellidos_amonestado,
            'rut_amonestado': rut_amonestado,
            'tipo_amonestacion': tipo_amonestacion,
            'motivo': motivo,
            'motivo_detalle': motivo_detalle,
            'fecha_amonestacion': fecha_amonestacion,
            'numero_departamento': numero_departamento,
            'fecha_limite_pago': fecha_limite_pago
        },
        'mensaje_confirmacion': f'¿Deseas crear una amonestación de tipo {tipo_amonestacion} para {nombre_amonestado} {apellidos_amonestado}?'
    }


def crear_bitacora_incidencia(incidencia_id, accion, detalle):
    """
    Crea un registro de bitácora para una incidencia.

    Args:
        incidencia_id: ID de la incidencia
        accion: Acción realizada
        detalle: Detalle de la acción

    Returns:
        dict con información del registro creado
    """
    try:
        incidencia = Incidencia.objects.get(id=incidencia_id)

        bitacora = Bitacora.objects.create(
            incidencia=incidencia,
            accion=accion,
            detalle=detalle
        )

        return {
            'exito': True,
            'bitacora_id': bitacora.id,
            'incidencia': incidencia.titulo,
            'mensaje': 'Registro de bitácora creado exitosamente'
        }
    except Incidencia.DoesNotExist:
        return {
            'exito': False,
            'error': f'No se encontró incidencia con ID {incidencia_id}'
        }
    except Exception as e:
        return {
            'exito': False,
            'error': str(e)
        }


def recomendar_solucion_incidencia(incidencia_id):
    """
    Genera recomendaciones para resolver una incidencia basándose en el historial.

    Args:
        incidencia_id: ID de la incidencia

    Returns:
        dict con recomendaciones
    """
    try:
        incidencia = Incidencia.objects.get(id=incidencia_id)

        # Buscar incidencias similares resueltas
        incidencias_similares = Incidencia.objects.filter(
            tipo_incidencia=incidencia.tipo_incidencia,
            estado='CERRADA'
        ).select_related('tipo_incidencia')[:5]

        recomendaciones = []

        for inc_similar in incidencias_similares:
            # Obtener acciones de bitácora de incidencias similares
            bitacoras = Bitacora.objects.filter(incidencia=inc_similar).order_by('fecha_bitacora')

            acciones = [
                {'accion': bit.accion, 'detalle': bit.detalle}
                for bit in bitacoras
            ]

            if acciones:
                recomendaciones.append({
                    'incidencia_similar_id': inc_similar.id,
                    'titulo': inc_similar.titulo,
                    'acciones_tomadas': acciones
                })

        return {
            'incidencia_actual': {
                'id': incidencia.id,
                'titulo': incidencia.titulo,
                'categoria': incidencia.tipo_incidencia.nombre_categoria_incidencia if incidencia.tipo_incidencia else None,
                'prioridad': incidencia.get_prioridad_display()
            },
            'recomendaciones_basadas_en': len(recomendaciones),
            'casos_similares_resueltos': recomendaciones
        }
    except Incidencia.DoesNotExist:
        return {
            'exito': False,
            'error': f'No se encontró incidencia con ID {incidencia_id}'
        }


# ==================== FUNCIONES DE EJECUCIÓN (POST-CONFIRMACIÓN) ====================
# Estas funciones se ejecutan DESPUÉS de que el usuario confirme la acción

def ejecutar_crear_condominio(datos):
    """Ejecuta la creación de un condominio después de la confirmación."""
    try:
        condominio = Condominio.objects.create(
            nombre=datos['nombre'],
            rut=datos['rut'],
            direccion=datos['direccion'],
            comuna=datos['comuna'],
            region=datos['region'],
            mail_contacto=datos['mail_contacto']
        )
        return {
            'exito': True,
            'registro_id': condominio.id,
            'mensaje': f'Condominio "{condominio.nombre}" creado exitosamente'
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def ejecutar_crear_usuario(datos):
    """Ejecuta la creación de un usuario después de la confirmación."""
    try:
        usuario = Usuario.objects.create(
            nombres=datos['nombres'],
            apellido=datos['apellido'],
            rut=datos['rut'],
            email=datos['email'],
            telefono=datos['telefono'],
            tipo_usuario=datos['tipo_usuario'],
            condominio_id=datos['condominio_id']
        )
        return {
            'exito': True,
            'registro_id': usuario.id,
            'mensaje': f'Usuario "{usuario.nombres} {usuario.apellido}" creado exitosamente'
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def ejecutar_crear_reunion(datos):
    """Ejecuta la creación de una reunión después de la confirmación."""
    try:
        from datetime import datetime

        # Combinar fecha y hora
        fecha_hora = datetime.strptime(
            f"{datos['fecha_reunion']} {datos['hora_reunion']}",
            '%Y-%m-%d %H:%M'
        )

        reunion = Reunion.objects.create(
            condominio_id=datos['condominio_id'],
            tema=datos['tema'],
            fecha_reunion=fecha_hora,
            ubicacion=datos['ubicacion'],
            descripcion=datos.get('descripcion'),
            estado='PROGRAMADA'
        )
        return {
            'exito': True,
            'registro_id': reunion.id,
            'mensaje': f'Reunión sobre "{reunion.tema}" creada exitosamente'
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def ejecutar_crear_incidencia(datos):
    """Ejecuta la creación de una incidencia después de la confirmación."""
    try:
        from datetime import datetime

        incidencia = Incidencia.objects.create(
            condominio_id=datos['condominio_id'],
            usuario_reporta_id=datos['usuario_reporta_id'],
            tipo_incidencia_id=datos['tipo_incidencia_id'],
            titulo=datos['titulo'],
            descripcion=datos['descripcion'],
            prioridad=datos['prioridad'],
            direccion_condominio_incidencia=datos.get('direccion_condominio_incidencia'),
            ubicacion_latitud_reporte=datos.get('latitud'),
            ubicacion_longitud_reporte=datos.get('longitud'),
            estado='PENDIENTE',
            fecha_reporte=datetime.now()
        )
        return {
            'exito': True,
            'registro_id': incidencia.id,
            'mensaje': f'Incidencia "{incidencia.titulo}" creada exitosamente'
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def ejecutar_crear_categoria(datos):
    """Ejecuta la creación de una categoría después de la confirmación."""
    try:
        categoria = CategoriaIncidencia.objects.create(
            nombre_categoria_incidencia=datos['nombre_categoria_incidencia']
        )
        return {
            'exito': True,
            'registro_id': categoria.id,
            'mensaje': f'Categoría "{categoria.nombre_categoria_incidencia}" creada exitosamente'
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}


def ejecutar_crear_amonestacion(datos):
    """Ejecuta la creación de una amonestación después de la confirmación."""
    try:
        from datetime import datetime

        # Convertir fecha string a objeto date
        fecha_amon = datetime.strptime(datos['fecha_amonestacion'], '%Y-%m-%d').date()
        fecha_limite = None
        if datos.get('fecha_limite_pago'):
            fecha_limite = datetime.strptime(datos['fecha_limite_pago'], '%Y-%m-%d').date()

        amonestacion = Amonestacion.objects.create(
            condominio_id=datos['condominio_id'],
            usuario_reporta_id=datos['usuario_reporta_id'],
            nombre_amonestado=datos['nombre_amonestado'],
            apellidos_amonestado=datos['apellidos_amonestado'],
            rut_amonestado=datos['rut_amonestado'],
            tipo_amonestacion=datos['tipo_amonestacion'],
            motivo=datos['motivo'],
            motivo_detalle=datos.get('motivo_detalle'),
            fecha_amonestacion=fecha_amon,
            numero_departamento=datos.get('numero_departamento'),
            fecha_limite_pago=fecha_limite
        )
        return {
            'exito': True,
            'registro_id': amonestacion.id,
            'mensaje': f'Amonestación para {amonestacion.nombre_amonestado} {amonestacion.apellidos_amonestado} creada exitosamente'
        }
    except Exception as e:
        return {'exito': False, 'error': str(e)}


# Mapeo de acciones a funciones de ejecución
EXECUTION_FUNCTIONS = {
    'crear_condominio': ejecutar_crear_condominio,
    'crear_usuario': ejecutar_crear_usuario,
    'crear_reunion': ejecutar_crear_reunion,
    'crear_incidencia': ejecutar_crear_incidencia,
    'crear_categoria': ejecutar_crear_categoria,
    'crear_amonestacion': ejecutar_crear_amonestacion,
}


# ==================== MAPEO DE HERRAMIENTAS PARA OPENAI ====================

AVAILABLE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_incidencias_abiertas",
            "description": "Obtiene todas las incidencias que están abiertas o en proceso. Útil para saber qué problemas están pendientes de resolver.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condominio_id": {
                        "type": "integer",
                        "description": "ID opcional del condominio para filtrar las incidencias"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_estadisticas_dashboard",
            "description": "Obtiene las estadísticas principales del sistema: total de condominios, usuarios, incidencias, reuniones, distribución por estado y prioridad, categorías más comunes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condominio_id": {
                        "type": "integer",
                        "description": "ID opcional del condominio para filtrar las estadísticas"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_amonestaciones_recientes",
            "description": "Obtiene las amonestaciones registradas en los últimos N días.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dias": {
                        "type": "integer",
                        "description": "Número de días hacia atrás a consultar (default: 30)"
                    },
                    "condominio_id": {
                        "type": "integer",
                        "description": "ID opcional del condominio para filtrar"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_incidencias",
            "description": "Busca incidencias por título o descripción.",
            "parameters": {
                "type": "object",
                "properties": {
                    "termino_busqueda": {
                        "type": "string",
                        "description": "Término a buscar en título o descripción"
                    },
                    "condominio_id": {
                        "type": "integer",
                        "description": "ID opcional del condominio para filtrar"
                    }
                },
                "required": ["termino_busqueda"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analizar_tendencias_incidencias",
            "description": "Analiza tendencias de incidencias en un período: categorías frecuentes, distribución de prioridades, tasa de resolución.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dias": {
                        "type": "integer",
                        "description": "Número de días a analizar (default: 90)"
                    },
                    "condominio_id": {
                        "type": "integer",
                        "description": "ID opcional del condominio para filtrar"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_todos_condominios",
            "description": "Lista todos los condominios del sistema con su información básica. Útil para ver qué condominios están disponibles.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_todas_categorias",
            "description": "Lista todas las categorías de incidencias disponibles. Útil para ver qué tipos de incidencias se pueden reportar.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_condominio_por_nombre",
            "description": "Busca condominios por nombre (búsqueda flexible, case-insensitive).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre o parte del nombre del condominio a buscar"
                    }
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "buscar_categoria_por_nombre",
            "description": "Busca categorías de incidencias por nombre (búsqueda flexible, case-insensitive).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre o parte del nombre de la categoría a buscar"
                    }
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_condominios_por_region",
            "description": "Lista condominios filtrados por región. Si no se especifica región, muestra todos los condominios agrupados por región. Útil para explorar condominios por ubicación geográfica.",
            "parameters": {
                "type": "object",
                "properties": {
                    "region_nombre": {
                        "type": "string",
                        "description": "Nombre de la región para filtrar (opcional, búsqueda flexible). Ejemplos: 'Metropolitana', 'Valparaíso', 'Biobío'. Si no se especifica, muestra todas las regiones."
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "obtener_estadisticas_incidencias_por_condominio",
            "description": "Obtiene estadísticas detalladas de incidencias para uno o todos los condominios. Muestra total de incidencias, distribución por estado (abiertas/cerradas), por prioridad, y categorías más frecuentes. Si no se especifican parámetros, muestra un resumen de todos los condominios ordenados por cantidad de incidencias.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condominio_id": {
                        "type": "integer",
                        "description": "ID del condominio para obtener estadísticas específicas (opcional)"
                    },
                    "condominio_nombre": {
                        "type": "string",
                        "description": "Nombre del condominio para buscar (opcional, búsqueda flexible). Ejemplos: 'Torres del Sol', 'Edificio Las Condes'"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "listar_incidencias_detalladas",
            "description": "Lista incidencias con DETALLES COMPLETOS (ID, título, descripción, categoría, estado, prioridad, fecha, usuario que reporta, dirección). Usa esta función cuando el usuario quiera ver incidencias específicas, no solo estadísticas. Permite filtrar por condominio, estado y/o prioridad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condominio_nombre": {
                        "type": "string",
                        "description": "Nombre del condominio para filtrar (opcional, búsqueda flexible). Ejemplos: 'El Arrayán', 'Torres del Sol'"
                    },
                    "estado": {
                        "type": "string",
                        "description": "Estado para filtrar (opcional). Valores: PENDIENTE, EN_PROCESO, RESUELTA, CERRADA, CANCELADA",
                        "enum": ["PENDIENTE", "EN_PROCESO", "RESUELTA", "CERRADA", "CANCELADA"]
                    },
                    "prioridad": {
                        "type": "string",
                        "description": "Prioridad para filtrar (opcional). Valores: BAJA, MEDIA, ALTA, URGENTE",
                        "enum": ["BAJA", "MEDIA", "ALTA", "URGENTE"]
                    },
                    "limite": {
                        "type": "integer",
                        "description": "Número máximo de incidencias a retornar (default: 10, máximo: 50)"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "crear_bitacora_incidencia",
            "description": "Crea un registro de bitácora (seguimiento) para una incidencia específica.",
            "parameters": {
                "type": "object",
                "properties": {
                    "incidencia_id": {
                        "type": "integer",
                        "description": "ID de la incidencia"
                    },
                    "accion": {
                        "type": "string",
                        "description": "Acción realizada (ej: 'Revisión inicial', 'Contacto con proveedor')"
                    },
                    "detalle": {
                        "type": "string",
                        "description": "Detalle completo de la acción tomada"
                    }
                },
                "required": ["incidencia_id", "accion", "detalle"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "recomendar_solucion_incidencia",
            "description": "Genera recomendaciones para resolver una incidencia basándose en casos similares previamente resueltos.",
            "parameters": {
                "type": "object",
                "properties": {
                    "incidencia_id": {
                        "type": "integer",
                        "description": "ID de la incidencia para la cual generar recomendaciones"
                    }
                },
                "required": ["incidencia_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proponer_crear_condominio",
            "description": "PROPONE crear un nuevo condominio (requiere confirmación del usuario antes de ejecutarse).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {"type": "string", "description": "Nombre del condominio"},
                    "rut": {"type": "string", "description": "RUT del condominio"},
                    "direccion": {"type": "string", "description": "Dirección completa"},
                    "comuna": {"type": "string", "description": "Comuna"},
                    "region": {"type": "string", "description": "Región"},
                    "mail_contacto": {"type": "string", "description": "Email de contacto"}
                },
                "required": ["nombre", "rut", "direccion", "comuna", "region", "mail_contacto"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proponer_crear_usuario",
            "description": "PROPONE crear un nuevo usuario (requiere confirmación del usuario antes de ejecutarse).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombres": {"type": "string", "description": "Nombres del usuario"},
                    "apellido": {"type": "string", "description": "Apellido del usuario"},
                    "rut": {"type": "string", "description": "RUT del usuario"},
                    "email": {"type": "string", "description": "Email del usuario"},
                    "telefono": {"type": "string", "description": "Teléfono del usuario"},
                    "tipo_usuario": {"type": "string", "description": "Tipo: PROPIETARIO, ARRENDATARIO, ADMINISTRADOR"},
                    "condominio_id": {"type": "integer", "description": "ID del condominio"}
                },
                "required": ["nombres", "apellido", "rut", "email", "telefono", "tipo_usuario", "condominio_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proponer_crear_reunion",
            "description": "PROPONE crear una nueva reunión (requiere confirmación del usuario antes de ejecutarse).",
            "parameters": {
                "type": "object",
                "properties": {
                    "condominio_id": {"type": "integer", "description": "ID del condominio"},
                    "tema": {"type": "string", "description": "Tema de la reunión"},
                    "fecha_reunion": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                    "hora_reunion": {"type": "string", "description": "Hora en formato HH:MM"},
                    "ubicacion": {"type": "string", "description": "Ubicación de la reunión"},
                    "descripcion": {"type": "string", "description": "Descripción opcional"}
                },
                "required": ["condominio_id", "tema", "fecha_reunion", "hora_reunion", "ubicacion"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proponer_crear_incidencia",
            "description": "PROPONE crear una nueva incidencia (requiere confirmación del usuario). El usuario reportante se obtiene automáticamente de la sesión. Usa esta función cuando el usuario quiera reportar un problema, incidencia o solicitud en un condominio.",
            "parameters": {
                "type": "object",
                "properties": {
                    "condominio_nombre": {
                        "type": "string",
                        "description": "Nombre del condominio donde ocurre la incidencia (búsqueda flexible). Ejemplos: 'Torres del Sol', 'Edificio Las Condes'"
                    },
                    "categoria_nombre": {
                        "type": "string",
                        "description": "Nombre de la categoría de la incidencia (búsqueda flexible). Ejemplos: 'Mantenimiento', 'Seguridad', 'Limpieza', 'Agua', 'Electricidad'"
                    },
                    "titulo": {
                        "type": "string",
                        "description": "Título breve y descriptivo de la incidencia. Ejemplo: 'Fuga de agua en baño común'"
                    },
                    "descripcion": {
                        "type": "string",
                        "description": "Descripción detallada del problema, incluyendo ubicación específica si es relevante"
                    },
                    "prioridad": {
                        "type": "string",
                        "description": "Nivel de urgencia: BAJA, MEDIA, ALTA, URGENTE (default: MEDIA). Usa URGENTE para emergencias.",
                        "enum": ["BAJA", "MEDIA", "ALTA", "URGENTE"]
                    },
                    "direccion": {
                        "type": "string",
                        "description": "Ubicación específica dentro del condominio (opcional). Ejemplo: 'Piso 3, departamento 301'"
                    },
                    "latitud": {
                        "type": "number",
                        "description": "Coordenada de latitud GPS (opcional)"
                    },
                    "longitud": {
                        "type": "number",
                        "description": "Coordenada de longitud GPS (opcional)"
                    }
                },
                "required": ["condominio_nombre", "categoria_nombre", "titulo", "descripcion"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proponer_crear_categoria",
            "description": "PROPONE crear una nueva categoría de incidencia (requiere confirmación del usuario antes de ejecutarse).",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre_categoria": {"type": "string", "description": "Nombre de la categoría"}
                },
                "required": ["nombre_categoria"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "proponer_crear_amonestacion",
            "description": "PROPONE crear una nueva amonestación (requiere confirmación del usuario antes de ejecutarse).",
            "parameters": {
                "type": "object",
                "properties": {
                    "condominio_id": {"type": "integer", "description": "ID del condominio"},
                    "usuario_reporta_id": {"type": "integer", "description": "ID del usuario que reporta"},
                    "nombre_amonestado": {"type": "string", "description": "Nombre del amonestado"},
                    "apellidos_amonestado": {"type": "string", "description": "Apellidos del amonestado"},
                    "rut_amonestado": {"type": "string", "description": "RUT del amonestado"},
                    "tipo_amonestacion": {"type": "string", "description": "VERBAL, ESCRITA, MULTA, SUSPENSION"},
                    "motivo": {"type": "string", "description": "Motivo de la amonestación"},
                    "fecha_amonestacion": {"type": "string", "description": "Fecha en formato YYYY-MM-DD"},
                    "numero_departamento": {"type": "string", "description": "Número de departamento opcional"},
                    "motivo_detalle": {"type": "string", "description": "Detalle del motivo opcional"},
                    "fecha_limite_pago": {"type": "string", "description": "Fecha límite de pago (solo MULTA) en formato YYYY-MM-DD"}
                },
                "required": ["condominio_id", "usuario_reporta_id", "nombre_amonestado", "apellidos_amonestado",
                            "rut_amonestado", "tipo_amonestacion", "motivo", "fecha_amonestacion"]
            }
        }
    }
]


# Mapeo de nombres de función a funciones reales
TOOL_FUNCTIONS = {
    # Herramientas de consulta
    "get_incidencias_abiertas": get_incidencias_abiertas,
    "get_estadisticas_dashboard": get_estadisticas_dashboard,
    "get_amonestaciones_recientes": get_amonestaciones_recientes,
    "buscar_incidencias": buscar_incidencias,
    "analizar_tendencias_incidencias": analizar_tendencias_incidencias,
    "crear_bitacora_incidencia": crear_bitacora_incidencia,
    "recomendar_solucion_incidencia": recomendar_solucion_incidencia,

    # Herramientas de búsqueda
    "buscar_condominio_por_nombre": buscar_condominio_por_nombre,
    "buscar_usuario_por_nombre": buscar_usuario_por_nombre,
    "buscar_categoria_por_nombre": buscar_categoria_por_nombre,
    "listar_todos_condominios": listar_todos_condominios,
    "listar_todas_categorias": listar_todas_categorias,
    "listar_condominios_por_region": listar_condominios_por_region,
    "obtener_estadisticas_incidencias_por_condominio": obtener_estadisticas_incidencias_por_condominio,
    "listar_incidencias_detalladas": listar_incidencias_detalladas,

    # Herramientas de escritura (con confirmación)
    "proponer_crear_condominio": proponer_crear_condominio,
    "proponer_crear_usuario": proponer_crear_usuario,
    "proponer_crear_reunion": proponer_crear_reunion,
    "proponer_crear_incidencia": proponer_crear_incidencia,
    "proponer_crear_categoria": proponer_crear_categoria,
    "proponer_crear_amonestacion": proponer_crear_amonestacion,
}
