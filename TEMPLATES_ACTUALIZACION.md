# Guía para Actualizar Templates con Django Forms

## ✅ Cambios Realizados en `condominios/form.html`

El template ha sido actualizado para usar Django Forms. Los cambios principales son:

### 1. **Errores Globales del Formulario** (líneas 32-44)
```django
{% if form.non_field_errors %}
    <div class="alert alert-danger alert-dismissible fade show" role="alert">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        <strong>Errores en el formulario:</strong>
        <ul class="mb-0 mt-2">
            {% for error in form.non_field_errors %}
                <li>{{ error }}</li>
            {% endfor %}
        </ul>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
{% endif %}
```

### 2. **Renderizado de Campos con Errores**

**ANTES** (campo manual):
```html
<input
    type="text"
    class="form-control"
    id="rut"
    name="rut"
    placeholder="12.345.678-9"
    value="{% if condominio %}{{ condominio.rut }}{% endif %}"
    required
    maxlength="10"
>
```

**DESPUÉS** (usando Django Form):
```django
<label for="{{ form.rut.id_for_label }}" class="form-label">
    RUT <span class="text-danger">*</span>
</label>
{{ form.rut }}
{% if form.rut.errors %}
    <div class="invalid-feedback d-block">
        {% for error in form.rut.errors %}
            {{ error }}
        {% endfor %}
    </div>
{% endif %}
<div class="form-text">
    Formato: XX.XXX.XXX-X
</div>
```

---

## 📋 Patrón Estándar para Actualizar Templates

### Estructura por Campo:

```django
<div class="col-md-6">  <!-- o col-12 según el diseño -->
    <!-- LABEL -->
    <label for="{{ form.NOMBRE_CAMPO.id_for_label }}" class="form-label">
        Texto del Label <span class="text-danger">*</span>  <!-- * solo si es required -->
    </label>

    <!-- CAMPO DEL FORM -->
    {{ form.NOMBRE_CAMPO }}

    <!-- ERRORES DEL CAMPO -->
    {% if form.NOMBRE_CAMPO.errors %}
        <div class="invalid-feedback d-block">
            {% for error in form.NOMBRE_CAMPO.errors %}
                {{ error }}
            {% endfor %}
        </div>
    {% endif %}

    <!-- TEXTO DE AYUDA (opcional) -->
    <div class="form-text">
        Texto de ayuda aquí
    </div>
</div>
```

---

## 🔧 Templates a Actualizar

### ✅ **Completados**:
1. **condominios/form.html** - Actualizado

### ⏳ **Pendientes**:

2. **reuniones/form.html**
   - Campos: `condominio`, `tipo_reunion`, `nombre_reunion`, `fecha_reunion`, `lugar_reunion`, `motivo_reunion`, `acta_reunion_url`

3. **categorias/form.html**
   - Campos: `nombre_categoria_incidencia`

4. **usuarios/form.html** ⚠️ (Caso especial)
   - Campos del form: `condominio`, `nombres`, `apellido`, `genero`, `rut`, `correo`, `residencia`, `tipo_usuario`, `estado_cuenta`
   - Campos adicionales (NO en form): `username`, `password` (manejados manualmente en template)

5. **incidencias/form.html**
   - Campos: `condominio`, `tipo_incidencia`, `titulo`, `descripcion`, `estado`, `prioridad`, `ubicacion_latitud_reporte`, `ubicacion_longitud_reporte`, `direccion_condominio_incidencia`, `usuario_reporta`, `fecha_cierre`

6. **bitacoras/form.html**
   - Campos: `incidencia`, `detalle`, `accion`

7. **evidencias/form.html**
   - Campos: `incidencia`, `url_archivo_evidencia`, `tipo_archivo_evidencia`

8. **amonestaciones/form.html**
   - Campos: `tipo_amonestacion`, `motivo`, `motivo_detalle`, `fecha_amonestacion`, `nombre_amonestado`, `apellidos_amonestado`, `rut_amonestado`, `numero_departamento`, `fecha_limite_pago`, `usuario_reporta`

---

## 🎯 Ejemplo Completo: usuarios/form.html

### Caso Especial: Campos `username` y `password`

