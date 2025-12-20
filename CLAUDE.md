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
- **Package Manager**: uv (moderno gestor de paquetes Python)

### Frontend
- **Framework CSS**: Bootstrap 5.3.2
- **Iconos**: Bootstrap Icons
- **Gráficos**: Chart.js 4.4.0
- **JavaScript**: Vanilla JS (OOP)

### APIs Externas
- **Geolocalización**: Browser Geolocation API (nativo)
- **Geocodificación inversa**: Nominatim/OpenStreetMap (gratuito, sin API key)
- **Asistente IA**: OpenAI API (GPT-4o) con Function Calling

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

**IMPORTANTE**: Esta sección documenta EXACTAMENTE los campos de cada modelo en la base de datos. Cuando uses herramientas de IA o modifiques código relacionado con estos modelos, verifica que los campos coincidan con esta especificación.

### 1. **Condominio**
**Tabla**: `condominios`

**Campos**:
- `id` (AutoField, PK)
- `rut` (CharField, max_length=10, unique=True) - RUT del condominio
- `nombre` (CharField, max_length=140) - Nombre del condominio
- `direccion` (CharField, max_length=255) - Dirección completa
- `region` (CharField, max_length=50) - Región donde se ubica
- `comuna` (CharField, max_length=50) - Comuna del condominio
- `mail_contacto` (EmailField, max_length=255) - Correo de contacto
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Nota**: Este modelo NO tiene campo `telefono`.

---

### 2. **Usuario**
**Tabla**: `usuarios`

**Campos**:
- `id` (AutoField, PK)
- `user` (OneToOneField to User, nullable) - Usuario Django para autenticación
- `condominio` (ForeignKey to Condominio) - Condominio asociado
- `nombres` (CharField, max_length=200) - Nombres del usuario
- `apellido` (CharField, max_length=200) - Apellidos del usuario
- `genero` (CharField, max_length=1, nullable, choices: M/F/O/N) - Género
- `rut` (CharField, max_length=10, unique=True) - RUT del usuario
- `correo` (EmailField, max_length=200, unique=True) - Correo electrónico
- `residencia` (TextField, nullable) - Dirección de residencia
- `tipo_usuario` (CharField, max_length=10, choices: ADMIN/SUPERVISOR/CONSERJE) - Rol
- `estado_cuenta` (CharField, max_length=10, choices: ACTIVO/INACTIVO, default=ACTIVO)
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Nota**: Este modelo NO tiene campo `telefono` ni `email` (usa `correo`).

---

### 3. **Reunion**
**Tabla**: `reuniones`

**Campos**:
- `id` (AutoField, PK)
- `condominio` (ForeignKey to Condominio) - Condominio asociado
- `tipo_reunion` (CharField, max_length=15, choices: ORDINARIA/EXTRAORDINARIA/INFORMATIVA)
- `nombre_reunion` (CharField, max_length=20) - Nombre de la reunión
- `fecha_reunion` (DateField) - Fecha programada
- `lugar_reunion` (CharField, max_length=60, nullable) - Lugar de realización
- `motivo_reunion` (TextField, nullable) - Motivo o temática
- `acta_reunion_url` (URLField, max_length=500, nullable) - URL del acta
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

---

### 4. **CategoriaIncidencia**
**Tabla**: `categoria_incidencias`

**Campos**:
- `id` (AutoField, PK)
- `nombre_categoria_incidencia` (CharField, max_length=30, unique=True) - Nombre de la categoría

**Nota**: 20 categorías precargadas vía management command `cargar_categorias`.

---

### 5. **Incidencia**
**Tabla**: `incidencias`

