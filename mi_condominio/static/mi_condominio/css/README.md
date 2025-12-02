# CSS - Hojas de Estilo

Carpeta para archivos CSS de la aplicación.

## Organización sugerida

```
css/
├── base.css          # Estilos base y reset CSS
├── variables.css     # Variables CSS (colores, tamaños, etc.)
├── layout.css        # Layouts y estructura general
├── components/       # Estilos de componentes reutilizables
│   ├── buttons.css
│   ├── forms.css
│   └── cards.css
└── pages/            # Estilos específicos de páginas
    ├── dashboard.css
    ├── incidencias.css
    └── reuniones.css
```

## Ejemplo de uso

```django
{% load static %}
<link rel="stylesheet" href="{% static 'mi_condominio/css/base.css' %}">
<link rel="stylesheet" href="{% static 'mi_condominio/css/components/buttons.css' %}">
```