Estos campos NO están en `UsuarioForm` porque pertenecen al modelo `User` de Django. Se manejan manualmente:

```django
<!-- Username (campo manual) -->
<div class="col-md-6">
    <label for="username" class="form-label">
        Nombre de Usuario <span class="text-danger">*</span>
    </label>
    <input
        type="text"
        class="form-control"
        id="username"
        name="username"
        placeholder="usuario123"
        {% if usuario and usuario.user %}value="{{ usuario.user.username }}"{% endif %}
        required
        maxlength="150"
    >
    <div class="form-text">
        Para iniciar sesión en el sistema
    </div>
</div>

<!-- Password (campo manual) -->
<div class="col-md-6">
    <label for="password" class="form-label">
        Contraseña {% if action == 'Editar' %}<small class="text-muted">(dejar vacío para no cambiar)</small>{% else %}<span class="text-danger">*</span>{% endif %}
    </label>
    <input
        type="password"
        class="form-control"
        id="password"
        name="password"
        placeholder="••••••••"
        {% if action == 'Crear' %}required{% endif %}
        minlength="8"
    >
</div>

<!-- Resto de campos usando form -->
{{ form.nombres }}
{{ form.apellido }}
<!-- etc -->
```

---

## 🚀 Beneficios de la Actualización

1. ✅ **Errores de validación visibles**: El usuario ve exactamente qué corregir
2. ✅ **Campos prepoblados automáticamente**: Django maneja valores en edición
3. ✅ **Widgets con clases CSS**: Ya incluyen `form-control`, placeholders, etc.
4. ✅ **Menos código**: No necesitas `value="{% if... %}"` manualmente
5. ✅ **Validación en backend**: No se puede bypasear desde el frontend

---

## 📝 Ejemplo Visual de Errores

Cuando un usuario ingresa un RUT inválido, verá:

```
┌─────────────────────────────────────────┐
│ RUT *                                   │
│ ┌─────────────────────────────────────┐ │
│ │ 123                                 │ │ ← Input con error
│ └─────────────────────────────────────┘ │
│ ⚠️ El RUT debe tener entre 7 y 9       │ ← Mensaje de error
│    caracteres (sin contar puntos...)    │
│ Formato: XX.XXX.XXX-X                   │ ← Help text
└─────────────────────────────────────────┘
```

---

## 🔍 Verificación Rápida

Para verificar que un template está correctamente actualizado:

1. ✅ Tiene `{% if form.non_field_errors %}` al inicio del form
2. ✅ Usa `{{ form.CAMPO }}` en lugar de `<input>`
3. ✅ Tiene `{% if form.CAMPO.errors %}` después de cada campo
4. ✅ Usa `{{ form.CAMPO.id_for_label }}` en el atributo `for` del label
5. ✅ La vista pasa `form` en el contexto (no solo el objeto)

---

## ⚡ Tip: Renderizado Automático Completo (Alternativa)

Si prefieres no mantener el HTML manualmente, puedes usar:

```django
<form method="post" novalidate>
    {% csrf_token %}

    <!-- Renderizado automático con Bootstrap -->
    {% for field in form %}
        <div class="mb-3">
            {{ field.label_tag }}
            {{ field }}
            {% if field.errors %}
                <div class="invalid-feedback d-block">
                    {{ field.errors }}
                </div>
            {% endif %}
            {% if field.help_text %}
                <div class="form-text">{{ field.help_text }}</div>
            {% endif %}
        </div>
    {% endfor %}

    <button type="submit" class="btn btn-primary">Guardar</button>
</form>
```

**Pros**: Menos código, actualización automática si cambias el form
**Contras**: Pierdes control sobre el layout (grid de Bootstrap, ordenamiento)

---

## 📌 Próximos Pasos

1. Actualizar los 7 templates restantes siguiendo el patrón de `condominios/form.html`
2. Probar cada formulario:
   - Enviar vacío (debe mostrar errores de campos requeridos)
   - Ingresar RUT inválido (debe mostrar error de formato)
   - Ingresar email/RUT duplicado (debe mostrar error de unicidad)
3. Verificar que los estilos Bootstrap se vean correctamente