**Campos**:
- `id` (AutoField, PK)
- `condominio` (ForeignKey to Condominio) - Condominio asociado
- `tipo_incidencia` (ForeignKey to CategoriaIncidencia) - Categoría de la incidencia
- `titulo` (CharField, max_length=160) - Título de la incidencia
- `descripcion` (TextField, nullable) - Descripción detallada
- `estado` (CharField, max_length=15, choices: PENDIENTE/EN_PROCESO/RESUELTA/CERRADA/CANCELADA, default=PENDIENTE)
- `ubicacion_latitud_reporte` (CharField, max_length=50, nullable) - Latitud del reporte
- `ubicacion_longitud_reporte` (CharField, max_length=50, nullable) - Longitud del reporte
- `direccion_condominio_incidencia` (CharField, max_length=180, nullable) - Dirección asociada
- `usuario_reporta` (ForeignKey to Usuario) - Usuario que reporta
- `fecha_reporte` (DateField, auto_now_add=True) - Fecha del reporte
- `fecha_cierre` (DateField, nullable) - Fecha de cierre
- `prioridad` (CharField, max_length=10, choices: BAJA/MEDIA/ALTA/URGENTE, default=MEDIA)
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Características especiales**:
- Geolocalización automática con JavaScript (GeolocationManager)
- Geocodificación inversa con Nominatim

---

### 6. **Bitacora**
**Tabla**: `bitacoras`

**Campos**:
- `id` (AutoField, PK)
- `incidencia` (ForeignKey to Incidencia) - Incidencia asociada
- `detalle` (TextField, nullable) - Detalle del registro
- `accion` (TextField, nullable) - Acción ejecutada
- `fecha_bitacora` (DateField, auto_now_add=True) - Fecha del registro
- `created_at` (DateTimeField, auto_now_add=True)

**Propósito**: Registro de seguimiento de acciones sobre incidencias.

---

### 7. **EvidenciaIncidencia**
**Tabla**: `evidencias_incidencia`

**Campos**:
- `id` (AutoField, PK)
- `incidencia` (ForeignKey to Incidencia) - Incidencia asociada
- `url_archivo_evidencia` (URLField, max_length=500) - URL del archivo
- `tipo_archivo_evidencia` (CharField, max_length=15, choices: IMAGEN/VIDEO/DOCUMENTO/AUDIO/OTRO)
- `created_at` (DateTimeField, auto_now_add=True)

**Nota**: Actualmente solo almacena URLs. Upload real de archivos pendiente.

---

### 8. **Amonestacion**
**Tabla**: `amonestaciones`

**Campos**:
- `id` (AutoField, PK)
- `tipo_amonestacion` (CharField, max_length=15, choices: VERBAL/ESCRITA/MULTA/SUSPENSION)
- `motivo` (CharField, max_length=40, choices: 12 motivos predefinidos + OTRO)
- `motivo_detalle` (CharField, max_length=200, nullable) - Detalle adicional del motivo
- `fecha_amonestacion` (DateField) - Fecha aplicada
- `nombre_amonestado` (CharField, max_length=150) - Nombre del sancionado
- `apellidos_amonestado` (CharField, max_length=150) - Apellidos del sancionado
- `rut_amonestado` (CharField, max_length=10) - RUT del sancionado
- `numero_departamento` (CharField, max_length=60, nullable) - Número de departamento
- `fecha_limite_pago` (DateField, nullable) - Fecha límite de pago (solo para MULTA)
- `usuario_reporta` (ForeignKey to Usuario) - Usuario que reporta
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

**Motivos predefinidos**:
1. RUIDOS_MOLESTOS
2. USO_INDEBIDO_ESTACIONAMIENTOS
3. DANO_BIEN_COMUN
4. MAL_USO_AREA_COMUN
5. INCUMPLIMIENTO_NORMAS_SANITARIAS
6. TENENCIA_IRRESPONSABLE
7. MAL_USO_DUCTOS_BASURA
8. ARRIENDO_ILEGAL
9. INCUMPLIMIENTO_OBRAS_REMODELACIONES
10. IMPEDIMENTO_LABORES_ADMINISTRATIVAS
11. SEGURIDAD
12. OTRO

---

### 9. **ChatSession** (Asistente IA)
**Tabla**: `chat_sessions`

