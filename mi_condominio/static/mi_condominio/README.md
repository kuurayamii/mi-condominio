# Archivos Estáticos de Mi Condominio

Esta carpeta contiene todos los archivos estáticos (CSS, JavaScript e imágenes) de la aplicación.

## Estructura

```
mi_condominio/static/mi_condominio/
├── css/           # Hojas de estilo CSS
├── js/            # Archivos JavaScript
└── images/        # Imágenes y recursos visuales
    ├── icons/     # Iconos (favicon, iconos de UI)
    ├── logos/     # Logos del proyecto
    └── backgrounds/ # Imágenes de fondo
```

## Uso en templates

Para usar estos archivos en tus templates Django:

```django
{% load static %}

<!-- CSS -->
<link rel="stylesheet" href="{% static 'mi_condominio/css/styles.css' %}">

<!-- JavaScript -->
<script src="{% static 'mi_condominio/js/main.js' %}"></script>

<!-- Imágenes -->
<img src="{% static 'mi_condominio/images/logos/logo.png' %}" alt="Logo">
```

## Producción

Para producción, ejecuta:
```bash
python manage.py collectstatic
```

Esto copiará todos los archivos estáticos a la carpeta `staticfiles/`.
