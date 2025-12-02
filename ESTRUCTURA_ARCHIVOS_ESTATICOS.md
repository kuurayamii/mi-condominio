# Estructura de Archivos Estáticos y Media

## Resumen

Este proyecto utiliza una estructura organizada para archivos estáticos y media siguiendo las mejores prácticas de Django.

## 📁 Estructura Completa

```
micondominio/
├── mi_condominio/
│   └── static/
│       └── mi_condominio/              # Archivos estáticos de la app
│           ├── css/                     # Hojas de estilo
│           │   ├── base.css            # ✅ Ejemplo creado
│           │   └── README.md
│           ├── js/                      # JavaScript
│           │   └── README.md
│           └── images/                  # Imágenes
│               ├── icons/               # Iconos (favicon, UI)
│               ├── logos/               # Logos del proyecto
│               ├── backgrounds/         # Fondos
│               └── README.md
│
├── media/                               # ⚠️ NO en Git
│   ├── evidencias/                      # Fotos/videos de incidencias
│   ├── actas/                           # PDFs de reuniones
│   ├── documentos/                      # Otros archivos
│   └── README.md
│
└── staticfiles/                         # ⚠️ Generado automáticamente
    └── (archivos recopilados)           # No editar manualmente
```

## 🎯 Uso en Templates

### Cargar archivos estáticos

```django
{% load static %}

<!DOCTYPE html>
<html>
<head>
    <!-- CSS -->
    <link rel="stylesheet" href="{% static 'mi_condominio/css/base.css' %}">

    <!-- Favicon -->
    <link rel="icon" href="{% static 'mi_condominio/images/icons/favicon.ico' %}">
</head>
<body>
    <!-- Logo -->
    <img src="{% static 'mi_condominio/images/logos/logo.png' %}" alt="Logo">

    <!-- JavaScript -->
    <script src="{% static 'mi_condominio/js/main.js' %}"></script>
</body>
</html>
```

### Usar archivos media (subidos por usuarios)

```django
<!-- En el modelo -->
class EvidenciaIncidencia(models.Model):
    archivo = models.FileField(upload_to='evidencias/')

<!-- En el template -->
{% if evidencia.archivo %}
    <img src="{{ evidencia.archivo.url }}" alt="Evidencia">
{% endif %}
```

## 📋 Comandos Útiles

### Desarrollo
```bash
# Django encuentra archivos automáticamente en mi_condominio/static/
python manage.py runserver
```

### Producción
```bash
# Recopilar todos los archivos estáticos
python manage.py collectstatic

# Los archivos se copian a staticfiles/
```

## 🔧 Configuración en settings.py

```python
# URL para acceder a archivos estáticos
STATIC_URL = 'static/'

# Carpeta donde collectstatic guarda archivos (producción)
STATIC_ROOT = BASE_DIR / 'staticfiles'

# URL para archivos subidos por usuarios
MEDIA_URL = 'media/'

# Carpeta donde se guardan archivos subidos
MEDIA_ROOT = BASE_DIR / 'media'
```

## 📝 Mejores Prácticas

### CSS
- ✅ Usar variables CSS para colores y tamaños
- ✅ Organizar por componentes y páginas
- ✅ Minificar en producción

### JavaScript
- ✅ Usar `'use strict';`
- ✅ Evitar variables globales
- ✅ Comentar código complejo
- ✅ Minificar en producción

### Imágenes
- ✅ Comprimir antes de subir
- ✅ Usar SVG para logos e iconos
- ✅ Usar nombres descriptivos
- ✅ Considerar WebP para mejor compresión

### Media
- ⚠️ NUNCA subir a Git
- ✅ Validar tipo y tamaño de archivos
- ✅ Usar nombres únicos (UUID)
- ✅ En producción, usar almacenamiento en la nube

## 🚀 Próximos Pasos

1. **Agregar CSS personalizado**
   - Crear estilos para dashboard
   - Estilos para formularios
   - Estilos responsive

2. **Agregar JavaScript**
   - Validación de formularios
   - Interactividad de UI
   - Llamadas AJAX

3. **Agregar imágenes**
   - Logo del proyecto
   - Favicon
   - Iconos de UI

4. **Configurar producción**
   - Configurar servidor web (Nginx/Apache)
   - Configurar almacenamiento en la nube para media
   - Activar compresión y caché