**Campos**:
- `id` (AutoField, PK)
- `usuario` (ForeignKey to Usuario) - Usuario dueño de la sesión
- `titulo` (CharField, max_length=255, nullable) - Título opcional
- `activa` (BooleanField, default=True) - Sesión activa
- `created_at` (DateTimeField, auto_now_add=True)
- `updated_at` (DateTimeField, auto_now=True)

---

### 10. **ChatMessage** (Asistente IA)
**Tabla**: `chat_messages`

**Campos**:
- `id` (AutoField, PK)
- `sesion` (ForeignKey to ChatSession) - Sesión asociada
- `role` (CharField, max_length=10, choices: user/assistant/system)
- `contenido` (TextField) - Contenido del mensaje
- `tokens_usados` (IntegerField, nullable) - Tokens consumidos
- `tool_calls` (JSONField, nullable) - Llamadas a herramientas MCP
- `created_at` (DateTimeField, auto_now_add=True)

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

## Asistente de IA con OpenAI

### Descripción

El sistema incluye un asistente de IA conversacional integrado que utiliza la API de OpenAI (GPT-4o) con capacidades de Function Calling (similar a MCP - Model Context Protocol). El asistente puede consultar y analizar datos de la base de datos para proporcionar insights, recomendaciones y análisis.

### Arquitectura del Asistente

**Componentes principales**:
1. **Models** (`ChatSession`, `ChatMessage`): Almacenan conversaciones y mensajes
2. **AI Tools** (`ai_tools.py`): Herramientas MCP para interactuar con la BD
3. **AI Assistant** (`ai_assistant.py`): Servicio que gestiona la comunicación con OpenAI
4. **Views** (`views.py`): API endpoints para el chat
5. **Frontend** (`ai_chat.js`, `ai_chat.css`): Interfaz de chat moderna

### Capacidades del Asistente

El asistente tiene acceso a 7 herramientas MCP:

| Herramienta | Descripción | Parámetros |
|-------------|-------------|------------|
| `get_incidencias_abiertas` | Obtiene incidencias abiertas o en proceso | `condominio_id` (opcional) |
| `get_estadisticas_dashboard` | Estadísticas generales del sistema | `condominio_id` (opcional) |
| `get_amonestaciones_recientes` | Amonestaciones de los últimos N días | `dias`, `condominio_id` |
| `buscar_incidencias` | Búsqueda por título o descripción | `termino_busqueda`, `condominio_id` |
| `analizar_tendencias_incidencias` | Análisis de tendencias y patrones | `dias`, `condominio_id` |
| `crear_bitacora_incidencia` | Crea registro de seguimiento | `incidencia_id`, `accion`, `detalle` |
| `recomendar_solucion_incidencia` | Sugiere soluciones basadas en historial | `incidencia_id` |

### Flujo de Funcionamiento

```
1. Usuario escribe mensaje en la interfaz de chat
   ↓
2. Frontend envía request POST a /ai-chat/send/
   ↓
3. Backend (ai_assistant.py):
   - Obtiene o crea sesión de chat
   - Construye historial de mensajes
   - Llama a OpenAI con tools disponibles
   ↓
4. OpenAI decide si usar herramientas:
   - SI: Ejecuta función(es) de ai_tools.py
   - NO: Responde directamente
   ↓
5. Si hubo tool calls:
   - Resultados se agregan al contexto
   - Segunda llamada a OpenAI para respuesta final
   ↓
6. Respuesta se guarda en BD y se envía al frontend
   ↓
7. Frontend renderiza respuesta con Markdown
```

### Ejemplos de Uso

**Consultas simples**:
- "¿Cuántas incidencias abiertas hay?"
- "Muéstrame las estadísticas del dashboard"
- "¿Qué amonestaciones hay este mes?"

**Análisis avanzado**:
- "¿Cuáles son las categorías de incidencias más comunes?"
- "Analiza las tendencias de los últimos 90 días"
- "¿Hay algún patrón en las incidencias de mantenimiento?"

**Recomendaciones**:
- "¿Cómo puedo resolver la incidencia #15?"
- "Dame recomendaciones basadas en casos similares"

**Operaciones**:
- "Agrega una entrada a la bitácora de la incidencia #10 diciendo que se contactó al proveedor"

