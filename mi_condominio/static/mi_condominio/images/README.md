# Images - Recursos Visuales

Carpeta para todas las imágenes y recursos visuales de la aplicación.

## Estructura

```
images/
├── icons/          # Iconos de la aplicación
│   ├── favicon.ico
│   ├── favicon-16x16.png
│   ├── favicon-32x32.png
│   └── ui-icons/   # Iconos de interfaz (edit, delete, etc.)
├── logos/          # Logos del proyecto
│   ├── logo.png
│   ├── logo.svg
│   └── logo-dark.png
└── backgrounds/    # Imágenes de fondo
    ├── hero.jpg
    └── pattern.png
```

## Formatos recomendados

- **Logos**: SVG (escalable) o PNG con fondo transparente
- **Iconos**: SVG o PNG (16x16, 24x24, 32x32)
- **Fotos**: JPG (comprimidas)
- **Ilustraciones**: SVG o PNG

## Optimización

Antes de subir imágenes:
1. Comprimir para reducir tamaño
2. Usar dimensiones apropiadas
3. Considerar usar WebP para mejor compresión

## Ejemplo de uso

```django
{% load static %}
<img src="{% static 'mi_condominio/images/logos/logo.png' %}" alt="Logo Mi Condominio">
<link rel="icon" href="{% static 'mi_condominio/images/icons/favicon.ico' %}">
```
