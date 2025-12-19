# CLAUDE.md - Sistema de Gestión de Condominios

## Descripción del Proyecto

Sistema web completo para la administración y gestión de condominios, desarrollado con Django. Permite la gestión integral de propiedades, residentes, reuniones, incidencias, evidencias y amonestaciones.

**Fecha de inicio**: 2025
**Estado**: Todas las vistas CRUD implementadas y funcionales

---

## Stack Tecnológico

### Backend
- **Django**: 5.2.8
- **Base de datos**: PostgreSQL
- **Lenguaje**: Python 3.x

### Frontend
- **Framework CSS**: Bootstrap 5.3.2
- **Iconos**: Bootstrap Icons
- **Gráficos**: Chart.js 4.4.0
- **JavaScript**: Vanilla JS (OOP)

### APIs Externas
- **Geolocalización**: Browser Geolocation API (nativo)
- **Geocodificación inversa**: Nominatim/OpenStreetMap (gratuito, sin API key)

---

## Arquitectura del Proyecto

### Estructura de Directorios

```
micondominio/
├── mi_condominio/              # Aplicación principal
│   ├── models.py               # 8 modelos principales
│   ├── views.py                # ~1300 líneas con todas las vistas CRUD
│   ├── urls.py                 # Rutas para 8 módulos
│   ├── admin.py                # Configuración del panel admin
│   ├── static/
│   │   └── mi_condominio/
│   │       ├── css/
│   │       └── js/
│   │           └── geolocation.js    # Módulo de geolocalización
│   ├── templates/
│   │   └── mi_condominio/
│   │       ├── landing.html
│   │       ├── login.html
│   │       ├── dashboard/
│   │       │   ├── base_dashboard.html
│   │       │   └── dashboard.html
│   │       ├── condominios/
│   │       ├── usuarios/
│   │       ├── reuniones/
│   │       ├── incidencias/
│   │       ├── categorias/
│   │       ├── bitacoras/
│   │       ├── evidencias/
│   │       └── amonestaciones/
│   └── management/
│       └── commands/
│           └── cargar_categorias.py
└── micondominio/               # Configuración del proyecto
    ├── settings.py
    ├── urls.py
    └── wsgi.py
```

---

## Modelos Implementados

### 1. **Condominio**
- Información básica de condominios
- Dirección completa
- Datos de contacto
- Relación con todos los demás modelos

### 2. **Usuario**
- Datos personales (nombre, apellido, RUT, email, teléfono)
- Tipo de usuario (PROPIETARIO, ARRENDATARIO, ADMINISTRADOR)
- Relación con condominio
- Campos de auditoría (fecha_creacion, fecha_actualizacion)

### 3. **Reunion**
- Información de reuniones
- Estado (PROGRAMADA, REALIZADA, CANCELADA)
- Relación con condominio
- Fecha, hora, ubicación, temas

### 4. **CategoriaIncidencia**
- Categorías para clasificar incidencias
- 20 categorías precargadas vía management command
- Nombres únicos (case-insensitive)

### 5. **Incidencia**
- Gestión de incidencias/problemas
- Relación con condominio, categoría y usuario reportante
- Estados (ABIERTA, EN_PROCESO, CERRADA, CANCELADA)
- Prioridades (BAJA, MEDIA, ALTA, URGENTE)
- Geolocalización opcional (latitud, longitud, dirección)
- Fecha de reporte y cierre

### 6. **Bitacora**
- Registro de seguimiento para incidencias
- Relación con incidencia
- Descripción, acción tomada, fecha

### 7. **EvidenciaIncidencia**
- Archivos de evidencia para incidencias
- Tipos: IMAGEN, VIDEO, DOCUMENTO, AUDIO, OTRO
- URL del archivo
- Relación con incidencia

### 8. **Amonestacion**
- Sanciones/advertencias a usuarios
- Tipos: VERBAL, ESCRITA, MULTA, SUSPENSION
- 12 motivos predefinidos
- Relación con usuario y condominio
- Descripción detallada

---

## Módulos CRUD Implementados

Todos los módulos siguen el mismo patrón:
- `list`: Vista de listado con filtros y búsqueda
- `create`: Creación de nuevos registros
- `edit`: Edición de registros existentes
- `delete`: Eliminación con confirmación

### Estado de Implementación (8/8 completados)