### Configuración

**Variables de entorno requeridas** (`.env`):
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

**Archivo de configuración**: `config/settings.py`
```python
import os
from dotenv import load_dotenv
load_dotenv()
```

### Archivos del Sistema

| Archivo | Propósito |
|---------|-----------|
| `mi_condominio/models.py` | Modelos `ChatSession` y `ChatMessage` |
| `mi_condominio/ai_tools.py` | Herramientas MCP (7 funciones) |
| `mi_condominio/ai_assistant.py` | Servicio principal del asistente |
| `mi_condominio/views.py` | Vistas y API endpoints |
| `mi_condominio/urls.py` | Rutas del chat |
| `static/mi_condominio/css/ai_chat.css` | Estilos del chat |
| `static/mi_condominio/js/ai_chat.js` | Lógica del frontend (clase `AIChatManager`) |
| `templates/mi_condominio/ai_chat/chat.html` | Template principal |

### Características de la Interfaz

- **Chat en tiempo real** con typing indicators
- **Renderizado de Markdown** con Marked.js
- **Preguntas sugeridas** al iniciar
- **Historial persistente** por sesión
- **Badges de herramientas** que muestran cuándo el asistente consultó la BD
- **Responsive** y diseño moderno
- **Auto-scroll** al recibir mensajes
- **Textarea expandible** (Shift+Enter para nueva línea)

### Modelo Utilizado

- **Modelo**: `gpt-4o` (puede cambiarse a `gpt-3.5-turbo` para menor costo)
- **Context window**: Últimos 20 mensajes de la sesión
- **System prompt**: Instrucciones específicas para actuar como asistente de condominios

### Costos Estimados (OpenAI)

**GPT-4o** (recomendado):
- Input: ~$2.50 / 1M tokens
- Output: ~$10.00 / 1M tokens
- Estimado por consulta: $0.01 - $0.05

**GPT-3.5-Turbo** (más económico):
- Input: ~$0.50 / 1M tokens
- Output: ~$1.50 / 1M tokens
- Estimado por consulta: $0.001 - $0.01

### Seguridad

- **Login requerido**: `@login_required` en todas las vistas
- **CSRF protection**: Tokens en requests POST
- **Validación de usuario**: Solo usuarios registrados en el sistema
- **Historial privado**: Cada usuario solo ve sus propias conversaciones
- **API key protegida**: Nunca expuesta al frontend

### Mejoras Futuras

- [ ] Streaming de respuestas (SSE) para respuestas en tiempo real
- [ ] Soporte para imágenes (GPT-4 Vision)
- [ ] Export de conversaciones a PDF
- [ ] Comandos de voz (Speech-to-Text)
- [ ] Respuestas de voz (Text-to-Speech)
- [ ] Analytics de uso del asistente
- [ ] Fine-tuning del modelo con datos históricos
- [ ] Integración con webhooks para notificaciones proactivas

---

## Sistema de Validaciones con Django Forms

**IMPORTANTE**: El proyecto utiliza Django Forms con validaciones robustas para garantizar la integridad de los datos.

### Archivo Principal: `forms.py`

**Ubicación**: `mi_condominio/forms.py`
**Líneas**: ~600 líneas
**Formularios**: 8 formularios (uno por cada modelo principal)

### Validadores Personalizados

#### 1. **validate_rut_chileno**
- **Formato aceptado**: `XX.XXX.XXX-X` o `XXXXXXXX-X`
- **Validaciones**:
  - Largo entre 7-9 caracteres (sin puntos/guión)
  - Solo números + opcionalmente K/k al final
  - Formato regex: `^\d{7,8}[0-9Kk]$`

#### 2. **validate_email_unique_case_insensitive**
- Valida unicidad de emails ignorando mayúsculas/minúsculas
- Excluye el registro actual en edición

#### 3. **validate_fecha_no_pasada**
- Previene fechas en el pasado

#### 4. **validate_fecha_no_muy_futura**
- Limita fechas a máximo N años en el futuro (default: 5 años)

