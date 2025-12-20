# Guía de Actualización de Vistas con Django Forms

## Estado Actual

### ✅ Completado:
1. **forms.py creado** con validaciones para todos los modelos
2. **Condominio** - create/edit actualizados
3. **Reunion** - create/edit actualizados
4. **Categoria** - create/edit actualizados

### ⏳ Pendiente de Actualizar:
5. **Usuario** - create/edit (requiere manejo especial de User de Django)
6. **Incidencia** - create/edit
7. **Bitacora** - create/edit
8. **Evidencia** - create/edit
9. **Amonestacion** - create/edit

---

## Patrón de Actualización

### Para vistas simples (sin lógica adicional):

**ANTES**:
```python
@login_required
def modelo_create(request):
    if request.method == 'POST':
        campo1 = request.POST.get('campo1')
        campo2 = request.POST.get('campo2')

        # Validaciones manuales
        if Modelo.objects.filter(campo1=campo1).exists():
            messages.error(request, 'Ya existe...')
        else:
            try:
                modelo = Modelo.objects.create(
                    campo1=campo1,
                    campo2=campo2
                )
                messages.success(request, f'{modelo} creado exitosamente.')
                return redirect('modelo_list')
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')

    return render(request, 'template.html', {...})
```

**DESPUÉS**:
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

**Para Edit**:
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

## Caso Especial: Usuario (con Django User)

**usuario_create**:
```python
@login_required
def usuario_create(request):
    if request.method == 'POST':
        form = UsuarioForm(request.POST)
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validar username único
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ya existe un usuario con este nombre de usuario.')
            form.add_error(None, 'El nombre de usuario ya está en uso.')
        elif form.is_valid():
            try:
                # Crear User de Django primero
                django_user = User.objects.create_user(
                    username=username,
                    email=form.cleaned_data['correo'],
                    password=password,
                    first_name=form.cleaned_data['nombres'],
                    last_name=form.cleaned_data['apellido']
                )

                # Crear usuario del sistema
                usuario = form.save(commit=False)
                usuario.user = django_user
                usuario.save()

                messages.success(request, f'Usuario "{usuario.nombres} {usuario.apellido}" creado exitosamente.')
                return redirect('usuario_list')
            except Exception as e:
                messages.error(request, f'Error al crear el usuario: {str(e)}')
                if 'django_user' in locals():
                    django_user.delete()  # Rollback si falla
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = UsuarioForm()

    return render(request, 'mi_condominio/usuarios/form.html', {
        'form': form,
        'action': 'Crear',
        'usuario': None,
    })
```

**usuario_edit**:
```python
@login_required
def usuario_edit(request, pk):
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioForm(request.POST, instance=usuario)
        password = request.POST.get('password')

        if form.is_valid():
            usuario = form.save()

            # Actualizar User de Django si existe
            if usuario.user:
                usuario.user.email = usuario.correo
                usuario.user.first_name = usuario.nombres
                usuario.user.last_name = usuario.apellido
                if password:  # Solo actualizar password si se proporcionó
                    usuario.user.set_password(password)
                usuario.user.save()

            messages.success(request, f'Usuario "{usuario.nombres} {usuario.apellido}" actualizado exitosamente.')
            return redirect('usuario_list')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = UsuarioForm(instance=usuario)

    return render(request, 'mi_condominio/usuarios/form.html', {
        'form': form,
        'action': 'Editar',
        'usuario': usuario,
    })
```

---

## Aplicar a los módulos restantes

### 1. Incidencia (líneas 582-698)
- Aplicar patrón estándar
- Form: `IncidenciaForm`

### 2. Bitacora (líneas 869-936)
- Aplicar patrón estándar
- Form: `BitacoraForm`

### 3. Evidencia (líneas 992-1064)
- Aplicar patrón estándar
- Form: `EvidenciaIncidenciaForm`

### 4. Amonestacion (líneas 1123-1227)
- Aplicar patrón estándar
- Form: `AmonestacionForm`

---

## Beneficios de los Formularios Django

1. ✅ **Validaciones automáticas**: RUT, emails, fechas
2. ✅ **Validaciones personalizadas**: Unicidad case-insensitive
3. ✅ **Mensajes de error claros**: Mostrados automáticamente en templates
4. ✅ **Widgets HTML mejorados**: Bootstrap classes, placeholders
5. ✅ **CSRF protection**: Incluido automáticamente
6. ✅ **Código más limpio**: 60% menos líneas en views.py
7. ✅ **Reutilizable**: Mismo form para create/edit

---

## Próximos Pasos

1. Actualizar las 4 vistas restantes (Usuario, Incidencia, Bitacora, Evidencia, Amonestacion)
2. Actualizar templates para mostrar errores de formulario (ver siguiente sección)
3. Probar cada formulario
4. Documentar en CLAUDE.md