| Módulo | Estado | Características Especiales |
|--------|--------|----------------------------|
| Condominios | ✅ | Filtros por región, búsqueda |
| Usuarios | ✅ | Filtros por tipo y condominio |
| Reuniones | ✅ | Filtros por estado y condominio |
| Incidencias | ✅ | **Geolocalización automática**, 5 filtros |
| Categorías | ✅ | **20 categorías precargadas**, orden descendente |
| Bitácora | ✅ | Filtro por incidencia |
| Evidencias | ✅ | Filtros por tipo de archivo, iconos visuales |
| Amonestaciones | ✅ | 5 filtros, badges por tipo |

---

## Convenciones y Decisiones Técnicas

### 1. **Separación de JavaScript**
- **NUNCA** escribir JavaScript inline en templates
- Crear archivos JS separados en `static/mi_condominio/js/`
- Usar clases y OOP para mejor organización
- Cargar via `{% block extra_js %}` y `{% static %}`

**Ejemplo**: `geolocation.js` - Clase `GeolocationManager`

### 2. **Inicialización de Datos**
- **NO** crear migraciones manuales para datos iniciales
- Usar Django management commands (`cargar_categorias.py`)
- Utilizar `get_or_create()` para idempotencia

### 3. **Optimización de Queries**
- Usar `select_related()` para relaciones ForeignKey
- Ejemplo: `Incidencia.objects.select_related('condominio', 'tipo_incidencia', 'usuario_reporta')`
- Evitar problemas N+1

### 4. **Ordenamiento**
- Listas ordenadas por defecto: descendente (`-id` o `-fecha`)
- Ejemplo: Categorías muestran las más recientes primero

### 5. **Patrones de Templates**
- Estructura consistente: `list.html`, `form.html`, `delete.html`
- Filtros en card separado arriba del contenido
- Sidebar con detección de estado activo
- Bootstrap icons consistentes por módulo

### 6. **Validación y Mensajes**
- Django messages framework para feedback
- Validación en backend (nunca confiar solo en frontend)
- Try-except para manejo de errores

### 7. **Seguridad**
- `@login_required` en todas las vistas del dashboard
- CSRF tokens en todos los formularios
- Validación de existencia de objetos relacionados

---

## Características Especiales

### Geolocalización en Incidencias

**Archivo**: `static/mi_condominio/js/geolocation.js`

**Funcionalidades**:
- Captura automática de GPS del dispositivo
- Precisión de ~11cm (6 decimales)
- Geocodificación inversa con Nominatim (gratuito)
- Manejo de errores comprehensivo
- Campos de solo lectura para lat/lon

**Configuración**:
```javascript
const options = {
    enableHighAccuracy: true,  // Máxima precisión
    timeout: 10000,            // 10 segundos
    maximumAge: 0              // Sin caché
};
```

### Management Commands

**Cargar Categorías Iniciales**:
```bash
python manage.py cargar_categorias
```

Carga 20 categorías predefinidas:
- Mantenimiento, Seguridad, Limpieza, Ruidos Molestos
- Estacionamientos, Áreas Comunes, Mascotas, Basura
- Iluminación, Agua, Electricidad, Ascensores
- Portones y Accesos, Jardines, Piscina, Quincho
- Gimnasio, Convivencia, Normativa, Otros

---

## Dashboard y Navegación

### Sidebar Structure

**Sección "Mi Condominio"**:
- Dashboard (home con gráficos Chart.js)
- Condominios
- Usuarios
- Reuniones

**Sección "Incidencias"**:
- Incidencias (con geolocalización)
- Bitácora
- Evidencias

**Sección "Administración"**:
- Categorías
- Amonestaciones
- Panel Admin (solo staff)

### Detección de Estado Activo

Patrón usado:
```django
{% if request.resolver_match.url_name == 'module_list' or
     request.resolver_match.url_name == 'module_create' or
     request.resolver_match.url_name == 'module_edit' or
     request.resolver_match.url_name == 'module_delete' %}active{% endif %}
```

---

## Patrón de Vistas CRUD

### Estructura Estándar

```python
@login_required
def module_list(request):
    # 1. Query base con select_related()
    objects = Model.objects.select_related(...).all()

    # 2. Aplicar filtros desde request.GET
    if filter_param := request.GET.get('filter'):
        objects = objects.filter(field=filter_param)

    # 3. Búsqueda con Q objects
    if search := request.GET.get('search'):
        objects = objects.filter(
            Q(field1__icontains=search) |
            Q(field2__icontains=search)
        )

    # 4. Ordenamiento
    objects = objects.order_by('-id')

    # 5. Render con contexto
    return render(request, 'template.html', {
        'objects': objects,
        'filter_options': ...,
    })
```