---

### Formularios Implementados

#### 1. **CondominioForm**
**Validaciones**:
- RUT único y formato chileno válido
- Nombre mínimo 3 caracteres
- Email válido
- Selector de región con 16 regiones de Chile
- Bootstrap classes en widgets

**Campos**:
- `rut`, `nombre`, `direccion`, `region`, `comuna`, `mail_contacto`

---

#### 2. **UsuarioForm**
**Validaciones**:
- RUT único y formato válido
- Correo único (case-insensitive)
- Nombres mínimo 2 caracteres
- Apellidos mínimo 2 caracteres

**Campos**:
- `condominio`, `nombres`, `apellido`, `genero`, `rut`, `correo`, `residencia`, `tipo_usuario`, `estado_cuenta`

**Nota**: Este formulario NO incluye campos de `username` y `password` (manejados separadamente en la vista por integración con Django User).

---

#### 3. **ReunionForm**
**Validaciones**:
- Fecha no más de 6 meses en el pasado
- Fecha no más de 2 años en el futuro
- Nombre mínimo 3 caracteres

**Campos**:
- `condominio`, `tipo_reunion`, `nombre_reunion`, `fecha_reunion`, `lugar_reunion`, `motivo_reunion`, `acta_reunion_url`

---

#### 4. **IncidenciaForm**
**Validaciones**:
- Título mínimo 5 caracteres
- Fecha cierre obligatoria si estado es CERRADA
- Fecha cierre no puede ser futura
- Auto-asigna fecha de cierre si estado es CERRADA/CANCELADA

**Campos**:
- `condominio`, `tipo_incidencia`, `titulo`, `descripcion`, `estado`, `prioridad`, `ubicacion_latitud_reporte`, `ubicacion_longitud_reporte`, `direccion_condominio_incidencia`, `usuario_reporta`, `fecha_cierre`

**Características especiales**:
- Campos de geolocalización readonly (populados por JavaScript)

---

#### 5. **CategoriaIncidenciaForm**
**Validaciones**:
- Nombre único (case-insensitive)
- Mínimo 3 caracteres

**Campos**:
- `nombre_categoria_incidencia`

---

#### 6. **BitacoraForm**
**Validaciones**:
- Al menos `detalle` o `accion` debe estar presente

**Campos**:
- `incidencia`, `detalle`, `accion`

---

#### 7. **EvidenciaIncidenciaForm**
**Validaciones**:
- URL válida (validación Django)
- Nota: Validación de extensión de archivo comentada (no bloquea, solo sugiere)

**Campos**:
- `incidencia`, `url_archivo_evidencia`, `tipo_archivo_evidencia`

---

#### 8. **AmonestacionForm**
**Validaciones**:
- RUT formato válido
- Fecha amonestación no más de 1 año atrás
- Fecha amonestación no futura
- Fecha límite obligatoria solo para MULTAS
- Fecha límite posterior a fecha amonestación
- Motivo detalle obligatorio si motivo es "OTRO"
- No permite fecha límite si tipo NO es MULTA
- Nombre mínimo 2 caracteres
- Apellidos mínimo 2 caracteres

**Campos**:
- `tipo_amonestacion`, `motivo`, `motivo_detalle`, `fecha_amonestacion`, `nombre_amonestado`, `apellidos_amonestado`, `rut_amonestado`, `numero_departamento`, `fecha_limite_pago`, `usuario_reporta`

---

### Uso en Views

**Patrón estándar para CREATE**:
```python
@login_required
def modelo_create(request):
    if request.method == 'POST':
        form = ModeloForm(request.POST)
        if form.is_valid():
            modelo = form.save()
            messages.success(request, f'{modelo} creado exitosamente.')
            return redirect('modelo_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ModeloForm()

    return render(request, 'template.html', {
        'form': form,
        'action': 'Crear',
        'modelo': None,
    })
```

