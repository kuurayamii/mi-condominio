# JavaScript

Carpeta para archivos JavaScript de la aplicación.

## Organización sugerida

```
js/
├── main.js           # Código JavaScript principal
├── utils.js          # Funciones auxiliares y utilidades
├── api.js            # Llamadas a APIs y AJAX
├── components/       # Scripts de componentes específicos
│   ├── modal.js
│   ├── datepicker.js
│   └── map.js
└── pages/            # Scripts específicos de páginas
    ├── incidencias.js
    ├── reuniones.js
    └── dashboard.js
```

## Ejemplo de uso

```django
{% load static %}
<script src="{% static 'mi_condominio/js/main.js' %}"></script>
<script src="{% static 'mi_condominio/js/components/modal.js' %}"></script>
```

## Buenas prácticas

- Usar `'use strict';` al inicio de cada archivo
- Evitar variables globales
- Comentar código complejo
- Usar nombres descriptivos para funciones y variables