### Create/Edit Pattern

```python
@login_required
def module_create(request):
    if request.method == 'POST':
        # Validación
        if not all(required_fields):
            messages.error(request, 'Campos requeridos')
        else:
            try:
                # Creación
                obj = Model.objects.create(...)
                messages.success(request, 'Éxito')
                return redirect('module_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

    # GET request
    return render(request, 'form.html', {
        'related_data': ...,
        'is_edit': False,
    })
```

---

## Filtros y Búsqueda

### Filtros Implementados por Módulo

| Módulo | Filtros | Búsqueda |
|--------|---------|----------|
| Condominios | región | nombre, dirección |
| Usuarios | condominio, tipo | nombre, apellido, email |
| Reuniones | condominio, estado | tema, ubicación |
| Incidencias | condominio, estado, prioridad, categoría | título, descripción |
| Bitácora | incidencia | detalle, acción, título incidencia |
| Evidencias | incidencia, tipo_archivo | título incidencia, URL |
| Amonestaciones | condominio, usuario, tipo, motivo | descripción, nombre usuario |

---

## Tareas Pendientes / Mejoras Futuras

### Funcionalidades Adicionales
- [ ] Sistema de notificaciones (email/push)
- [ ] Reportes y estadísticas avanzadas
- [ ] Exportación de datos (PDF, Excel)
- [ ] Sistema de permisos granular por rol
- [ ] Upload real de archivos para evidencias (actualmente solo URLs)
- [ ] Galería de imágenes para evidencias
- [ ] Calendario interactivo para reuniones
- [ ] Sistema de votaciones para reuniones
- [ ] Chat entre residentes y administración
- [ ] App móvil (React Native / Flutter)

### Optimizaciones
- [ ] Paginación en listas largas
- [ ] Caché para consultas frecuentes
- [ ] API REST (Django REST Framework)
- [ ] Tests unitarios y de integración
- [ ] CI/CD pipeline
- [ ] Docker containerization

### UX/UI
- [ ] Modo oscuro
- [ ] Responsive mejorado para móviles
- [ ] Animaciones y transiciones
- [ ] Preview de archivos en evidencias
- [ ] Drag & drop para upload de archivos
- [ ] Filtros con AJAX (sin reload)

---

## Comandos Útiles

### Desarrollo
```bash
# Correr servidor de desarrollo
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar categorías iniciales
python manage.py cargar_categorias

# Collectstatic para producción
python manage.py collectstatic
```

### Base de Datos
```bash
# Shell de Django
python manage.py shell

# Acceso a PostgreSQL
python manage.py dbshell
```

---

## Notas Importantes

### Geolocalización
- Requiere HTTPS en producción (browsers modernos)
- Nominatim tiene rate limiting (1 request/segundo)
- Considerar agregar User-Agent personalizado
- Fallback si geolocalización falla

### Seguridad
- Variables de entorno para SECRET_KEY y DB credentials
- ALLOWED_HOSTS configurado en producción
- DEBUG = False en producción
- CSRF y CORS configurados apropiadamente

### Performance
- Usar select_related() y prefetch_related()
- Índices en campos de búsqueda frecuente
- Caché para datos estáticos
- CDN para archivos estáticos

---

## Historial de Decisiones Técnicas

### 1. JavaScript Externo vs Inline
**Decisión**: Siempre usar archivos JS externos
**Razón**: Mejor mantenibilidad, caching, reutilización
**Fecha**: Durante implementación de geolocalización

### 2. Management Commands vs Migraciones Manuales
**Decisión**: Usar management commands para datos iniciales
**Razón**: Más seguro, idempotente, no rompe migraciones
**Fecha**: Durante carga de categorías

### 3. Nominatim vs Google Maps API
**Decisión**: Nominatim/OpenStreetMap
**Razón**: Gratuito, sin API key, suficiente para el caso de uso
**Fecha**: Durante implementación de geocodificación inversa

### 4. Orden Descendente para Categorías
**Decisión**: `-id` en el queryset
**Razón**: Mostrar las más recientes primero, solicitado por usuario
**Fecha**: Durante implementación de categorías

---

## Contacto y Contribución

Este proyecto es parte de un sistema de gestión de condominios. Para contribuir o hacer preguntas, seguir las convenciones establecidas en este documento.

**Última actualización**: 2025-12-16
**Versión Django**: 5.2.8
**Estado**: Producción-ready (con mejoras pendientes)