**Patrón estándar para EDIT**:
```python
@login_required
def modelo_edit(request, pk):
    modelo = get_object_or_404(Modelo, pk=pk)

    if request.method == 'POST':
        form = ModeloForm(request.POST, instance=modelo)
        if form.is_valid():
            modelo = form.save()
            messages.success(request, f'{modelo} actualizado exitosamente.')
            return redirect('modelo_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = ModeloForm(instance=modelo)

    return render(request, 'template.html', {
        'form': form,
        'action': 'Editar',
        'modelo': modelo,
    })
```

---

### Estado de Implementación en Views

| Módulo | Estado | Observaciones |
|--------|--------|---------------|
| Condominio | ✅ Completado | views.py y templates actualizados |
| Reunion | ✅ Completado | views.py y templates actualizados |
| Categoria | ✅ Completado | views.py y templates actualizados |
| Usuario | ✅ Completado | views.py y templates actualizados con manejo especial de Django User |
| Incidencia | ✅ Completado | views.py y templates actualizados con soporte de geolocalización |
| Bitacora | ✅ Completado | views.py y templates actualizados |
| Evidencia | ✅ Completado | views.py y templates actualizados |
| Amonestacion | ✅ Completado | views.py y templates actualizados con lógica condicional |

**Estado**: ✅ **100% COMPLETADO** - Todos los módulos implementan Django Forms con validaciones robustas.

### Estado de Implementación en Templates

| Módulo | Create/Edit Template | Delete Template | Observaciones |
|--------|---------------------|-----------------|---------------|
| Condominio | ✅ `condominios/form.html` | ✅ | Errores globales + por campo |
| Reunion | ✅ `reuniones/form.html` | ✅ | Errores globales + por campo |
| Categoria | ✅ `categorias/form.html` | ✅ | Errores globales + por campo |
| Usuario | ✅ `usuarios/form.html` | ✅ | Errores globales + por campo |
| Incidencia | ✅ `incidencias/form.html` | ✅ | Errores + geolocation.js integrado |
| Bitacora | ✅ `bitacoras/form.html` | ✅ | Errores globales + por campo |
| Evidencia | ✅ `evidencias/form.html` | ✅ | Errores globales + por campo |
| Amonestacion | ✅ `amonestaciones/form.html` | ✅ | Errores + JavaScript condicional |

**Patrón de Templates**:
- Todos los templates usan `{{ form.field }}` para renderizar campos
- Todos incluyen bloque de errores globales (`form.non_field_errors`)
- Todos incluyen errores por campo (`form.field.errors`)
- Todos usan `novalidate` en el formulario para validación personalizada
- Todos usan labels con `{{ form.field.id_for_label }}`
- Todos mantienen compatibilidad con JavaScript existente (geolocalización, campos condicionales)

---

### Beneficios del Sistema de Validaciones

1. ✅ **Seguridad**: Previene inyección SQL, XSS, datos inválidos
2. ✅ **Integridad**: Garantiza unicidad (RUT, emails), formatos correctos
3. ✅ **UX mejorada**: Mensajes de error claros y específicos
4. ✅ **Menos código**: 60% reducción en views.py
5. ✅ **Reutilización**: Mismo form para create/edit
6. ✅ **Testeable**: Fácil escribir tests para validaciones
7. ✅ **Mantenible**: Validaciones centralizadas en forms.py

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

### Gestión de Dependencias (uv)
```bash
# Instalar dependencias del proyecto
uv sync

# Agregar nueva dependencia
uv add nombre-paquete

# Agregar dependencia de desarrollo
uv add --dev nombre-paquete

# Remover dependencia
uv remove nombre-paquete

# Actualizar dependencias
uv lock --upgrade
```

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

**Última actualización**: 2025-12-19
**Versión Django**: 5.2.8
**Estado**: Producción-ready con validaciones completas (con mejoras pendientes)

**Hitos recientes**:
- ✅ Implementación completa de Django Forms en todos los módulos (8/8)
- ✅ Validaciones robustas que no pueden ser bypasseadas desde el frontend
- ✅ Reducción de ~60% en código de views.py
- ✅ Experiencia de usuario mejorada con mensajes de error claros
